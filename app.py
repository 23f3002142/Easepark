
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager 
from models.user_model import Users
from models import db
from models.user_model import Users, ParkingLot , ParkingSpot,Reservation ,db
from controllers.admin_routes import admin_blueprint
from controllers.user_routes import user_blueprint
from controllers.auth_routes import auth




app=Flask(__name__)
app.config['SECRET_KEY']= 'kdmn@1924'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easepark.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'# type: ignore

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

app.register_blueprint(auth)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)

@app.route('/')
def home():
    return render_template('home.html')

if __name__=='__main__':
    with app.app_context():
        db.create_all()

        admin = Users.query.filter_by(username='admin').first()
        if not admin:
            admin = Users(
                username='admin', # type: ignore
                email='adminxyz@gmail.com',# type: ignore
                password=generate_password_hash('admin123'),# type: ignore
                role='admin' # type: ignore
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
