
from flask import Blueprint,render_template,redirect,url_for,flash , request , abort
from flask_login import login_required,current_user
from sqlalchemy import func
from models.user_model import Users,ParkingLot,ParkingSpot,Reservation,db
from datetime import datetime , timedelta 
from zoneinfo import ZoneInfo

admin_blueprint=Blueprint('admin',__name__,url_prefix='/dashboard')

@admin_blueprint.route('/admin')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorised"
    else :
        lots= ParkingLot.query.filter_by(is_active=True).all()
        return render_template('admin_dashboard.html',Parking_lots=lots)

 # adding a new parking lot

@admin_blueprint.route('/addlot' , methods=['GET','POST'])
@login_required
def add_lot():
    if request.method=='POST':
        name = request.form['parking_name']
        price = request.form['price']
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = request.form['max_spots']

        new_lot= ParkingLot(parking_name=name,price=price,address=address,pin_code=pin_code,max_spots=max_spots ) #type: ignore
        db.session.add(new_lot)
        db.session.commit()

        # Now create spots
        for i in range(1, int(max_spots) + 1):
            new_spot = ParkingSpot( lot_id=new_lot.id,spot_number=str(i),status='A',) #type: ignore
            db.session.add(new_spot)    
        db.session.commit()
        flash(f'A new Lot is Added with {max_spots} new spots', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('add_lot.html')


@admin_blueprint.route('admin/profile/view')
@login_required
def admin_profile_view():
    if current_user.role != 'admin':
        abort(404)
    
    return render_template('admin_profile_view.html',user=current_user)


@admin_blueprint.route('admin/profile/edit', methods=['GET','POST'])
@login_required
def admin_profile_edit():
    if current_user.role != 'admin':
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
            return redirect(url_for('admin.view_profile'))
    return render_template('admin_profile_edit.html',user=user)




# Edit parking lot
@admin_blueprint.route('/editlot/<int:lot_id>' , methods=['GET','POST'])
@login_required
def edit_lot(lot_id):
    lot=ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)
    if request.method=='POST':
        lot.parking_name = request.form['parking_name']
        lot.price = request.form['price']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        new_max_spots =int(request.form['max_spots'])
        current_spots_count = len(lot.spots)

        # If increasing spots
        if new_max_spots > current_spots_count:
            for i in range(current_spots_count + 1, new_max_spots + 1):
                new_spot = ParkingSpot(
                    lot_id=lot.id, #type: ignore
                    spot_number=str(i),#type: ignore
                    status='A'#type: ignore
                )
                db.session.add(new_spot)
        elif new_max_spots < current_spots_count:
            all_spots = list(reversed(lot.spots))
            spots_to_remove_count = current_spots_count - new_max_spots
            extra_spots = all_spots[:spots_to_remove_count]

            for spot in extra_spots:
                if spot.status == 'A':
                    db.session.delete(spot)
                else:
                    flash("Cannot reduce max spots: some of the last spots are occupied.", "danger")
                    return redirect(url_for('admin.dashboard'))
            
        lot.max_spots = new_max_spots

        
        db.session.commit()
        flash('Lot edited Successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('edit_lot.html' , lot=lot)


# deleting parking lots
@admin_blueprint.route('/deletelot/<int:lot_id>')
def delete_lot(lot_id):
    lot=ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)
    for spot in lot.spots:
        for reservation in spot.reservations:
            if reservation.status == 'active':
                flash("Cannot delete: One or more spots are currently booked.", "danger")
                return redirect(url_for("admin.dashboard"))

    # No active bookings — delete the lot
    lot.is_active = False
    db.session.commit()
    flash('Parking lot is deleted','danger')
    return redirect(url_for('admin.dashboard'))

#can view each spot
@admin_blueprint.route('/spot/<int:spot_id>')
def view_spot(spot_id):
    spot = ParkingSpot.query.filter_by(id=spot_id).first()
    if spot is None:
        abort(404)
    if spot.status=='O':
        if spot.reservations:
            reservation = spot.reservations[0]
        else:
            reservation = None

        if request.method == 'GET' and reservation != None:
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            booking_time = reservation.booking_timestamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
            duration = (now - booking_time).total_seconds() / 3600

            duration = max(1, int(duration))
            estimated_cost = duration * reservation.cost_per_unit_time
        else:
            estimated_cost = None
        return render_template('occspot.html',spot=spot,reservation=reservation,estimated_cost=estimated_cost)
    
    return render_template('view_spot.html', spot=spot)

#can delete a spot
@admin_blueprint.route('/deletespot/<int:spot_id>')
def delete_spot(spot_id):
    spot=ParkingSpot.query.filter_by(id=spot_id).first()
    if spot is None:
        abort(404)
    lot=spot.lot
    if spot.status != 'A':
        flash('Cannot Delete an occupied spot','failure')
        return redirect(url_for('admin.view_spot',spot_id=spot_id))
    db.session.delete(spot)
    lot.max_spots -= 1
    db.session.commit()
    flash('The spot is deleted Successfully','success')
    return redirect(url_for('admin.dashboard'))


#admin user Section
@admin_blueprint.route('/users')
@login_required
def view_users():
    if current_user.role != 'admin':
        abort(404)
    users=Users.query.filter(Users.role != 'admin').all()
    return render_template('admin_users.html',users=users)



@admin_blueprint.route('/user-history/<int:user_id>')
@login_required
def user_booking_history(user_id):
    if current_user.role != 'admin':
        abort(403)

    user = Users.query.get_or_404(user_id)
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

    return render_template(
        'admin_user_history.html',
        user=user,
        history=history,
        total_amount_paid=total_amount_paid,
        total_duration_hours=total_duration_hours,
        total_bookings=total_bookings,
        first_booking=first_booking,
        latest_booking=latest_booking
    )



@admin_blueprint.route('/summary')
@login_required
def admin_summary():
    # first chart for avaialabe to occupany ratio 
    total_spots=ParkingSpot.query.count()
    occupied_spots=ParkingSpot.query.filter(ParkingSpot.status!='A').count()
    available_spots=total_spots-occupied_spots

    #second chart for weekly trend 
    today = datetime.utcnow().date()
    one_year_ago = today - timedelta(days=365)

    monthly_data = db.session.query(
                                    func.strftime('%Y-%m', Reservation.booking_timestamp),  # Year-Month format
                                    func.count(Reservation.id)
                                ).filter(
                                    Reservation.booking_timestamp >= one_year_ago
                                ).group_by(
                                    func.strftime('%Y-%m', Reservation.booking_timestamp)
                                ).order_by(
                                    func.strftime('%Y-%m', Reservation.booking_timestamp)
                                ).all()

    months = []
    bookings_per_month = []

    for month_str, count in monthly_data:
        # convert "YYYY-MM" → "MonthName YYYY"
        month_dt = datetime.strptime(month_str, "%Y-%m")
        month_label = month_dt.strftime("%b %Y")  # Example: Jan 2025
        months.append(month_label)
        bookings_per_month.append(count)


    #third chart 
    # Get number of new users registered per month (past 12 months)
    today = datetime.today()
    one_year_ago = today.replace(year=today.year - 1)
    
    registration_stats = (
    db.session.query(
        func.strftime('%Y-%m', Users.member_since).label('month'),
        func.count(Users.id).label('Users_count')
    )
    .filter(Users.member_since >= one_year_ago)
    .group_by(func.strftime('%Y-%m', Users.member_since))
    .order_by(func.strftime('%Y-%m', Users.member_since))
    .all()
    )

    # Prepare data for chart
    labels = [row.month for row in registration_stats]
    data = [row.Users_count for row in registration_stats]

    #chart 4
    top_lots = (
        db.session.query(
            ParkingLot.parking_name,
            func.count(Reservation.id).label('usage_count')
        )
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)
        .group_by(ParkingLot.id)
        .order_by(func.count(Reservation.id).desc())
        .limit(10)  # Top 10 lots
        .all()
    )

    # Prepare data for chart
    labels1 = [row.parking_name for row in top_lots]
    data1 = [row.usage_count for row in top_lots]

    #chart 5 
    avg_parking_time = (
        db.session.query(
            ParkingLot.parking_name,
            func.avg(func.julianday(Reservation.releasing_timestamp) - func.julianday(Reservation.booking_timestamp)).label('avg_duration_days')
        )
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)
        .filter(Reservation.releasing_timestamp.isnot(None))  # Only completed reservations
        .group_by(ParkingLot.id)
        .order_by(func.avg(func.julianday(Reservation.releasing_timestamp) - func.julianday(Reservation.booking_timestamp)).desc())
        .limit(10)  # Top 10 lots by usage
        .all()
    )

    labels2 = [row.parking_name for row in avg_parking_time]
    data2 = [round(row.avg_duration_days * 24, 2) for row in avg_parking_time]

    return render_template('admin_summary.html',total_spots=total_spots,occupied_spots=occupied_spots,available_spots=available_spots,
                           months=months,
                           bookings_per_month=bookings_per_month,
                           labels=labels, data=data,
                           labels1=labels1, data1=data1,
                           labels2=labels2, data2=data2)


@admin_blueprint.route('admin/summary', methods=['GET','POST'])
@login_required
def admin_search():
    results=[]
    query=''
    search_type=''

    if request.method=='POST':
        search_type = request.form.get('search_type')   
        query = (request.form.get('query') or '').strip().lower()

        if search_type=='user':
            results= Users.query.filter(
                (Users.username.ilike(f"%{query}%")) |
                (Users.full_name.ilike(f"%{query}%")) |
                (Users.email.ilike(f"%{query}%"))
            ).all()
        elif search_type =='lot_name':
            results = ParkingLot.query.filter(
                ParkingLot.parking_name.ilike(f"%{query}%")
            ).all()
        
        elif search_type =='lot_number':
            results = ParkingLot.query.filter(
                ParkingLot.pin_code.ilike(f"%{query}%")
            ).all()

    return render_template('admin_search.html',results=results,search_type=search_type,query=query)
    
