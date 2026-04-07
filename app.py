# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from flask import Flask,render_template,flash, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager, mail,limiter,oauth, jwt, cors
from models import db
from models.user_model import Users
from controllers.admin_routes import admin_blueprint
from controllers.user_routes import user_blueprint
from controllers.auth_routes import auth
from controllers.api_auth_routes import api_auth
from controllers.api_user_routes import api_user_blueprint
from controllers.api_admin_routes import api_admin_blueprint
from flask_mail import Mail
from flask_limiter.errors import RateLimitExceeded
from flask_migrate import Migrate
from datetime import timedelta

import os


app=Flask(__name__)

#config
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv("SQLALCHEMY_DATABASE_URI")


if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Only add sslmode for remote databases (not localhost)
if database_url and 'sslmode' not in database_url and 'localhost' not in database_url and '127.0.0.1' not in database_url:
    database_url += '?sslmode=require'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 280, 
    "pool_pre_ping": True  
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Rate limiter: only set Redis URL if available, otherwise use memory storage
redis_url = os.getenv("REDIS_URL")
if redis_url and redis_url.strip():
    app.config['RATELIMIT_STORAGE_URI'] = redis_url
# Session cookies: set SECURE=True only in production (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

#JWT config
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY", "jwt-fallback-secret")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db.init_app(app)
migrate = Migrate(app, db)

#JWT & CORS
jwt.init_app(app)
frontend_origin = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [o.strip() for o in frontend_origin.split(",") if o.strip()]
# Always allow localhost for development
if "http://localhost:5173" not in allowed_origins:
    allowed_origins.append("http://localhost:5173")
# In production, prioritize the actual frontend URL
if os.getenv("BASE_URL"):  # This indicates we're in production
    production_frontend = os.getenv("FRONTEND_URL")
    if production_frontend and production_frontend not in allowed_origins:
        allowed_origins.insert(0, production_frontend)
cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

#rate_limiter
limiter.init_app(app)
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Too many requests. Please try again later."}), 429
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
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "False") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")
mail.init_app(app)


#Blueprint (legacy server-rendered)
app.register_blueprint(auth)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)

#API Blueprints (JSON for Vue frontend)
app.register_blueprint(api_auth)
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_admin_blueprint)

#hardcoded Admin(for starter purposes , will be changed at the time of production)
def seed_admin_user():
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

# Initialize database on startup (but handle errors gracefully)
try:
    with app.app_context():
        db.create_all()
        seed_admin_user()
        print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization failed: {e}")
    # Don't fail the app startup, just log the error

# Start keep-alive thread in production
try:
    start_keep_alive()
    print("Keep-alive thread started")
except Exception as e:
    print(f"Keep-alive failed to start: {e}")

# ─── Keep-Alive Endpoint (prevents Render free tier sleep)
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "database": "disconnected", "error": str(e)}), 500


def start_keep_alive():
    """Background thread that pings the health endpoint every 13 minutes."""
    import threading
    import requests as req
    import time

    base_url = os.getenv("BASE_URL")
    if not base_url:
        return  # Only run in production where BASE_URL is set

    def ping():
        while True:
            time.sleep(13 * 60)  # 13 minutes
            try:
                req.get(f"{base_url}/api/health", timeout=10)
            except Exception:
                pass

    t = threading.Thread(target=ping, daemon=True)
    t.start()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin_user()
    # Run only when directly executed, not when imported by Gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # When imported by Gunicorn in production, start keep-alive
    start_keep_alive()
