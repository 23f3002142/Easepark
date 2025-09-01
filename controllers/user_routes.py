
from flask import Blueprint,render_template,flash,request,url_for,abort,redirect,jsonify,make_response
from flask_login import login_required,current_user
from models.user_model import Users,ParkingLot,ParkingSpot,Reservation,db
from datetime import datetime , timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo
from sqlalchemy import or_,and_
from flask_mail import Message
from extensions import mail
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

import random

user_blueprint=Blueprint('user',__name__,url_prefix='/dashboard')

@user_blueprint.route('/user')
@login_required
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

        # Summary calculations
        total_amount_paid = sum(res.total_cost or 0 for res in history)
        # Total duration parked (sum of all completed bookings)
        total_duration_hours = 0
        for res in history:
            if res.booking_timestamp and res.releasing_timestamp:
                duration = (res.releasing_timestamp - res.booking_timestamp).total_seconds() / 3600
                total_duration_hours += duration
        
        total_duration_hours = round(total_duration_hours, 2)

        total_bookings = len(history)
        first_booking = history[-1].booking_timestamp if history else None
        latest_booking = history[0].booking_timestamp if history else None

        # Prepare booking counts by date
        booking_counts = defaultdict(int)
        for res in history:
            if res.booking_timestamp:
                date_str = res.booking_timestamp.strftime('%d %b')
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
def user_profile_view():
    if current_user.role != 'user':
        abort(404)
    
    return render_template('user_profile_view.html',user=current_user)


@user_blueprint.route('/profile/edit', methods=['GET','POST'])
@login_required
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
def choose_booking():
    return render_template("choose_booking.html")


@user_blueprint.route('/book', methods=['GET','POST'])
@login_required
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
    msg = Message("EasePark OTP Verification", 
                  sender="kshitij.3001@gmail.com", 
                  recipients=[email])
    msg.body = f"Your OTP for EasePark booking action is: {otp}. Do not share it."
    mail.send(msg)


@user_blueprint.route('/book/<int:lot_id>', methods=['Get', 'POST'])
@login_required
def reserve_spot(lot_id):
    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)

    spot = ParkingSpot.query.filter_by(lot_id=lot_id , status = 'A').first()

    if not spot:
        return redirect(url_for('user.book_spot'))
    
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
            # First time booking request → generate OTP
            otp = generate_otp()
            current_time = datetime.now(ZoneInfo("Asia/Kolkata"))

            reservation = Reservation(
                spot_id=spot.id, #type:ignore
                user_id=current_user.id,#type:ignore
                vehicle_number=vehicle_number,#type:ignore
                cost_per_unit_time=lot.price,#type:ignore
                booking_timestamp=current_time,#type:ignore
                status="pending",   #type:ignore
                otp_required=True,#type:ignore
                otp_verified=False,#type:ignore
                otp_secret=otp#type:ignore
            )

            db.session.add(reservation)
            db.session.commit()

            send_otp_email(current_user.email, otp)
            flash("OTP sent to your registered email. Please verify.", "info")
            return render_template('verify_otp.html', lot=lot, spot=spot)
    return render_template('reserve_spot.html', lot=lot,spot=spot,user=current_user)


@user_blueprint.route('/history')
@login_required
def booking_history():
    history = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.booking_timestamp.desc()).all()
    user=current_user
    

    return render_template('booking_history.html', history=history , user=user)



def generate_receipt_pdf(reservation, lot, spot):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "EasePark Parking Receipt")

    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"User: {current_user.full_name or current_user.username}")
    c.drawString(50, 680, f"Parking Lot: {lot.parking_name}")
    c.drawString(50, 660, f"Spot Number: {spot.spot_number}")
    c.drawString(50, 640, f"Vehicle Number: {reservation.vehicle_number}")
    c.drawString(50, 620, f"Booking Time: {reservation.booking_timestamp}")
    c.drawString(50, 600, f"Release Time: {reservation.releasing_timestamp or 'N/A'}")
    c.drawString(50, 580, f"Total Cost: ₹{reservation.total_cost or 0}")

    c.drawString(50, 540, "Thank you for using EasePark!")
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def send_receipt_email(user, reservation, lot, spot):
    pdf_buffer = generate_receipt_pdf(reservation, lot, spot)

    msg = Message(
        subject="EasePark Booking Receipt",
        sender="your_email@gmail.com",
        recipients=[user.email]
    )
    msg.body = f"""
Hello {user.username},

Here is your receipt for your recent booking with EasePark:

Lot: {lot.parking_name}
Spot: {spot.spot_number}
Total Cost: ₹{reservation.total_cost}

Thank you for choosing EasePark!
"""

    # attached PDF
    msg.attach(
        f"receipt_{reservation.id}.pdf",
        "application/pdf",
        pdf_buffer.read()
    )

    mail.send(msg)



@user_blueprint.route('/release/<int:reservation_id>' , methods=['GET','POST'])
@login_required
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
    
    spot=ParkingSpot.query.filter_by(id=reservation.spot_id).first()
    if spot is None:
        abort(404)
    lot=ParkingLot.query.filter_by(id=spot.lot_id).first()
    
    if lot is None:
        abort(404)

    if request.method == 'GET':
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        booking_time = reservation.booking_timestamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        duration = (now - booking_time).total_seconds() / 3600

        duration = max(1, int(duration))
        estimated_cost = duration * reservation.cost_per_unit_time
    else:
        estimated_cost = None

    if request.method == 'POST':
        otp_entered = request.form.get("otp")

        if otp_entered:  # OTP verification step
            if reservation.otp_secret == otp_entered:
                release_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                booking_time = reservation.booking_timestamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                duration = (release_time - booking_time).total_seconds() / 3600
                duration = max(1, int(duration))

                total_cost = duration * reservation.cost_per_unit_time

                reservation.releasing_timestamp = release_time
                reservation.total_cost = total_cost
                reservation.status = 'completed'
                reservation.otp_verified = True

                spot.status = 'A'
                db.session.commit()

                # after db.session.commit()
                send_receipt_email(current_user, reservation, lot, spot)
                flash("Spot released successfully. Receipt has been emailed to you.", "success")
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
    return render_template('release_spot.html', reservation=reservation, spot=spot, lot=lot,datetime=datetime,timedelta=timedelta,estimated_cost=estimated_cost)




@user_blueprint.route("/receipt/<int:reservation_id>")
@login_required
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
def user_summary():
    user=current_user
    if current_user.role != 'user':
        abort(403)

    user = Users.query.get_or_404(user.id)
    history = Reservation.query.filter_by(user_id=user.id).order_by(
        Reservation.booking_timestamp.desc()
    ).all()

     # Summary calculations
    total_amount_paid = sum(res.total_cost or 0 for res in history)
    



    # for chart-1 
    # Total duration parked (sum of all completed bookings)
    total_duration_hours = 0
    for res in history:
        if res.booking_timestamp and res.releasing_timestamp:
            duration = (res.releasing_timestamp - res.booking_timestamp).total_seconds() / 3600
            total_duration_hours += duration
    
    total_duration_hours = round(total_duration_hours, 2)

    total_bookings = len(history)
    first_booking = history[-1].booking_timestamp if history else None
    latest_booking = history[0].booking_timestamp if history else None

    # Prepare booking counts by date
    booking_counts = defaultdict(int)
    for res in history:
        if res.booking_timestamp:
            date_str = res.booking_timestamp.strftime('%d %b')
            booking_counts[date_str] += 1

    # Sort by date
    sorted_dates = sorted(booking_counts.items(), key=lambda x: datetime.strptime(x[0], '%d %b'))
    chart_labels = [d[0] for d in sorted_dates]
    chart_data = [d[1] for d in sorted_dates]

    #for chart 2

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
        if res.booking_timestamp and res.releasing_timestamp:
            duration = res.releasing_timestamp - res.booking_timestamp
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



    #CHart 3
    booking_labels = []
    duration_values = []
    cost_values = []

    for idx, res in enumerate(history):
        if res.booking_timestamp and res.releasing_timestamp and res.total_cost:
            duration = res.releasing_timestamp - res.booking_timestamp
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
    chart_duration_labels = list(duration_buckets.keys()),
    chart_duration_data = list(duration_buckets.values()),
    chart_booking_labels=booking_labels,
    chart_duration_data_each=duration_values,
    chart_cost_data_each=cost_values
)

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
