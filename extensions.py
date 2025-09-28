
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
from authlib.integrations.flask_client import OAuth

login_manager = LoginManager()
mail = Mail()


#Rate-limiter(for server overload)
def rate_limit_key():
    if current_user.is_authenticated:
        return str(current_user.id)
    return get_remote_address()

limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=["200 per hour"]
)

oauth = OAuth() 

