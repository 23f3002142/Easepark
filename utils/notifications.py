from models import db
from models.user_model import Notification


def notify(user_id: int, title: str, message: str, type: str = 'info'):
    """Create a notification for a user."""
    n = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
    )  # type: ignore
    db.session.add(n)
    db.session.commit()
    return n
