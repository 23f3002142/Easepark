"""
controllers/api_auth_routes.py
───────────────────────────────
Handles all authentication for the EasePark REST API.

AUTH FLOW OVERVIEW (important for recruiter conversations):
─────────────────────────────────────────────────────────────
The app uses a two-token JWT strategy:

  1. ACCESS TOKEN  (short-lived: 24 hours)
     - Sent in every API request: Authorization: Bearer <token>
     - If stolen, expires quickly → limits damage window
     - Stored in localStorage on the frontend

  2. REFRESH TOKEN (long-lived: 30 days)
     - Used ONLY to get a new access token when the current one expires
     - Never sent to normal endpoints — only to POST /api/auth/refresh
     - Stored separately in localStorage

  3. LOGOUT / REVOCATION
     - JWTs are stateless by design — the server can't "delete" a token.
     - Solution: we maintain a Redis "blocklist" of revoked token JTIs.
     - JTI = JWT ID, a UUID baked into every token. On logout we write
       SETEX blocklist:<jti> "revoked" <remaining_ttl_seconds> in Redis.
     - Every protected endpoint checks the blocklist via the
       @jwt.token_in_blocklist_loader callback in app.py.

ENDPOINTS:
  POST /api/auth/register          – create account, send verification OTP
  POST /api/auth/login             – returns access + refresh tokens
  GET  /api/auth/me                – returns current user profile
  POST /api/auth/logout            – blacklists the current access token
  POST /api/auth/refresh           – exchanges refresh token for new access token
  POST /api/auth/change-password   – change password (requires current password)
  POST /api/auth/forgot-password   – sends reset OTP to email
  POST /api/auth/reset-password    – verifies OTP and sets new password
  POST /api/auth/verify-email      – verifies email with OTP sent at registration
  POST /api/auth/resend-verification – re-sends the email verification OTP
  GET  /api/auth/google-login      – initiates Google OAuth flow
  GET  /api/auth/google-authorize  – OAuth callback, redirects to Vue with token
"""

from flask import request, jsonify, session, url_for, redirect, current_app
from flask_smorest import Blueprint
from utils.logger import logger
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from models.user_model import Users, db
from extensions import oauth, limiter
from utils.email import send_verification_otp, send_password_reset_otp
from utils.validation import validate_schema
from schemas.auth_schemas import (
    SendOtpSchema,
    VerifyRegistrationOtpSchema,
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    ChangePasswordSchema,
)
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import random
import base64
import os

api_auth = Blueprint('api_auth', __name__, url_prefix='/api/v1/auth', description="Authentication Operations")

OTP_EXPIRY_MINUTES = 10


# ── Helpers ──────────────────────────────────────────────────────────────────

def _generate_otp() -> str:
    """6-digit numeric OTP."""
    return str(random.randint(100000, 999999))


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
        "is_verified": user.is_verified,
        "is_oauth": user.password is None or user.password == "",
    }


def _normalized_frontend_url() -> str:
    # FRONTEND_URL may hold a comma-separated list of allowed origins (used for CORS),
    # e.g. "https://easepark.app,https://www.easepark.app". For redirects we need a
    # single, valid URL — so take the first non-empty origin.
    raw = os.getenv("FRONTEND_URL", "http://localhost:5173")
    first = next((o.strip() for o in raw.split(",") if o.strip()), "http://localhost:5173")
    return first.rstrip("/")


def _oauth_error_redirect(message: str):
    return redirect(f"{_normalized_frontend_url()}/login?oauth_error={quote_plus(message)}")


def _generate_unique_username(seed: str) -> str:
    base = (seed or "user").strip().lower()
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


# ── Pre-Registration Email Verification ──────────────────────────────────────

@api_auth.route("/send-verification-otp", methods=["POST"])
@limiter.limit("5 per minute")
@api_auth.arguments(SendOtpSchema, location='json')
@api_auth.response(200, description="Verification OTP sent to your email.")
def send_verification_otp_endpoint(valid_data):
    """
    Sends a verification OTP to an email BEFORE the user account is created.

    NEW FLOW (change #4):
      1. User fills in email on Register page
      2. Clicks "Verify Email" → this endpoint sends OTP
      3. User enters OTP inline on the same page
      4. Frontend sends OTP with the register request
      5. Register endpoint verifies OTP → creates user with is_verified=True

    WHY verify before creating the account?
      - No orphan unverified accounts in the database
      - No separate verification page needed
      - Cleaner UX — everything happens on the register page

    OTP is stored in Redis (ephemeral, auto-expires) rather than in the DB
    because the user doesn't exist yet. Key: "email_otp:<email>" → "<otp>"
    """
    email = valid_data.get("email").strip()

    # Check if email is already taken
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    otp = _generate_otp()

    # Store OTP in Redis with expiry (10 minutes)
    try:
        from cache import redis_client
        if redis_client:
            redis_client.setex(f"email_otp:{email}", OTP_EXPIRY_MINUTES * 60, otp)
        else:
            # Fallback: store in Flask session (less ideal but works without Redis)
            session[f"email_otp:{email}"] = otp
            session[f"email_otp_exp:{email}"] = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
    except Exception:
        session[f"email_otp:{email}"] = otp
        session[f"email_otp_exp:{email}"] = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()

    send_verification_otp(email, otp)
    return jsonify({"message": "Verification OTP sent to your email."}), 200


def _verify_email_otp(email: str, otp: str) -> bool:
    """Check if the provided OTP matches the one stored for this email."""
    try:
        from cache import redis_client
        if redis_client:
            stored = redis_client.get(f"email_otp:{email}")
            if stored:
                if hasattr(stored, "decode"):
                    stored = stored.decode("utf-8")
                if stored == otp:
                    redis_client.delete(f"email_otp:{email}")  # one-time use
                    return True
            return False
    except Exception as e:
        logger.error(f"[OTP Verify] Redis retrieval error: {e}")

    # Fallback: check Flask session
    stored = session.get(f"email_otp:{email}")
    exp_str = session.get(f"email_otp_exp:{email}")
    if stored and stored == otp:
        if exp_str and datetime.utcnow() <= datetime.fromisoformat(exp_str):
            session.pop(f"email_otp:{email}", None)
            session.pop(f"email_otp_exp:{email}", None)
            return True
    return False


def _is_email_verified(email: str) -> bool:
    """Checks if the email has been successfully verified via OTP within the last 15 minutes."""
    try:
        from cache import redis_client
        if redis_client:
            val = redis_client.get(f"email_verified:{email}")
            return val == "true"
    except Exception as e:
        logger.error(f"[Verification Check] Redis read error: {e}")

    # Fallback: check session
    val = session.get(f"email_verified:{email}")
    exp_str = session.get(f"email_verified_exp:{email}")
    if val:
        if exp_str and datetime.utcnow() <= datetime.fromisoformat(exp_str):
            return True
    return False


def _clear_email_verified(email: str):
    """Clears the verified state after successful registration."""
    try:
        from cache import redis_client
        if redis_client:
            redis_client.delete(f"email_verified:{email}")
    except Exception as e:
        logger.error(f"[Verification Clear] Redis delete error: {e}")
    
    session.pop(f"email_verified:{email}", None)
    session.pop(f"email_verified_exp:{email}", None)


# ── Register ─────────────────────────────────────────────────────────────────

@api_auth.route("/verify-registration-otp", methods=["POST"])
@limiter.limit("5 per minute")
@api_auth.arguments(VerifyRegistrationOtpSchema, location='json')
@api_auth.response(200, description="Email verified successfully!")
@api_auth.response(400, description="Invalid or expired OTP.")
def verify_registration_otp(valid_data):
    """
    Verifies the OTP entered inline by the user before creating their account.
    If correct, sets f"email_verified:{email}" to "true" in Redis or session for 15 minutes.
    """
    email = valid_data.get("email").strip()
    otp = valid_data.get("otp").strip()

    if not _verify_email_otp(email, otp):
        return jsonify({"error": "Invalid or expired OTP. Please request a new one."}), 400

    # Store verified status for 15 minutes
    try:
        from cache import redis_client
        if redis_client:
            redis_client.setex(f"email_verified:{email}", 15 * 60, "true")
        else:
            session[f"email_verified:{email}"] = True
            session[f"email_verified_exp:{email}"] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    except Exception as e:
        logger.error(f"[Verification Save] Redis save error: {e}")
        session[f"email_verified:{email}"] = True
        session[f"email_verified_exp:{email}"] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()

    return jsonify({"message": "Email verified successfully!"}), 200


@api_auth.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
@api_auth.arguments(RegisterSchema, location='json')
@api_auth.response(201, description="Registration successful!")
@api_auth.response(400, description="Email not verified first.")
@api_auth.response(409, description="Username or Email already registered.")
def register(valid_data):
    """
    Creates a new user account.

    Checks if the email has been verified via the new verification endpoint.
    If the verification is valid, user is created with is_verified=True immediately.
    No separate verification page needed.
    """
    username = valid_data.get("username").strip()
    email = valid_data.get("email").strip()
    password = valid_data.get("password")

    # Check if the email has been verified
    if not _is_email_verified(email):
        return jsonify({"error": "Email is not verified. Please verify your email first."}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hash_pw = generate_password_hash(password)
    user = Users(
        username=username,      # type: ignore
        email=email,            # type: ignore
        password=hash_pw,       # type: ignore
        role="user",            # type: ignore
        is_verified=True,       # type: ignore  — already verified via inline OTP
    )
    db.session.add(user)

    try:
        db.session.commit()
        _clear_email_verified(email)  # Clear the verification flag upon successful signup
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Registration failed. Please try again."}), 500

    return jsonify({
        "message": "Account created successfully! You can now sign in.",
    }), 201


# ── Email Verification ────────────────────────────────────────────────────────

@api_auth.route("/verify-email", methods=["POST"])
@limiter.limit("10 per minute")
@api_auth.arguments(VerifyRegistrationOtpSchema, location='json')
@api_auth.response(200, description="Email verified successfully! You can now log in.")
def verify_email(valid_data):
    """
    Verifies a user's email with the OTP sent at registration.

    FLOW:
      Register → OTP email → user enters OTP here → is_verified = True → can book
    """
    email = valid_data.get("email").strip()
    otp = valid_data.get("otp").strip()

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email"}), 404

    if user.is_verified:
        return jsonify({"message": "Email is already verified"}), 200

    if not user.email_verification_otp:
        return jsonify({"error": "No pending verification. Request a new OTP."}), 400

    if datetime.utcnow() > user.email_verification_expires_at:
        user.email_verification_otp = None
        user.email_verification_expires_at = None
        db.session.commit()
        return jsonify({"error": "OTP has expired. Please request a new one."}), 400

    if user.email_verification_otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # OTP is valid — mark verified and clear OTP fields
    user.is_verified = True
    user.email_verification_otp = None
    user.email_verification_expires_at = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully! You can now log in."}), 200


@api_auth.route("/resend-verification", methods=["POST"])
@limiter.limit("3 per minute")
@api_auth.arguments(SendOtpSchema, location='json')
@api_auth.response(200, description="Verification OTP resent. Check your inbox.")
def resend_verification(valid_data):
    """Resends the email verification OTP. Rate-limited to prevent email spam."""
    email = valid_data.get("email").strip()

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email"}), 404

    if user.is_verified:
        return jsonify({"message": "Email is already verified"}), 200

    otp = _generate_otp()
    user.email_verification_otp = otp
    user.email_verification_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.session.commit()

    send_verification_otp(email, otp)
    return jsonify({"message": "Verification OTP resent. Check your inbox."}), 200


# ── Login ─────────────────────────────────────────────────────────────────────

@api_auth.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@api_auth.arguments(LoginSchema, location='json')
@api_auth.response(200, description="Login successful, returns tokens.")
def login(valid_data):
    """
    Authenticates a user and returns BOTH an access token and a refresh token.

    WHY two tokens?
      - Access token: short-lived (24h). Used for every API call.
        If someone intercepts it, it expires soon.
      - Refresh token: long-lived (30d). Used ONLY to get a new access token.
        The frontend silently calls /api/auth/refresh when it gets a 401.
        This keeps users logged in across sessions without permanently valid credentials.
    """
    username = valid_data.get("username").strip()
    password = valid_data.get("password")

    from sqlalchemy import or_
    user = Users.query.filter(or_(Users.username == username, Users.email == username)).first()
    if not user or not user.password or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username/email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "token": access_token,          # kept as "token" for backward compat with existing Vue code
        "refresh_token": refresh_token,
        "user": serialize_user(user),
    }), 200


# ── Refresh Token ─────────────────────────────────────────────────────────────

@api_auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)   # ← only accepts refresh tokens, not access tokens
@api_auth.response(200, description="Token refreshed successfully.")
def refresh():
    """
    Issues a new short-lived access token using a valid refresh token.

    FLOW on the frontend:
      1. Any API call returns 401 (access token expired)
      2. Axios interceptor catches it, calls POST /api/auth/refresh with refresh token
      3. Gets back a new access token, retries the original request
      4. User never sees a "session expired" error
    """
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"token": new_access_token}), 200


# ── Logout ────────────────────────────────────────────────────────────────────

@api_auth.route("/logout", methods=["POST"])
@jwt_required()
@api_auth.response(200, description="Logged out successfully")
def logout():
    """
    Revokes the current access token by adding its JTI to the Redis blocklist.

    WHY does logout need Redis if JWTs are stateless?
      JWTs are self-contained — the server can't "delete" one. A blocklist is the
      standard solution: we record the token's unique ID (JTI) in Redis with a TTL
      equal to the token's remaining lifetime. Every request checks this blocklist
      via the @jwt.token_in_blocklist_loader callback in app.py.
      When the TTL expires, Redis auto-deletes the entry — no cleanup needed.
    """
    jti = get_jwt()["jti"]   # JTI = JWT ID, a UUID unique to this specific token
    token_expires = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=24))

    try:
        from cache import redis_client
        if redis_client:
            redis_client.setex(
                f"blocklist:{jti}",
                int(token_expires.total_seconds()),
                "revoked"
            )
    except Exception as e:
        logger.error(f"[Logout] Redis blocklist write failed: {e}")
        # We still return 200 — the frontend clears its tokens regardless.
        # The access token will naturally expire in ≤24h even without blocklisting.

    return jsonify({"message": "Logged out successfully"}), 200


# ── Profile ───────────────────────────────────────────────────────────────────

@api_auth.route("/me", methods=["GET"])
@jwt_required()
@api_auth.response(200, description="Current user profile returned.")
def me():
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": serialize_user(user)}), 200


# ── Change Password ───────────────────────────────────────────────────────────

@api_auth.route("/change-password", methods=["POST"])
@jwt_required()
@api_auth.arguments(ChangePasswordSchema, location='json')
@api_auth.response(200, description="Password changed successfully")
def change_password(valid_data):
    user_id = get_jwt_identity()
    user = db.session.get(Users, int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_password = valid_data.get("current_password")
    new_password = valid_data.get("new_password")
    confirm_password = valid_data.get("confirm_password")

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


# ── Forgot Password ───────────────────────────────────────────────────────────

@api_auth.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
@api_auth.arguments(ForgotPasswordSchema, location='json')
@api_auth.response(200, description="A password reset OTP has been sent to your email.")
def forgot_password(valid_data):
    """
    Step 1 of password reset: send a 6-digit OTP to the user's registered email.
    Checks if the email exists in the database and returns a 404 if not found.
    """
    email = valid_data.get("email").strip()

    user = Users.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "No account found with this email address."}), 404

    # Google OAuth user (no password set) — tell them to use Google instead
    if not user.password:
        return jsonify({
            "error": "This account was created using Google Sign-In. Please use 'Sign in with Google' instead.",
            "oauth_account": True,
        }), 400

    otp = _generate_otp()
    user.password_reset_otp = otp
    user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.session.commit()
    send_password_reset_otp(email, otp)

    return jsonify({
        "message": "A password reset OTP has been sent to your email."
    }), 200


@api_auth.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
@api_auth.arguments(ResetPasswordSchema, location='json')
@api_auth.response(200, description="Password reset successfully. You can now log in.")
def reset_password(valid_data):
    """
    Step 2 of password reset: verify the OTP and set the new password.

    After success, the OTP fields are cleared so the link can't be reused.
    """
    email = valid_data.get("email").strip()
    otp = valid_data.get("otp").strip()
    new_password = valid_data.get("new_password")

    user = Users.query.filter_by(email=email).first()
    if not user or not user.password_reset_otp:
        return jsonify({"error": "Invalid or expired OTP"}), 400

    if datetime.utcnow() > user.password_reset_expires_at:
        user.password_reset_otp = None
        user.password_reset_expires_at = None
        db.session.commit()
        return jsonify({"error": "OTP has expired. Please request a new one."}), 400

    if user.password_reset_otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # OTP valid — update password and clear reset fields
    user.password = generate_password_hash(new_password)
    user.password_reset_otp = None
    user.password_reset_expires_at = None
    db.session.commit()

    return jsonify({"message": "Password reset successfully. You can now log in."}), 200


# ── Google OAuth ──────────────────────────────────────────────────────────────

@api_auth.route("/google-login", methods=["GET"])
@api_auth.response(302, description="Redirects to Google OAuth authorization.")
def google_login():
    base_url = os.getenv("BASE_URL")
    if not base_url:
        base_url = request.host_url.rstrip("/")
    else:
        base_url = base_url.rstrip("/")
    redirect_uri = f"{base_url}{url_for('api_auth.google_authorize')}"
    nonce = base64.urlsafe_b64encode(os.urandom(16)).decode()
    session["nonce"] = nonce
    return oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])  # type: ignore


@api_auth.route("/google-authorize", methods=["GET"])
@api_auth.response(302, description="Redirects to Vue frontend callback URL.")
def google_authorize():
    """
    Google OAuth callback.

    Google-authenticated users are automatically marked as is_verified=True
    because Google has already confirmed they own the email address.
    This is a standard assumption — Gmail, GitHub, etc. all do the same.
    """
    try:
        token = oauth.google.authorize_access_token()  # type: ignore
        nonce = session.pop("nonce", None)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)  # type: ignore
    except Exception as e:
        # Log the real cause so OAuth failures are diagnosable in the server logs
        # (common culprits: redirect_uri/scope mismatch, lost session nonce/state,
        # or an invalid GOOGLE_CLIENT_ID/SECRET).
        logger.error(f"[oauth] Google sign-in failed: {type(e).__name__}: {e}")
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
            email=email,            # type: ignore
            username=username,      # type: ignore
            full_name=full_name or username,  # type: ignore
            password=None,          # type: ignore  — no password for OAuth users
            role="user",            # type: ignore
            is_verified=True,       # type: ignore  — Google already verified the email
        )
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return _oauth_error_redirect("Could not complete Google sign-in. Please try again.")
    elif not user.is_verified:
        # Existing user who registered manually but never verified —
        # Google just proved the email is real, so we verify them now.
        user.is_verified = True
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # Pass both tokens to the Vue frontend via query params
    return redirect(
        f"{_normalized_frontend_url()}/auth/callback"
        f"?token={access_token}&refresh_token={refresh_token}"
    )
