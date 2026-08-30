from collections.abc import Callable

from app.modules.identity.models import User


class UserNotFoundError(LookupError):
    pass


def lookup_user(user_id: int, load_user: Callable[[int], User | None]) -> User:
    """Look up a user without coupling the service to SQLAlchemy or FastAPI."""
    user = load_user(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user
