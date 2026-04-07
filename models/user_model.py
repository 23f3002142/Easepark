from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from models import db


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(100) , unique=True , nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password= db.Column(db.String(255) , nullable=True)
    role= db.Column(db.String(15), nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.Text, nullable=True)
    pin_code = db.Column(db.String(10), nullable=True, index=True)
    member_since = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total_bookings = db.Column(db.Integer, default=0)


    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')

class ParkingLot(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False, index=True)
    max_spots = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)

    # for map integeration
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    spots = db.relationship('ParkingSpot', backref='lot', cascade="all, delete", lazy='dynamic')


class ParkingSpot(UserMixin, db.Model):
    __table_args__ = (
        db.Index('ix_spot_lot_status', 'lot_id', 'status'),
    )
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False, index=True)
    spot_number = db.Column(db.String(20), nullable=True) # spot number that can be given to human for finding the spot
    status = db.Column(db.String(1), default='A', index=True) # A can be considered as 'Available' at first.
    is_active = db.Column(db.Boolean, default=True) # this show wether the spot is accessible or disabled by the admin
    reservations = db.relationship('Reservation', backref='spot', lazy='dynamic')

class Reservation(UserMixin, db.Model):
    __table_args__ = (
        db.Index('ix_reservation_user_status', 'user_id', 'status'),
    )
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    vehicle_number = db.Column(db.String(20), nullable=True, index=True)
    booking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    releasing_timestamp = db.Column(db.DateTime, nullable=True)
    cost_per_unit_time = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, completed, cancelled

    # for OTP confirmation (future scope)
    otp_required = db.Column(db.Boolean, default=False)
    otp_verified = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(50), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)


    # for QR-based check-in/out (future scope)
    qr_code = db.Column(db.Text, nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    razorpay_payment_id = db.Column(db.String(100), nullable=False)
    razorpay_order_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='success')  # success / failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservation = db.relationship('Reservation', backref='payment', lazy=True)
