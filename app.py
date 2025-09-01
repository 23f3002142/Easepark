from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager, mail
from models import db
from models.user_model import Users, ParkingLot , ParkingSpot,Reservation
from controllers.admin_routes import admin_blueprint
from controllers.user_routes import user_blueprint
from controllers.auth_routes import auth
import os
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv()


app=Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'auth.login'# type: ignore

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT",587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
  

mail = Mail(app)  # initialize Mail with app
mail.init_app(app)


app.register_blueprint(auth)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint,)

@app.before_request 
def create_admin_user():
    admin = Users.query.filter_by(username='admin').first()
    if not admin:
        admin = Users(
            username='admin',# type: ignore
            email='adminxyz@gmail.com',# type: ignore
            password=generate_password_hash('admin123'),# type: ignore
            role='admin'# type: ignore
        )
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)