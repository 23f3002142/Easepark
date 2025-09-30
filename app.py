from flask import Flask,render_template,flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager, mail,limiter,oauth
from models import db
from models.user_model import Users
from controllers.admin_routes import admin_blueprint
from controllers.user_routes import user_blueprint
from controllers.auth_routes import auth
from flask_mail import Mail
from flask_limiter.errors import RateLimitExceeded
from dotenv import load_dotenv
from flask_migrate import Migrate

import os
load_dotenv()


app=Flask(__name__)

#config
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv("SQLALCHEMY_DATABASE_URI")

# Ensure the URL uses the 'postgresql://' prefix
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Ensure sslmode=require is set for secure connections on Render
if database_url and 'sslmode' not in database_url:
    database_url += '?sslmode=require'

# Set the final, corrected database URL
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Configure the SQLAlchemy engine to handle connection pooling and prevent timeouts
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 280,  # Recycle connections to prevent them from timing out
    "pool_pre_ping": True  # Check if a connection is alive before using it
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RATELIMIT_STORAGE_URI'] = os.getenv("REDIS_URL")

db.init_app(app)
migrate = Migrate(app, db)

#rate_limiter
limiter.init_app(app)
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    flash("Too many requests. Please try again later.", "danger")
    return redirect(url_for("user.dashboard"))

#Login Manager
login_manager.init_app(app)
login_manager.login_view = 'auth.login'# type: ignore
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

#Authlib (for OAuth)
oauth.init_app(app) 
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)



#flask_mail 
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT",587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail.init_app(app)


#Blueprint
app.register_blueprint(auth)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)

#hardcoded Admin(for starter purposes , will be changed at the time of production)
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

#home page
@app.route('/')
def home():
    return render_template('home.html')

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Run only when directly executed, not when imported by Gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
