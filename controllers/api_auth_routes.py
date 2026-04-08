from flask import Blueprint, request, jsonify, session, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user_model import Users, db
from extensions import oauth
from urllib.parse import quote_plus
import base64
import os

api_auth = Blueprint('api_auth', __name__, url_prefix='/api/auth')


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


def _normalized_frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _oauth_error_redirect(message: str):
    return redirect(f"{_normalized_frontend_url()}/login?oauth_error={quote_plus(message)}")


def _generate_unique_username(seed: str) -> str:
    base = (seed or "user").strip().lower()
    # Keep usernames predictable and DB-safe.
    cleaned = ''.join(ch for ch in base if ch.isalnum() or ch in ['.', '_', '-']).strip('._-')
    if not cleaned:
        cleaned = "user"

    candidate = cleaned[:80]
    if not Users.query.filter_by(username=candidate).first():
        return candidate

    suffix = 1
    while True:
        suffix_str = str(suffix)
        trimmed = cleaned[: max(1, 80 - len(suffix_str) - 1)]
        candidate = f"{trimmed}_{suffix_str}"
        if not Users.query.filter_by(username=candidate).first():
            return candidate
        suffix += 1


@api_auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hash_pw = generate_password_hash(password)
    user = Users(username=username, email=email, password=hash_pw, role="user")  # type: ignore
    db.session.add(user)

    try:
        db.session.commit()
        return jsonify({"message": "Registration successful"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Registration failed. Please try again."}), 500


@api_auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = Users.query.filter_by(username=username).first()

    if not user or not user.password or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "user": serialize_user(user),
    }), 200


@api_auth.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": serialize_user(user)}), 200


@api_auth.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400

    # Google OAuth users have no password set
    if not user.password:
        return jsonify({"error": "Password change is not available for Google sign-in accounts"}), 400

    if not check_password_hash(user.password, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    user.password = generate_password_hash(new_password)

    try:
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to change password"}), 500


@api_auth.route("/google-login", methods=["GET"])
def google_login():
    base_url = os.getenv("BASE_URL", request.host_url.rstrip("/"))
    redirect_uri = f"{base_url}{url_for('api_auth.google_authorize')}"
    nonce = base64.urlsafe_b64encode(os.urandom(16)).decode()
    session["nonce"] = nonce
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])  # type: ignore


@api_auth.route("/google-authorize", methods=["GET"])
def google_authorize():
    try:
        token = oauth.google.authorize_access_token()  # type: ignore
        nonce = session.pop("nonce", None)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)  # type: ignore
    except Exception:
        return _oauth_error_redirect("Google sign-in failed. Please try again.")

    email = (user_info.get("email") or "").strip().lower() if user_info else ""
    full_name = (user_info.get("name") or "").strip() if user_info else ""

    if not email:
        return _oauth_error_redirect("Google account email was not provided.")

    user = Users.query.filter_by(email=email).first()

    if not user:
        username_seed = email.split("@")[0]
        if full_name:
            username_seed = username_seed or full_name
        username = _generate_unique_username(username_seed)

        user = Users(
            email=email,  # type: ignore
            username=username,  # type: ignore
            full_name=full_name or username,  # type: ignore
            password=None,  # type: ignore
            role="user",  # type: ignore
        )
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return _oauth_error_redirect("Could not complete Google sign-in. Please try again.")

    access_token = create_access_token(identity=str(user.id))

    # Redirect to Vue frontend with token as query param
    return redirect(f"{_normalized_frontend_url()}/auth/callback?token={access_token}")
