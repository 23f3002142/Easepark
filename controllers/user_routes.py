
from flask import Blueprint,render_template,flash,request,url_for,abort,redirect,jsonify,make_response
from flask_login import login_required,current_user
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from models.user_model import Users,ParkingLot,ParkingSpot,Reservation,db
from datetime import datetime , timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo
from sqlalchemy import or_,and_
from flask_mail import Message
from extensions import mail,limiter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import smtplib
import io
import os
import random

user_blueprint=Blueprint('user',__name__,url_prefix='/dashboard')

@user_blueprint.route('/user')
@login_required
@limiter.limit("10 per 1 minute")
def dashboard():

    if current_user.role != 'user':
        return "Unauthorised"
    else:
        # Get all active reservations of the user
        active_reservations = Reservation.query.filter_by(user_id=current_user.id, status='active').all()

        active_bookings = []
        for res in active_reservations:
            lot = ParkingLot.query.get(res.spot.lot_id)
            if lot is None:
                abort(404)

            local_time = res.booking_timestamp.astimezone(ZoneInfo("Asia/Kolkata"))
            booking_date = local_time.strftime('%d %b %Y')
            time_range = local_time.strftime('%I:%M %p') + " - Now"

            active_bookings.append({
                "lot_name": lot.parking_name,
                "spot_number": res.spot.spot_number,
                "date": booking_date,
                "time_range": time_range
            })

        # This block should NOT be inside the for loop
        user_pin = current_user.pin_code

        # Get all lots matching user's pin code
        lots = ParkingLot.query.filter_by(pin_code=user_pin,is_active=True).all()

        available_lots = []
        for lot in lots:
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            free_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()

            available_lots.append({
                'name': lot.parking_name,
                'free_spots': free_spots,
                'total_spots': total_spots
            })

        user=current_user
        if current_user.role != 'user':
            abort(403)

        user = Users.query.get_or_404(user.id)
        history = Reservation.query.filter_by(user_id=user.id).order_by(
            Reservation.booking_timestamp.desc()
        ).all()
        for res in history:
            res.booking_timestamp_ist = res.booking_timestamp.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))

        # Prepare booking counts by date
        booking_counts = defaultdict(int)
        for res in history:
            if res.booking_timestamp_ist:
                date_str = res.booking_timestamp_ist.strftime('%d %b')
                booking_counts[date_str] += 1

        # Sort by date
        sorted_dates = sorted(booking_counts.items(), key=lambda x: datetime.strptime(x[0], '%d %b'))
        chart_labels = [d[0] for d in sorted_dates]
        chart_data = [d[1] for d in sorted_dates]

        notifications = [
            "🚗 New parking lots added recently — check nearby lots now!",
            "📄 View your booking history and release spots when done.",
            "🕒 Charges are calculated hourly — remember to release your spot in time!",
        ]


        return render_template(
            'user_dashboard.html.jinja',
            user=current_user,
            active_bookings=active_bookings,
            available_lots=available_lots,
            notifications=notifications,
            chart_labels=chart_labels,
            chart_data=chart_data
        )
    
@user_blueprint.route('/profile/view')
@login_required
@limiter.limit("10 per 1 minute")
def user_profile_view():
    if current_user.role != 'user':
        abort(404)
    
    return render_template('user_profile_view.html',user=current_user)


@user_blueprint.route('/profile/edit', methods=['GET','POST'])
@login_required
@limiter.limit("10 per 1 minute")
def user_profile_edit():
    if current_user.role != 'user':
        abort(404)
    user=current_user

    if request.method == 'POST':
        if request.method == 'POST':
            user.full_name = request.form['full_name']
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            user.address = request.form['address']
            user.pin_code = request.form['pin_code']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.user_profile_view'))
    return render_template('user_profile_edit.html',user=user)

@user_blueprint.route("/choose_booking")
@login_required
@limiter.limit("10 per 1 minute")
def choose_booking():
    return render_template("choose_booking.html")

@user_blueprint.route("/api/lots")
def get_lots():
    lots=ParkingLot.query.filter_by(is_active=True).all()
    lots_data=[]
    for lot in lots:
        lots_data.append({
            "id": lot.id,
            "name": lot.parking_name,
            "address": lot.address,
            "price": lot.price,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "max_spots": lot.max_spots
        })
    return jsonify(lots_data)

@user_blueprint.route("/book_map")
def book_map():
    return render_template("book_map.html")

@user_blueprint.route('/book', methods=['GET','POST'])
@login_required
@limiter.limit("10 per 1 minute")
def book_spot():
    search_query= request.args.get('search','')
    lots=[]

    if search_query:
        lots = ParkingLot.query.filter(
            and_(
                ParkingLot.is_active == True,#type: ignore
                or_(
                    ParkingLot.parking_name.ilike(f'%{search_query}%'),
                    ParkingLot.address.ilike(f'%{search_query}%'),
                    ParkingLot.pin_code.ilike(f'%{search_query}%')
                )
            )
        ).all()
    

    return render_template('book_spot.html', lots=lots,search_query=search_query)

def generate_otp():
    return str(random.randint(100000, 999999)) 

def send_otp_email(email, otp):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = "EasePark OTP Verification"
    sender = {"email": os.getenv("MAIL_DEFAULT_SENDER")}
    to = [{"email": email}]
    text_content = f"Your OTP for EasePark booking action is: {otp}. Do not share it."

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, 
        sender=sender, 
        subject=subject, 
        text_content=text_content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"DEBUG: OTP for {email} sent successfully via Brevo API: {otp}")
    except ApiException as e:
        print("Brevo API Exception:", e)

@user_blueprint.route('/book/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per 3 minute")
def reserve_spot(lot_id):
    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.spot_number.asc()).first()

    if not spot:
        return redirect(url_for('user.book_spot'))

    if request.method == 'GET':
        # Check for an existing pending reservation
        reservation = (
            Reservation.query.join(ParkingSpot)
            .filter(
                Reservation.user_id == current_user.id,
                ParkingSpot.lot_id == lot_id,
                Reservation.status == "pending"
            )
            .order_by(Reservation.id.desc())
            .first()
        )


        if reservation:
            # Generate new OTP for resend
            otp = generate_otp()
            reservation.otp_secret = otp
            db.session.commit()
            send_otp_email(current_user.email, otp)
            flash("A new OTP has been sent to your email.", "info")
            return render_template('verify_otp.html', lot=lot, spot=reservation.spot)

        return render_template('reserve_spot.html', lot=lot, spot=spot, user=current_user)

    if request.method == 'POST':
        otp_entered = request.form.get("otp")
        vehicle_number = request.form.get("vehicle_number")

        reservation = Reservation.query.filter_by(
            user_id=current_user.id, spot_id=spot.id, status="pending"
        ).order_by(Reservation.id.desc()).first()

        if reservation and otp_entered:
            if reservation.otp_secret == otp_entered:
                # ✅ OTP verified → confirm booking
                reservation.status = "active"
                reservation.otp_verified = True
                spot.status = 'O'  # Occupied
                current_user.total_bookings += 1
                db.session.commit()
                flash(f"Spot number {spot.spot_number} reserved successfully!", "success")
                return redirect(url_for('user.dashboard'))
            else:
                flash("Invalid OTP, please try again.", "danger")
                return render_template('verify_otp.html', lot=lot, spot=spot)

        else:
            # 🚨 Check if this vehicle number is already in an active reservation
            active_reservation = Reservation.query.filter_by(
                vehicle_number=vehicle_number,
                status="active"
            ).first()

            if active_reservation:
                flash("This vehicle already has an active reservation. Please use another vehicle.", "danger")
                return redirect(url_for('user.choose_booking'))

            # First time booking request → generate OTP
            otp = generate_otp()
            current_time = datetime.now(ZoneInfo("Asia/Kolkata"))

            reservation = Reservation(
                spot_id=spot.id,  # type: ignore
                user_id=current_user.id,  # type: ignore
                vehicle_number=vehicle_number,  # type: ignore
                cost_per_unit_time=lot.price,  # type: ignore
                booking_timestamp=current_time,  # type: ignore
                status="pending",   # type: ignore
                otp_required=True,  # type: ignore
                otp_verified=False,  # type: ignore
                otp_secret=otp  # type: ignore
            )

            db.session.add(reservation)
            db.session.commit()

            send_otp_email(current_user.email, otp)
            flash("OTP sent to your registered email. Please verify.", "info")
            return render_template('verify_otp.html', lot=lot, spot=spot)

    return render_template('reserve_spot.html', lot=lot, spot=spot, user=current_user)



@user_blueprint.route('/history')
@login_required
@limiter.limit("10 per 1 minute")
def booking_history():
    history = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.booking_timestamp.desc()).all()
    user=current_user
    for res in history:
        res.booking_timestamp_ist = res.booking_timestamp.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
        if res.releasing_timestamp:
            res.releasing_timestamp_ist = res.releasing_timestamp.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
        else:
            res.releasing_timestamp_ist = None
    return render_template('booking_history.html', history=history , user=user)



def generate_receipt_pdf(reservation, lot, spot):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#2C3E50"))
    c.drawCentredString(300, 750, "EasePark Parking Receipt")

    # Line below header
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, 740, 550, 740)

    # Body
    c.setFont("Helvetica", 12)
    y = 700
    line_gap = 20

    details = [
        ("User", reservation.user.full_name or reservation.user.username),
        ("Parking Lot", lot.parking_name),
        ("Spot Number", spot.spot_number),
        ("Vehicle Number", reservation.vehicle_number),
        ("Booking Time", str(reservation.booking_timestamp)),
        ("Release Time", str(reservation.releasing_timestamp or 'N/A')),
        ("Total Cost", f"₹{reservation.total_cost or 0}"),
    ]

    for label, value in details:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(200, y, str(value))
        y -= line_gap

    # Footer
    c.setFillColor(colors.HexColor("#16A085"))
    c.setFont("Helvetica-BoldOblique", 14)
    c.drawCentredString(300, y - 40, "Thank you for using EasePark!")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


def send_receipt_email(user, reservation, lot, spot):
    pdf_buffer = generate_receipt_pdf(reservation, lot, spot)

    # Configure Brevo API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "EasePark Booking Receipt"
    sender = {"email": os.getenv("MAIL_DEFAULT_SENDER")}
    to = [{"email": user.email}]

    text_content = f"""
Hello {user.username},

Here is your receipt for your recent booking with EasePark:

Lot: {lot.parking_name}
Spot: {spot.spot_number}
Total Cost: ₹{reservation.total_cost}

Thank you for choosing EasePark!
"""

    # Attach PDF (Brevo requires base64 encoding)
    import base64
    pdf_content = base64.b64encode(pdf_buffer.read()).decode('utf-8')

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        text_content=text_content,
        attachment=[{
            "content": pdf_content,
            "name": f"receipt_{reservation.id}.pdf"
        }]
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"DEBUG: Receipt email sent to {user.email}")
    except ApiException as e:
        print("Brevo API Exception:", e)



@user_blueprint.route('/release/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per 3 minute")
def release_spot(reservation_id):
    reservation = Reservation.query.filter(
        Reservation.id == reservation_id,
        Reservation.user_id == current_user.id,
        or_(
            Reservation.status == 'active',
            Reservation.status == 'pending_release'
        )
    ).first()

    if reservation is None:
        abort(404)

    spot = ParkingSpot.query.filter_by(id=reservation.spot_id).first()
    if spot is None:
        abort(404)

    lot = ParkingLot.query.filter_by(id=spot.lot_id).first()
    if lot is None:
        abort(404)

    IST = ZoneInfo("Asia/Kolkata")

    if request.method == 'GET':
        now = datetime.now(IST)

        # convert from UTC → IST
        booking_time = reservation.booking_timestamp.astimezone(IST)

        duration = (now - booking_time).total_seconds() / 3600
        duration = max(1, int(duration))  # at least 1 hour
        estimated_cost = duration * reservation.cost_per_unit_time
    else:
        estimated_cost = None

    if request.method == 'POST':
        otp_entered = request.form.get("otp")

        if otp_entered:  # OTP verification step
            if reservation.otp_secret == otp_entered:
                release_time = datetime.now(IST)
                booking_time = reservation.booking_timestamp.astimezone(IST)

                duration = (release_time - booking_time).total_seconds() / 3600
                duration = max(1, int(duration))

                total_cost = duration * reservation.cost_per_unit_time

                # Save in UTC (DB-friendly)
                reservation.releasing_timestamp = datetime.utcnow()
                reservation.total_cost = total_cost
                reservation.status = 'completed'
                reservation.otp_verified = True

                spot.status = 'A'
                db.session.commit()

                try:
                    # ✅ Use Brevo API instead of SMTP
                    send_receipt_email(current_user, reservation, lot, spot)
                    flash("Spot released successfully. Receipt has been emailed to you.", "success")
                except Exception as e:
                    # Catch unexpected API errors so Render doesn’t timeout
                    print("Error sending receipt email:", e)
                    flash("Spot released successfully, but receipt email failed to send.", "warning")

                return redirect(url_for('user.dashboard'))
            else:
                flash("Invalid OTP, please try again.", "danger")
                return render_template("verify_otp.html", lot=lot, spot=spot)

        # Step 1: Generate and send OTP for release
        otp = str(random.randint(100000, 999999))
        reservation.otp_secret = otp
        reservation.otp_required = True
        reservation.status = "pending_release"
        db.session.commit()

        send_otp_email(current_user.email, otp)
        flash("OTP sent to your registered email. Please verify to release.", "info")
        return render_template("verify_otp.html", lot=lot, spot=spot)

    return render_template(
        'release_spot.html',
        reservation=reservation,
        spot=spot,
        lot=lot,
        datetime=datetime,
        timedelta=timedelta,
        estimated_cost=estimated_cost
    )


@user_blueprint.route("/receipt/<int:reservation_id>")
@login_required
@limiter.limit("10 per 1 minute")
def download_receipt(reservation_id):
    reservation = Reservation.query.filter_by(
        id=reservation_id, user_id=current_user.id
    ).first()

    if not reservation:
        abort(404)

    spot = ParkingSpot.query.get(reservation.spot_id)
    if spot is None:
        abort(404)

    lot = spot.lot

    # Generate PDF in memory
    pdf_buffer = io.BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "EasePark Parking Receipt")

    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"User: {current_user.full_name or current_user.username}")
    p.drawString(50, 680, f"Parking Lot: {lot.parking_name}")
    p.drawString(50, 660, f"Spot Number: {spot.spot_number}")
    p.drawString(50, 640, f"Vehicle Number: {reservation.vehicle_number}")
    p.drawString(50, 620, f"Booking Time: {reservation.booking_timestamp}")
    p.drawString(50, 600, f"Release Time: {reservation.releasing_timestamp or 'N/A'}")
    p.drawString(50, 580, f"Total Cost: ₹{reservation.total_cost or 0}")

    p.showPage()
    p.save()
    pdf_buffer.seek(0)

    # Return response as downloadable PDF
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{reservation.id}.pdf'

    return response




@user_blueprint.route('/user-summary')
@login_required
@limiter.limit("10 per 1 minute")
def user_summary():
    user = current_user
    if current_user.role != 'user':
        abort(403)

    user = Users.query.get_or_404(user.id)
    history = Reservation.query.filter_by(user_id=user.id).order_by(
        Reservation.booking_timestamp.desc()
    ).all()

    # Convert timestamps to IST for each reservation
    for res in history:
        if res.booking_timestamp:
            res.booking_timestamp_ist = res.booking_timestamp.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
        else:
            res.booking_timestamp_ist = None

        if res.releasing_timestamp:
            res.releasing_timestamp_ist = res.releasing_timestamp.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
        else:
            res.releasing_timestamp_ist = None

    # Summary calculations
    total_amount_paid = sum(res.total_cost or 0 for res in history)

    # Total duration parked (sum of all completed bookings)
    total_duration_hours = 0
    for res in history:
        if res.booking_timestamp_ist and res.releasing_timestamp_ist:
            duration = (res.releasing_timestamp_ist - res.booking_timestamp_ist).total_seconds() / 3600
            total_duration_hours += duration
    total_duration_hours = round(total_duration_hours, 2)

    total_bookings = len(history)
    first_booking = history[-1].booking_timestamp_ist if history else None
    latest_booking = history[0].booking_timestamp_ist if history else None

    # Prepare booking counts by date
    booking_counts = defaultdict(int)
    for res in history:
        if res.booking_timestamp_ist:
            date_str = res.booking_timestamp_ist.strftime('%d %b')
            booking_counts[date_str] += 1

    # Sort by date
    sorted_dates = sorted(booking_counts.items(), key=lambda x: datetime.strptime(x[0], '%d %b'))
    chart_labels = [d[0] for d in sorted_dates]
    chart_data = [d[1] for d in sorted_dates]

    # Duration buckets
    duration_buckets = {
        '<3 hrs': 0,
        '3–6 hrs': 0,
        '6–9 hrs': 0,
        '9–12 hrs': 0,
        '12+ hrs': 0,
        '1 day+': 0,
        '>2 days': 0
    }

    for res in history:
        if res.booking_timestamp_ist and res.releasing_timestamp_ist:
            duration = res.releasing_timestamp_ist - res.booking_timestamp_ist
            duration_hours = duration.total_seconds() / 3600

            if duration_hours < 3:
                duration_buckets['<3 hrs'] += 1
            elif duration_hours <= 6:
                duration_buckets['3–6 hrs'] += 1
            elif duration_hours <= 9:
                duration_buckets['6–9 hrs'] += 1
            elif duration_hours <= 12:
                duration_buckets['9–12 hrs'] += 1
            elif duration_hours <= 24:
                duration_buckets['12+ hrs'] += 1
            elif duration_hours <= 48:
                duration_buckets['1 day+'] += 1
            else:
                duration_buckets['>2 days'] += 1

    # Chart 3: booking durations vs cost
    booking_labels = []
    duration_values = []
    cost_values = []

    for idx, res in enumerate(history):
        if res.booking_timestamp_ist and res.releasing_timestamp_ist and res.total_cost:
            duration = res.releasing_timestamp_ist - res.booking_timestamp_ist
            hours = duration.total_seconds() / 3600
            booking_labels.append(f"Booking {idx + 1}")
            duration_values.append(round(hours, 2))
            cost_values.append(res.total_cost)

    return render_template(
        'user_summary.html.jinja',
        user=user,
        history=history,
        total_amount_paid=total_amount_paid,
        total_duration_hours=total_duration_hours,
        total_bookings=total_bookings,
        first_booking=first_booking,
        latest_booking=latest_booking,
        chart_labels=chart_labels,
        chart_data=chart_data,
        chart_duration_labels=list(duration_buckets.keys()),
        chart_duration_data=list(duration_buckets.values()),
        chart_booking_labels=booking_labels,
        chart_duration_data_each=duration_values,
        chart_cost_data_each=cost_values
    )



