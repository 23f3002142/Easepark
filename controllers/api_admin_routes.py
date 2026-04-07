from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import joinedload
from models.user_model import Users, ParkingLot, ParkingSpot, Reservation, db
from cache import cached, invalidate_cache
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

api_admin_blueprint = Blueprint('api_admin', __name__, url_prefix='/api/admin')

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


def get_admin_user():
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
    if not user or user.role != 'admin':
        return None
    return user


def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "address": user.address,
        "pin_code": user.pin_code,
        "member_since": user.member_since.isoformat() if user.member_since else None,
        "total_bookings": user.total_bookings,
    }


# ─── Dashboard ───
@api_admin_blueprint.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    # Single query: lots + spot counts via subquery
    spot_counts = (
        db.session.query(
            ParkingSpot.lot_id,
            func.count(ParkingSpot.id).label('total'),
            func.count(ParkingSpot.id).filter(ParkingSpot.status == 'O').label('occupied')
        )
        .group_by(ParkingSpot.lot_id)
        .subquery()
    )

    lots = (
        db.session.query(ParkingLot, spot_counts.c.total, spot_counts.c.occupied)
        .outerjoin(spot_counts, ParkingLot.id == spot_counts.c.lot_id)
        .filter(ParkingLot.is_active == True)
        .order_by(ParkingLot.id.asc())
        .all()
    )

    # Also fetch all spots grouped by lot for the dashboard visualization
    all_spots = (
        ParkingSpot.query
        .filter(ParkingSpot.lot_id.in_([lot.id for lot, _, _ in lots]))
        .order_by(ParkingSpot.lot_id, ParkingSpot.spot_number.asc())
        .all()
    )
    spots_by_lot = {}
    for s in all_spots:
        spots_by_lot.setdefault(s.lot_id, []).append({
            "id": s.id,
            "spot_number": s.spot_number,
            "status": s.status,
        })

    lots_data = []
    for lot, total, occupied in lots:
        total = total or 0
        occupied = occupied or 0
        lot_spots = spots_by_lot.get(lot.id, [])
        # Sort: available first, then occupied
        lot_spots.sort(key=lambda x: (0 if x['status'] == 'A' else 1, x['spot_number']))
        lots_data.append({
            "id": lot.id,
            "parking_name": lot.parking_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "max_spots": lot.max_spots,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "total_spots": total,
            "occupied_spots": occupied,
            "available_spots": total - occupied,
            "spots": lot_spots,
        })

    return jsonify({"lots": lots_data}), 200


# ─── Profile ───
@api_admin_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def profile_view():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"user": serialize_user(admin)}), 200


@api_admin_blueprint.route('/profile', methods=['PUT'])
@jwt_required()
def profile_edit():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    admin.full_name = data.get('full_name', admin.full_name)
    admin.username = data.get('username', admin.username)
    admin.email = data.get('email', admin.email)
    admin.phone_number = data.get('phone_number', admin.phone_number)
    admin.address = data.get('address', admin.address)
    admin.pin_code = data.get('pin_code', admin.pin_code)

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated", "user": serialize_user(admin)}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500


# ─── Add Lot ───
@api_admin_blueprint.route('/lots', methods=['POST'])
@jwt_required()
def add_lot():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get('parking_name', '').strip()
    price = data.get('price')
    address = data.get('address', '').strip()
    pin_code = data.get('pin_code', '').strip()
    max_spots = data.get('max_spots')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([name, price, address, pin_code, max_spots]):
        return jsonify({"error": "parking_name, price, address, pin_code, and max_spots are required"}), 400

    lat_val = float(latitude) if latitude else None
    long_val = float(longitude) if longitude else None

    new_lot = ParkingLot(
        parking_name=name, price=float(price), address=address,
        pin_code=pin_code, max_spots=int(max_spots),
        latitude=lat_val, longitude=long_val
    )  # type: ignore
    db.session.add(new_lot)
    db.session.commit()

    for i in range(1, int(max_spots) + 1):
        db.session.add(ParkingSpot(lot_id=new_lot.id, spot_number=str(i), status='A'))  # type: ignore
    db.session.commit()

    return jsonify({"message": f"Lot '{name}' added with {max_spots} spots", "lot_id": new_lot.id}), 201


# ─── Edit Lot ───
@api_admin_blueprint.route('/lots/<int:lot_id>', methods=['PUT'])
@jwt_required()
def edit_lot(lot_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        return jsonify({"error": "Lot not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    lot.parking_name = data.get('parking_name', lot.parking_name)
    lot.price = float(data.get('price', lot.price))
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.latitude = data.get('latitude', lot.latitude)
    lot.longitude = data.get('longitude', lot.longitude)

    new_max_spots = int(data.get('max_spots', lot.max_spots))
    current_spots_count = lot.spots.count()

    if new_max_spots > current_spots_count:
        for i in range(current_spots_count + 1, new_max_spots + 1):
            db.session.add(ParkingSpot(lot_id=lot.id, spot_number=str(i), status='A'))  # type: ignore
    elif new_max_spots < current_spots_count:
        all_spots = list(lot.spots.order_by(ParkingSpot.id.desc()).limit(current_spots_count - new_max_spots))
        for spot in all_spots:
            if spot.status == 'A':
                db.session.delete(spot)
            else:
                return jsonify({"error": "Cannot reduce: some trailing spots are occupied"}), 409

    lot.max_spots = new_max_spots
    db.session.commit()

    return jsonify({"message": "Lot updated successfully"}), 200


# ─── Get single lot (for edit form) ───
@api_admin_blueprint.route('/lots/<int:lot_id>', methods=['GET'])
@jwt_required()
def get_lot(lot_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        return jsonify({"error": "Lot not found"}), 404

    spots = []
    for s in lot.spots.order_by(ParkingSpot.spot_number.asc()).all():
        spots.append({
            "id": s.id,
            "spot_number": s.spot_number,
            "status": s.status,
            "is_active": s.is_active,
        })

    return jsonify({
        "lot": {
            "id": lot.id,
            "parking_name": lot.parking_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "max_spots": lot.max_spots,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "is_active": lot.is_active,
            "spots": spots,
        }
    }), 200


# ─── Delete Lot (soft delete) ───
@api_admin_blueprint.route('/lots/<int:lot_id>', methods=['DELETE'])
@jwt_required()
def delete_lot(lot_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        return jsonify({"error": "Lot not found"}), 404

    # Check for active reservations in a single query
    active_count = (
        Reservation.query
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
        .filter(ParkingSpot.lot_id == lot_id, Reservation.status == 'active')
        .count()
    )
    if active_count > 0:
        return jsonify({"error": "Cannot delete: one or more spots are currently booked"}), 409

    lot.is_active = False
    db.session.commit()
    return jsonify({"message": "Parking lot deleted"}), 200


# ─── View Spot ───
@api_admin_blueprint.route('/spots/<int:spot_id>', methods=['GET'])
@jwt_required()
def view_spot(spot_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    spot = ParkingSpot.query.filter_by(id=spot_id).first()
    if spot is None:
        return jsonify({"error": "Spot not found"}), 404

    result = {
        "id": spot.id,
        "spot_number": spot.spot_number,
        "status": spot.status,
        "is_active": spot.is_active,
        "lot_id": spot.lot_id,
        "lot_name": spot.lot.parking_name,
    }

    if spot.status == 'O':
        reservation = (
            Reservation.query.filter(
                Reservation.spot_id == spot.id,
                Reservation.status == 'active'
            ).order_by(Reservation.booking_timestamp.desc()).first()
        )

        if reservation:
            booking_time = reservation.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
            now = datetime.now(IST)
            duration = max(1, int((now - booking_time).total_seconds() / 3600))
            estimated_cost = duration * reservation.cost_per_unit_time

            result["reservation"] = {
                "id": reservation.id,
                "user_id": reservation.user_id,
                "username": reservation.user.username,
                "vehicle_number": reservation.vehicle_number,
                "booking_time": booking_time.isoformat(),
                "duration_hours": duration,
                "estimated_cost": estimated_cost,
            }

    return jsonify({"spot": result}), 200


# ─── Delete Spot ───
@api_admin_blueprint.route('/spots/<int:spot_id>', methods=['DELETE'])
@jwt_required()
def delete_spot(spot_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    spot = ParkingSpot.query.filter_by(id=spot_id).first()
    if spot is None:
        return jsonify({"error": "Spot not found"}), 404

    if spot.status != 'A':
        return jsonify({"error": "Cannot delete an occupied spot"}), 409

    lot = spot.lot
    db.session.delete(spot)
    lot.max_spots -= 1
    db.session.commit()

    return jsonify({"message": "Spot deleted successfully"}), 200


# ─── Users ───
@api_admin_blueprint.route('/users', methods=['GET'])
@jwt_required()
def view_users():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    users = Users.query.filter(Users.role != 'admin').all()
    users_data = [serialize_user(u) for u in users]
    return jsonify({"users": users_data}), 200


# ─── User Booking History (admin view) ───
@api_admin_blueprint.route('/users/<int:user_id>/history', methods=['GET'])
@jwt_required()
def user_booking_history(user_id):
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Single query with eager-loaded spot + lot
    history = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter_by(user_id=user.id)
        .order_by(Reservation.booking_timestamp.desc())
        .all()
    )

    history_data = []
    total_amount_paid = 0
    total_duration_hours = 0.0

    for res in history:
        booking_ist = res.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
        releasing_ist = res.releasing_timestamp.replace(tzinfo=UTC).astimezone(IST).isoformat() if res.releasing_timestamp else None
        spot = res.spot
        lot = spot.lot if spot else None

        total_amount_paid += res.total_cost or 0
        if res.booking_timestamp and res.releasing_timestamp:
            b = booking_ist
            r = res.releasing_timestamp.replace(tzinfo=UTC).astimezone(IST)
            total_duration_hours += (r - b).total_seconds() / 3600

        history_data.append({
            "id": res.id,
            "lot_name": lot.parking_name if lot else "Unknown",
            "spot_number": spot.spot_number if spot else "?",
            "vehicle_number": res.vehicle_number,
            "booking_timestamp": booking_ist.isoformat(),
            "releasing_timestamp": releasing_ist,
            "total_cost": res.total_cost,
            "status": res.status,
        })

    total_duration_hours = round(total_duration_hours, 2)
    total_bookings = len(history)
    first_booking = history[-1].booking_timestamp.replace(tzinfo=UTC).astimezone(IST).isoformat() if history else None
    latest_booking = history[0].booking_timestamp.replace(tzinfo=UTC).astimezone(IST).isoformat() if history else None

    return jsonify({
        "user": serialize_user(user),
        "history": history_data,
        "total_amount_paid": total_amount_paid,
        "total_duration_hours": total_duration_hours,
        "total_bookings": total_bookings,
        "first_booking": first_booking,
        "latest_booking": latest_booking,
    }), 200


# ─── Admin Summary (charts) ───
@api_admin_blueprint.route('/summary', methods=['GET'])
@jwt_required()
def admin_summary():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    # 1. Spot occupancy
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter(ParkingSpot.status != 'A').count()
    available_spots = total_spots - occupied_spots

    # 2. Bookings per month (last year)
    today = datetime.utcnow().date()
    one_year_ago = today - timedelta(days=365)

    monthly_data = db.session.query(
        func.to_char(Reservation.booking_timestamp, 'YYYY-MM').label('month'),
        func.count(Reservation.id)
    ).filter(
        Reservation.booking_timestamp >= one_year_ago
    ).group_by(
        func.to_char(Reservation.booking_timestamp, 'YYYY-MM')
    ).order_by(
        func.to_char(Reservation.booking_timestamp, 'YYYY-MM')
    ).all()

    months = []
    bookings_per_month = []
    for month_str, count in monthly_data:
        month_dt = datetime.strptime(month_str, "%Y-%m")
        months.append(month_dt.strftime("%b %Y"))
        bookings_per_month.append(count)

    # 3. User registrations per month
    registration_stats = (
        db.session.query(
            func.to_char(Users.member_since, 'YYYY-MM').label('month'),
            func.count(Users.id).label('users_count')
        )
        .filter(Users.member_since >= one_year_ago)
        .group_by(func.to_char(Users.member_since, 'YYYY-MM'))
        .order_by(func.to_char(Users.member_since, 'YYYY-MM'))
        .all()
    )
    reg_labels = [row.month for row in registration_stats]
    reg_data = [row.users_count for row in registration_stats]

    # 4. Top lots by usage
    top_lots = (
        db.session.query(
            ParkingLot.parking_name,
            func.count(Reservation.id).label('usage_count')
        )
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)
        .group_by(ParkingLot.id)
        .order_by(func.count(Reservation.id).desc())
        .limit(10)
        .all()
    )
    top_lot_labels = [row.parking_name for row in top_lots]
    top_lot_data = [row.usage_count for row in top_lots]

    # 5. Avg parking time per lot
    avg_parking_time = (
        db.session.query(
            ParkingLot.parking_name,
            func.avg(
                func.extract('epoch', Reservation.releasing_timestamp - Reservation.booking_timestamp) / 3600.0
            ).label('avg_duration_hours')
        )
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)
        .filter(Reservation.releasing_timestamp.isnot(None))
        .group_by(ParkingLot.id)
        .order_by(func.avg(
            func.extract('epoch', Reservation.releasing_timestamp - Reservation.booking_timestamp) / 3600.0
        ).desc())
        .limit(10)
        .all()
    )
    avg_labels = [row.parking_name for row in avg_parking_time]
    avg_data = [round(row.avg_duration_hours, 2) for row in avg_parking_time]

    return jsonify({
        "total_spots": total_spots,
        "occupied_spots": occupied_spots,
        "available_spots": available_spots,
        "months": months,
        "bookings_per_month": bookings_per_month,
        "registration_labels": reg_labels,
        "registration_data": reg_data,
        "top_lot_labels": top_lot_labels,
        "top_lot_data": top_lot_data,
        "avg_time_labels": avg_labels,
        "avg_time_data": avg_data,
    }), 200


# ─── Admin Search ───
@api_admin_blueprint.route('/search', methods=['GET'])
@jwt_required()
def admin_search():
    admin = get_admin_user()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 403

    search_type = request.args.get('type', '').strip()
    query = request.args.get('q', '').strip().lower()

    results = []

    if search_type == 'user':
        users = Users.query.filter(
            (Users.username.ilike(f"%{query}%")) |
            (Users.full_name.ilike(f"%{query}%")) |
            (Users.email.ilike(f"%{query}%"))
        ).all()
        results = [serialize_user(u) for u in users]

    elif search_type == 'lot_name':
        lots = ParkingLot.query.filter(
            ParkingLot.is_active == True,  # type: ignore
            ParkingLot.parking_name.ilike(f"%{query}%")
        ).all()
        results = [{
            "id": l.id, "parking_name": l.parking_name,
            "address": l.address, "pin_code": l.pin_code,
            "max_spots": l.max_spots, "price": l.price,
        } for l in lots]

    elif search_type == 'lot_number':
        lots = ParkingLot.query.filter(
            ParkingLot.is_active == True,  # type: ignore
            ParkingLot.pin_code.ilike(f"%{query}%")
        ).all()
        results = [{
            "id": l.id, "parking_name": l.parking_name,
            "address": l.address, "pin_code": l.pin_code,
            "max_spots": l.max_spots, "price": l.price,
        } for l in lots]

    return jsonify({"results": results, "search_type": search_type, "query": query}), 200
