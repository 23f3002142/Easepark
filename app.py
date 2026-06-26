
from dotenv import load_dotenv
load_dotenv()

from utils.logger import logger

from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash
from extensions import mail, limiter, oauth, jwt, cors
from models import db
from models.user_model import Users
from controllers.api_auth_routes import api_auth
from controllers.api_user_routes import api_user_blueprint
from controllers.api_admin_routes import api_admin_blueprint
from flask_limiter.errors import RateLimitExceeded
from flask_migrate import Migrate
from datetime import timedelta
from sqlalchemy import text
from flask_smorest import Api
import uuid
import os


app=Flask(__name__)

# Config OpenAPI / Swagger
app.config["API_TITLE"] = "EasePark API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/api/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

#config
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv("SQLALCHEMY_DATABASE_URI")


if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Only add sslmode for remote databases (not localhost or internal docker db)
if database_url and 'sslmode' not in database_url and 'localhost' not in database_url and '127.0.0.1' not in database_url and '@db' not in database_url:
    database_url += '?sslmode=require'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 280, 
    "pool_pre_ping": True  
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Rate limiter: only use Redis if it's actually reachable, otherwise use memory
redis_url = os.getenv("REDIS_URL")
if redis_url and redis_url.strip():
    try:
        import redis as _redis
        _kwargs = {"socket_connect_timeout": 5, "socket_timeout": 5}
        # Render external Redis uses rediss:// (TLS) — disable strict cert verification
        if redis_url.startswith("rediss://"):
            import ssl
            _kwargs["ssl_cert_reqs"] = ssl.CERT_NONE
            _kwargs["ssl_check_hostname"] = False
        _r = _redis.from_url(redis_url, **_kwargs)
        _r.ping()
        # Flask-Limiter needs the storage URI; for rediss:// also pass ssl options
        app.config['RATELIMIT_STORAGE_URI'] = redis_url
        app.config['RATELIMIT_SWALLOW_ERRORS'] = True
        if redis_url.startswith("rediss://"):
            app.config['RATELIMIT_STORAGE_OPTIONS'] = {
                "ssl_cert_reqs": "none",
                "ssl_check_hostname": False
            }
        logger.info(f"Rate limiter: using Redis ({redis_url[:30]}...)")
    except Exception as _e:
        logger.warning(f"Rate limiter: Redis unavailable ({_e}), falling back to in-memory")
        # Don't set RATELIMIT_STORAGE_URI → defaults to memory
# Session cookies: set SECURE=True only in production (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

#JWT config
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY", "jwt-fallback-secret")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

db.init_app(app)
migrate = Migrate(app, db)

#JWT & CORS
jwt.init_app(app)

# ── JWT blocklist: check Redis on every protected request ───────────────────
# When a user logs out, we write their token's JTI (unique JWT ID) into Redis.
# This callback runs before every @jwt_required() endpoint.
# If the JTI is in Redis → token is revoked → return 401 automatically.
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    try:
        from cache import redis_client
        if redis_client:
            return redis_client.get(f"blocklist:{jti}") is not None
    except Exception:
        pass
    return False  # If Redis is unavailable, allow the token (graceful degradation)

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
    return jsonify({"error": "Too many requests. Please try again later."}), 429

# Custom 422 validation error handler to keep format consistent with frontend
@app.errorhandler(422)
def handle_unprocessable_entity_error(err):
    data = getattr(err, "data", None)
    if data and "messages" in data:
        messages = data["messages"]
        if isinstance(messages, dict):
            if "json" in messages:
                messages = messages["json"]
            elif "query" in messages:
                messages = messages["query"]
        return jsonify({"errors": messages}), 422
    return jsonify({"errors": {"_schema": ["Invalid input parameters"]}}), 422

# Request ID Correlation Middleware
@app.before_request
def before_request_func():
    if not hasattr(g, 'request_id'):
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

@app.after_request
def after_request_func(response):
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    return response

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


#API Blueprints via flask-smorest
api = Api(app)
api.register_blueprint(api_auth)
api.register_blueprint(api_user_blueprint)
api.register_blueprint(api_admin_blueprint)

#hardcoded Admin — credentials come from environment variables
# WHY env vars? Because hardcoding credentials in source code is a security
# vulnerability: the password ends up in Git history forever.
def seed_admin_user():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@easepark.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    admin = Users.query.filter_by(username=admin_username).first()
    if not admin:
        admin = Users(
            username=admin_username,                        # type: ignore
            email=admin_email,                              # type: ignore
            password=generate_password_hash(admin_password),# type: ignore
            role='admin',                                   # type: ignore
            is_verified=True,                               # type: ignore  — admin is always verified
        )
        db.session.add(admin)
        db.session.commit()

# ─── Keep-Alive Endpoint (prevents Render free tier sleep) ───
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
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
        return  

    def ping():
        while True:
            time.sleep(13 * 60)  # 13 minutes
            try:
                req.get(f"{base_url}/api/health", timeout=10)
            except Exception:
                pass

    t = threading.Thread(target=ping, daemon=True)
    t.start()


try:
    with app.app_context():
        db.create_all()
        logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

# Seed the admin user
try:
    with app.app_context():
        seed_admin_user()
except Exception as e:
    logger.warning(f"[startup] Admin seed skipped (schema may be mid-migration): {e}")

# Start keep-alive thread
try:
    start_keep_alive()
except Exception as e:
    logger.error(f"Keep-alive failed to start: {e}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin_user()
    app.run(host="0.0.0.0", port=5000, debug=True)
