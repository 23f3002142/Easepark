from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from models import db



class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(100) , unique=True , nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password= db.Column(db.String(100) , nullable=False)
    role= db.Column(db.String(15), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    pin_code = db.Column(db.String(10), nullable=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class ParkingLot(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot',cascade="all, delete", lazy=True)


class ParkingSpot(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=True) # spot number that can be given to human for finding the spot
    status = db.Column(db.String(1), default='A') # A can be considered as 'Available' at first.
    is_active = db.Column(db.Boolean, default=True) # this show wether the spot is accessible or disabled by the admin
    reservations = db.relationship('Reservation', backref='spot', lazy=True)

class Reservation(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=True)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    cost_per_unit_time = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled