
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from models.file1 import Users, ParkingLot , ParkingSpot,Reservation



app=Flask(__name__)
app.config['SECRET KEY ']= 'kdmn@1924'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easepark.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

db.init_app(app)
login_manager.init_app(app)



if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
