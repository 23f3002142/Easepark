from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from models.user_model import Users, ParkingLot, ParkingSpot, Reservation, db, Payment
from datetime import datetime, timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import joinedload
from extensions import limiter
from cache import cached, invalidate_cache
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os
import random
import razorpay
import base64
import math

api_user_blueprint = Blueprint('api_user', __name__, url_prefix='/api/user')

razorpay_client = razorpay.Client(
    auth=(os.environ.get("RAZORPAY_KEY_ID"), os.environ.get("RAZORPAY_KEY_SECRET"))
)

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
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
@api_user_blueprint.route('/dashboard', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def dashboard():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    # Active reservations — single query with eager-loaded spot + lot
    active_reservations = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter_by(user_id=user.id, status='active')
        .all()
    )
    active_bookings = []
    for res in active_reservations:
        lot = res.spot.lot if res.spot else None
        if lot is None:
            continue
        local_time = res.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
        active_bookings.append({
            "reservation_id": res.id,
            "lot_name": lot.parking_name,
            "spot_number": res.spot.spot_number,
            "date": local_time.strftime('%d %b %Y'),
            "time_range": local_time.strftime('%I:%M %p') + " - Now",
        })

    # Nearby lots by pin code — single query with spot counts
    spot_counts = (
        db.session.query(
            ParkingSpot.lot_id,
            func.count(ParkingSpot.id).label('total'),
            func.count(ParkingSpot.id).filter(ParkingSpot.status == 'A').label('free')
        )
        .group_by(ParkingSpot.lot_id)
        .subquery()
    )
    nearby = (
        db.session.query(ParkingLot, spot_counts.c.total, spot_counts.c.free)
        .outerjoin(spot_counts, ParkingLot.id == spot_counts.c.lot_id)
        .filter(ParkingLot.pin_code == user.pin_code, ParkingLot.is_active == True)
        .all()
    )
    available_lots = []
    for lot, total, free in nearby:
        available_lots.append({
            "id": lot.id,
            "name": lot.parking_name,
            "free_spots": free or 0,
            "total_spots": total or 0,
        })

    # Chart data — aggregate in DB instead of Python
    chart_rows = (
        db.session.query(
            func.to_char(Reservation.booking_timestamp, 'DD Mon').label('d'),
            func.count(Reservation.id)
        )
        .filter(Reservation.user_id == user.id)
        .group_by(func.to_char(Reservation.booking_timestamp, 'DD Mon'))
        .order_by(func.min(Reservation.booking_timestamp))
        .all()
    )
    chart_labels = [r[0] for r in chart_rows]
    chart_data = [r[1] for r in chart_rows]

    notifications = [
        "New parking lots added recently — check nearby lots now!",
        "View your booking history and release spots when done.",
        "Charges are calculated hourly — remember to release your spot in time!",
    ]

    return jsonify({
        "user": serialize_user(user),
        "active_bookings": active_bookings,
        "available_lots": available_lots,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "notifications": notifications,
    }), 200


def _invalidate_user_cache(user_id):
    """Clear cached data for a user after mutations."""
    invalidate_cache(f"user_dashboard:u:{user_id}*")
    invalidate_cache(f"user_history:u:{user_id}*")
    invalidate_cache(f"user_summary:u:{user_id}*")
    invalidate_cache("lots:*")


# ─── Profile ───
@api_user_blueprint.route('/profile', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def profile_view():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"user": serialize_user(user)}), 200


@api_user_blueprint.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def profile_edit():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    user.full_name = data.get('full_name', user.full_name)
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.address = data.get('address', user.address)
    user.pin_code = data.get('pin_code', user.pin_code)

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully", "user": serialize_user(user)}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500


# ─── Lots (for booking) ───
@api_user_blueprint.route('/lots', methods=['GET'])
@jwt_required()
def get_lots():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)

    # Build spot counts subquery once
    spot_counts = (
        db.session.query(
            ParkingSpot.lot_id,
            func.count(ParkingSpot.id).label('total'),
            func.count(ParkingSpot.id).filter(ParkingSpot.status == 'A').label('free')
        )
        .group_by(ParkingSpot.lot_id)
        .subquery()
    )

    lots_query = (
        db.session.query(ParkingLot, spot_counts.c.total, spot_counts.c.free)
        .outerjoin(spot_counts, ParkingLot.id == spot_counts.c.lot_id)
        .filter(ParkingLot.is_active == True)
    )

    if search_query:
        lots_query = lots_query.filter(
            or_(
                ParkingLot.parking_name.ilike(f'%{search_query}%'),
                ParkingLot.address.ilike(f'%{search_query}%'),
                ParkingLot.pin_code.ilike(f'%{search_query}%')
            )
        )

    pagination = lots_query.paginate(page=page, per_page=per_page, error_out=False)

    lots_data = []
    for lot, total, free in pagination.items:
        lots_data.append({
            "id": lot.id,
            "name": lot.parking_name,
            "address": lot.address,
            "price": lot.price,
            "pin_code": lot.pin_code,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "max_spots": lot.max_spots,
            "total_spots": total or 0,
            "free_spots": free or 0,
        })

    return jsonify({
        "lots": lots_data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
        }
    }), 200


@api_user_blueprint.route('/lots/all', methods=['GET'])
@jwt_required()
def get_all_lots_for_map():
    spot_counts = (
        db.session.query(
            ParkingSpot.lot_id,
            func.count(ParkingSpot.id).filter(ParkingSpot.status == 'A').label('free')
        )
        .group_by(ParkingSpot.lot_id)
        .subquery()
    )
    lots = (
        db.session.query(ParkingLot, spot_counts.c.free)
        .outerjoin(spot_counts, ParkingLot.id == spot_counts.c.lot_id)
        .filter(ParkingLot.is_active == True)
        .all()
    )
    lots_data = []
    for lot, free in lots:
        lots_data.append({
            "id": lot.id,
            "name": lot.parking_name,
            "address": lot.address,
            "price": lot.price,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "max_spots": lot.max_spots,
            "free_spots": free or 0,
        })
    return jsonify({"lots": lots_data}), 200


# ─── Nearby Lots (Haversine) ───
def _haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lng points using Haversine formula."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@api_user_blueprint.route('/lots/nearby', methods=['GET'])
@jwt_required()
@limiter.limit("20 per 1 minute")
def get_nearby_lots():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    limit = request.args.get('limit', 5, type=int)

    if lat is None or lng is None:
        return jsonify({"error": "lat and lng query params required"}), 400

    # Get all active lots with free spot counts in one query
    spot_counts = (
        db.session.query(
            ParkingSpot.lot_id,
            func.count(ParkingSpot.id).filter(ParkingSpot.status == 'A').label('free')
        )
        .group_by(ParkingSpot.lot_id)
        .subquery()
    )
    lots = (
        db.session.query(ParkingLot, spot_counts.c.free)
        .outerjoin(spot_counts, ParkingLot.id == spot_counts.c.lot_id)
        .filter(ParkingLot.is_active == True)
        .all()
    )

    # Calculate distance and filter — all in-memory, instant for < 10k lots
    results = []
    for lot, free in lots:
        free = free or 0
        if free <= 0:
            continue  # Skip full lots
        if not lot.latitude or not lot.longitude:
            continue
        dist = _haversine(lat, lng, lot.latitude, lot.longitude)
        results.append({
            "id": lot.id,
            "name": lot.parking_name,
            "address": lot.address,
            "price": lot.price,
            "latitude": lot.latitude,
            "longitude": lot.longitude,
            "max_spots": lot.max_spots,
            "free_spots": free,
            "distance_km": round(dist, 2),
        })

    # Sort by distance ascending, take top N
    results.sort(key=lambda x: x["distance_km"])
    results = results[:limit]

    return jsonify({"lots": results}), 200


# ─── Reserve Spot ───
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
        to=to, sender=sender, subject=subject, text_content=text_content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Brevo API Exception:", e)


OTP_EXPIRY_MINUTES = 10
RELEASE_EXPIRY_MINUTES = 5


def cleanup_stale_pending_reservations():
    """Auto-cancel stale pending reservations and revert stale pending_release → active."""
    now = datetime.utcnow()
    changed = False

    # Stale pending bookings (10 min) → cancel + free spot
    pending_cutoff = now - timedelta(minutes=OTP_EXPIRY_MINUTES)
    stale_pending = (
        Reservation.query
        .options(joinedload(Reservation.spot))
        .filter(
            Reservation.status == 'pending',
            Reservation.booking_timestamp < pending_cutoff
        )
        .all()
    )
    for res in stale_pending:
        res.status = 'cancelled'
        if res.spot and res.spot.status == 'O':
            res.spot.status = 'A'
        res.otp_secret = None
        changed = True

    # Stale pending_release (5 min) → revert to active
    release_cutoff = now - timedelta(minutes=RELEASE_EXPIRY_MINUTES)
    stale_release = (
        Reservation.query
        .filter(
            Reservation.status == 'pending_release',
            Reservation.booking_timestamp < release_cutoff
        )
        .all()
    )
    for res in stale_release:
        res.status = 'active'
        res.otp_secret = None
        res.otp_verified = False
        changed = True

    if changed:
        db.session.commit()


@api_user_blueprint.route('/book/<int:lot_id>', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def reserve_spot(lot_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    # Clean up expired pending reservations before processing
    cleanup_stale_pending_reservations()

    lot = ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        return jsonify({"error": "Lot not found"}), 404

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.spot_number.asc()).first()
    if not spot:
        return jsonify({"error": "No available spots in this lot"}), 409

    data = request.get_json() or {}
    vehicle_number = data.get("vehicle_number", "").strip()

    if not vehicle_number:
        return jsonify({"error": "Vehicle number is required"}), 400

    # Check if vehicle already has active reservation
    active_reservation = Reservation.query.filter_by(vehicle_number=vehicle_number, status="active").first()
    if active_reservation:
        return jsonify({"error": "This vehicle already has an active reservation"}), 409

    # Create active reservation directly — no OTP needed at booking time
    current_time = datetime.now(IST)
    reservation = Reservation(
        spot_id=spot.id,  # type: ignore
        user_id=user.id,  # type: ignore
        vehicle_number=vehicle_number,  # type: ignore
        cost_per_unit_time=lot.price,  # type: ignore
        booking_timestamp=current_time,  # type: ignore
        status="active",  # type: ignore
        otp_required=False,  # type: ignore
        otp_verified=False,  # type: ignore
    )
    spot.status = 'O'
    user.total_bookings += 1
    db.session.add(reservation)
    db.session.commit()
    _invalidate_user_cache(user.id)

    return jsonify({
        "message": f"Spot {spot.spot_number} reserved successfully!",
        "reservation_id": reservation.id,
        "spot_number": spot.spot_number,
    }), 201


# ─── Booking History ───
@api_user_blueprint.route('/history', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def booking_history():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 7, type=int)

    pagination = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter_by(user_id=user.id)
        .order_by(Reservation.booking_timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    history = []
    for res in pagination.items:
        booking_ist = res.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
        releasing_ist = None
        if res.releasing_timestamp:
            releasing_ist = res.releasing_timestamp.replace(tzinfo=UTC).astimezone(IST).isoformat()

        spot = res.spot
        lot = spot.lot if spot else None

        history.append({
            "id": res.id,
            "lot_name": lot.parking_name if lot else "Unknown",
            "spot_number": spot.spot_number if spot else "?",
            "vehicle_number": res.vehicle_number,
            "booking_timestamp": booking_ist.isoformat(),
            "releasing_timestamp": releasing_ist,
            "total_cost": res.total_cost,
            "status": res.status,
        })

    return jsonify({
        "history": history,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
        }
    }), 200


# ─── Cancel Booking ───
@api_user_blueprint.route('/cancel/<int:reservation_id>', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def cancel_booking(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = (
        Reservation.query
        .options(joinedload(Reservation.spot))
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
            Reservation.status.in_(['active', 'pending'])
        )
        .first()
    )

    if not reservation:
        return jsonify({"error": "Reservation not found or already completed"}), 404

    # Free the spot if it was occupied
    spot = reservation.spot
    if spot and spot.status == 'O':
        spot.status = 'A'

    reservation.status = 'cancelled'
    reservation.releasing_timestamp = datetime.utcnow()
    reservation.total_cost = 0
    reservation.otp_secret = None

    db.session.commit()
    _invalidate_user_cache(user.id)

    return jsonify({"message": "Booking cancelled successfully. No charges applied."}), 200


# ─── Release Spot ───
@api_user_blueprint.route('/release/<int:reservation_id>', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def release_spot_info(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
            or_(Reservation.status == 'active', Reservation.status == 'pending_release')
        )
        .first()
    )

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    spot = reservation.spot
    lot = spot.lot if spot else None

    now = datetime.now(IST)
    booking_time = reservation.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
    duration = max(1, int((now - booking_time).total_seconds() / 3600))
    estimated_cost = duration * reservation.cost_per_unit_time

    return jsonify({
        "reservation_id": reservation.id,
        "lot_name": lot.parking_name if lot else "Unknown",
        "spot_number": spot.spot_number if spot else "?",
        "vehicle_number": reservation.vehicle_number,
        "booking_time": booking_time.isoformat(),
        "current_time": now.isoformat(),
        "duration_hours": duration,
        "estimated_cost": estimated_cost,
        "cost_per_hour": reservation.cost_per_unit_time,
    }), 200


# ─── Release Confirmation: Send OTP ───
@api_user_blueprint.route('/release/<int:reservation_id>/send-otp', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def release_send_otp(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = Reservation.query.filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user.id,
        Reservation.status == 'active',
    ).first()
    if not reservation:
        return jsonify({"error": "Active reservation not found"}), 404

    otp = generate_otp()
    reservation.otp_secret = otp
    reservation.otp_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    reservation.status = 'pending_release'
    db.session.commit()

    send_otp_email(user.email, otp)
    return jsonify({"message": "OTP sent to your registered email"}), 200


# ─── Release Confirmation: Verify OTP ───
@api_user_blueprint.route('/release/<int:reservation_id>/verify-otp', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def release_verify_otp(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    otp_entered = data.get("otp", "").strip()
    if not otp_entered:
        return jsonify({"error": "OTP is required"}), 400

    reservation = Reservation.query.filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user.id,
        Reservation.status == 'pending_release',
    ).first()
    if not reservation:
        return jsonify({"error": "Reservation not found or not pending release"}), 404

    if reservation.otp_expires_at and datetime.utcnow() > reservation.otp_expires_at:
        reservation.status = 'active'
        reservation.otp_secret = None
        db.session.commit()
        return jsonify({"error": "OTP has expired. Please try again."}), 400

    if reservation.otp_secret != otp_entered:
        return jsonify({"error": "Invalid OTP"}), 400

    reservation.otp_secret = None
    reservation.otp_verified = True
    db.session.commit()
    return jsonify({"message": "OTP verified. Proceed to payment."}), 200


# ─── Release Confirmation: Verify Password ───
@api_user_blueprint.route('/release/<int:reservation_id>/verify-password', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def release_verify_password(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "Password is required"}), 400

    if not user.password:
        return jsonify({"error": "Password verification not available for Google accounts. Please use OTP."}), 400

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401

    reservation = Reservation.query.filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user.id,
        Reservation.status.in_(['active', 'pending_release']),
    ).first()
    if not reservation:
        return jsonify({"error": "Active reservation not found"}), 404

    reservation.status = 'pending_release'
    reservation.otp_verified = True
    reservation.otp_secret = None
    db.session.commit()
    return jsonify({"message": "Password verified. Proceed to payment."}), 200


# ─── Cancel Release (revert pending_release → active) ───
@api_user_blueprint.route('/release/<int:reservation_id>/cancel', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def cancel_release(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = Reservation.query.filter(
        Reservation.id == reservation_id,
        Reservation.user_id == user.id,
        Reservation.status == 'pending_release',
    ).first()
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    reservation.status = 'active'
    reservation.otp_secret = None
    reservation.otp_verified = False
    db.session.commit()
    return jsonify({"message": "Release cancelled. Booking is still active."}), 200


@api_user_blueprint.route('/release/<int:reservation_id>', methods=['POST'])
@jwt_required()
@limiter.limit("10 per 3 minute")
def release_spot(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
            Reservation.status == 'pending_release',
            Reservation.otp_verified == True,
        )
        .first()
    )

    if not reservation:
        return jsonify({"error": "Reservation not verified for release. Confirm via OTP or password first."}), 403

    spot = reservation.spot
    lot = spot.lot if spot else None

    now = datetime.now(IST)
    booking_time = reservation.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
    duration = max(1, int((now - booking_time).total_seconds() / 3600))
    estimated_cost = duration * reservation.cost_per_unit_time

    # Create Razorpay order
    amount_paise = int(estimated_cost * 100)
    order = razorpay_client.order.create(dict(
        amount=amount_paise,
        currency='INR',
        payment_capture='1'
    ))

    return jsonify({
        "order_id": order['id'],
        "razorpay_key_id": os.environ.get("RAZORPAY_KEY_ID"),
        "amount": estimated_cost,
        "amount_paise": amount_paise,
        "reservation_id": reservation.id,
        "lot_name": lot.parking_name,
        "duration_hours": duration,
        "user_name": user.full_name or "",
        "user_email": user.email or "",
        "user_phone": user.phone_number or "",
    }), 200


# ─── Payment Verification ───
@api_user_blueprint.route('/payment/verify', methods=['POST'])
@jwt_required()
def payment_verify():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    payment_id = data.get("payment_id")
    order_id = data.get("order_id")
    signature = data.get("signature")
    reservation_id = data.get("reservation_id")

    if not all([payment_id, order_id, signature, reservation_id]):
        return jsonify({"error": "Payment info missing"}), 400

    # Verify Razorpay signature to prevent forged payments
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except Exception:
        return jsonify({"error": "Payment signature verification failed"}), 400

    reservation = db.session.get(Reservation, reservation_id)
    if not reservation or reservation.user_id != user.id:
        return jsonify({"error": "Reservation not found"}), 404

    release_time = datetime.now(IST)
    booking_time = reservation.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
    duration = max(1, int((release_time - booking_time).total_seconds() / 3600))
    total_cost = duration * reservation.cost_per_unit_time

    spot = db.session.get(ParkingSpot, reservation.spot_id)

    reservation.releasing_timestamp = datetime.utcnow()
    reservation.total_cost = total_cost
    reservation.status = 'completed'
    reservation.otp_required = False
    reservation.otp_verified = False
    reservation.otp_secret = None
    if spot:
        spot.status = 'A'

    payment = Payment(
        reservation_id=reservation.id,  # type: ignore
        razorpay_payment_id=payment_id,  # type: ignore
        razorpay_order_id=order_id,  # type: ignore
        amount=total_cost,  # type: ignore
        status='success',  # type: ignore
    )
    db.session.add(payment)
    db.session.commit()
    _invalidate_user_cache(user.id)

    # Send receipt email
    try:
        lot = db.session.get(ParkingLot, spot.lot_id) if spot else None
        if lot and spot:
            send_receipt_email(user, reservation, lot, spot)
    except Exception as e:
        print("Error sending receipt email:", e)

    return jsonify({"message": "Payment successful. Spot released.", "total_cost": total_cost}), 200


# ─── Receipt ───
def generate_receipt_pdf(reservation, lot, spot):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#2C3E50"))
    c.drawCentredString(300, 750, "EasePark Parking Receipt")

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, 740, 550, 740)

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
        ("Total Cost", f"Rs.{reservation.total_cost or 0}"),
    ]

    for label, value in details:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(200, y, str(value))
        y -= line_gap

    c.setFillColor(colors.HexColor("#16A085"))
    c.setFont("Helvetica-BoldOblique", 14)
    c.drawCentredString(300, y - 40, "Thank you for using EasePark!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def send_receipt_email(user, reservation, lot, spot):
    pdf_buffer = generate_receipt_pdf(reservation, lot, spot)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "EasePark Booking Receipt"
    sender = {"email": os.getenv("MAIL_DEFAULT_SENDER")}
    to = [{"email": user.email}]
    text_content = (
        f"Hello {user.username},\n\n"
        f"Here is your receipt for your recent booking with EasePark:\n\n"
        f"Lot: {lot.parking_name}\n"
        f"Spot: {spot.spot_number}\n"
        f"Total Cost: Rs.{reservation.total_cost}\n\n"
        f"Thank you for choosing EasePark!"
    )

    pdf_content = base64.b64encode(pdf_buffer.read()).decode('utf-8')

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, sender=sender, subject=subject, text_content=text_content,
        attachment=[{"content": pdf_content, "name": f"receipt_{reservation.id}.pdf"}]
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Brevo API Exception:", e)


@api_user_blueprint.route('/receipt/<int:reservation_id>', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def download_receipt(reservation_id):
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user.id).first()
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    spot = ParkingSpot.query.get(reservation.spot_id)
    if spot is None:
        return jsonify({"error": "Spot not found"}), 404
    lot = spot.lot

    pdf_buffer = generate_receipt_pdf(reservation, lot, spot)

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{reservation.id}.pdf'
    return response


# ─── User Summary ───
@api_user_blueprint.route('/summary', methods=['GET'])
@jwt_required()
@limiter.limit("10 per 1 minute")
def user_summary():
    user = get_current_user()
    if not user or user.role != 'user':
        return jsonify({"error": "Unauthorized"}), 403

    # Only include active and completed reservations in stats (not pending/cancelled)
    all_reservations = (
        Reservation.query
        .filter(
            Reservation.user_id == user.id,
            Reservation.status.in_(['active', 'completed', 'pending_release'])
        )
        .order_by(Reservation.booking_timestamp.desc())
        .all()
    )

    # Convert timestamps
    for res in all_reservations:
        res.booking_timestamp_ist = res.booking_timestamp.replace(tzinfo=UTC).astimezone(IST) if res.booking_timestamp else None
        res.releasing_timestamp_ist = res.releasing_timestamp.replace(tzinfo=UTC).astimezone(IST) if res.releasing_timestamp else None

    total_amount_paid = sum(res.total_cost or 0 for res in all_reservations)

    total_duration_hours = 0
    for res in all_reservations:
        if res.booking_timestamp_ist and res.releasing_timestamp_ist:
            duration = (res.releasing_timestamp_ist - res.booking_timestamp_ist).total_seconds() / 3600
            total_duration_hours += duration
    total_duration_hours = round(total_duration_hours, 2)

    total_bookings = len(all_reservations)
    first_booking = all_reservations[-1].booking_timestamp_ist.isoformat() if all_reservations and all_reservations[-1].booking_timestamp_ist else None
    latest_booking = all_reservations[0].booking_timestamp_ist.isoformat() if all_reservations and all_reservations[0].booking_timestamp_ist else None

    # Booking over time chart
    booking_counts = defaultdict(int)
    for res in all_reservations:
        if res.booking_timestamp_ist:
            date_str = res.booking_timestamp_ist.strftime('%d %b')
            booking_counts[date_str] += 1

    sorted_dates = sorted(booking_counts.items(), key=lambda x: datetime.strptime(x[0], '%d %b'))
    chart_labels = [d[0] for d in sorted_dates]
    chart_data = [d[1] for d in sorted_dates]

    # Duration distribution
    duration_buckets = {
        '<3 hrs': 0, '3-6 hrs': 0, '6-9 hrs': 0,
        '9-12 hrs': 0, '12+ hrs': 0, '1 day+': 0, '>2 days': 0
    }
    for res in all_reservations:
        if res.booking_timestamp_ist and res.releasing_timestamp_ist:
            d = (res.releasing_timestamp_ist - res.booking_timestamp_ist).total_seconds() / 3600
            if d < 3: duration_buckets['<3 hrs'] += 1
            elif d <= 6: duration_buckets['3-6 hrs'] += 1
            elif d <= 9: duration_buckets['6-9 hrs'] += 1
            elif d <= 12: duration_buckets['9-12 hrs'] += 1
            elif d <= 24: duration_buckets['12+ hrs'] += 1
            elif d <= 48: duration_buckets['1 day+'] += 1
            else: duration_buckets['>2 days'] += 1

    # Duration vs cost scatter
    booking_labels = []
    duration_values = []
    cost_values = []
    for idx, res in enumerate(all_reservations):
        if res.booking_timestamp_ist and res.releasing_timestamp_ist and res.total_cost:
            d = (res.releasing_timestamp_ist - res.booking_timestamp_ist).total_seconds() / 3600
            booking_labels.append(f"Booking {idx + 1}")
            duration_values.append(round(d, 2))
            cost_values.append(res.total_cost)

    # Paginated history for the summary page
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagination = (
        Reservation.query
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter_by(user_id=user.id)
        .order_by(Reservation.booking_timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    history = []
    for res in pagination.items:
        booking_ist = res.booking_timestamp.replace(tzinfo=UTC).astimezone(IST)
        releasing_ist = res.releasing_timestamp.replace(tzinfo=UTC).astimezone(IST).isoformat() if res.releasing_timestamp else None
        spot = res.spot
        lot = spot.lot if spot else None
        history.append({
            "id": res.id,
            "lot_name": lot.parking_name if lot else "Unknown",
            "spot_number": spot.spot_number if spot else "?",
            "vehicle_number": res.vehicle_number,
            "booking_timestamp": booking_ist.isoformat(),
            "releasing_timestamp": releasing_ist,
            "total_cost": res.total_cost,
            "status": res.status,
        })

    return jsonify({
        "user": serialize_user(user),
        "total_amount_paid": total_amount_paid,
        "total_duration_hours": total_duration_hours,
        "total_bookings": total_bookings,
        "first_booking": first_booking,
        "latest_booking": latest_booking,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "chart_duration_labels": list(duration_buckets.keys()),
        "chart_duration_data": list(duration_buckets.values()),
        "chart_booking_labels": booking_labels,
        "chart_duration_data_each": duration_values,
        "chart_cost_data_each": cost_values,
        "history": history,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
        }
    }), 200
