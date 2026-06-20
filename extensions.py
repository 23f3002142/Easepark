from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_cors import CORS

mail = Mail()
jwt = JWTManager()
cors = CORS()


# Rate-limiter: key by authenticated user ID (from JWT) or fall back to IP
def rate_limit_key():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except Exception:
        pass
    return get_remote_address()


limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=["200 per hour"]
)

oauth = OAuth()
