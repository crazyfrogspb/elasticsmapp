from functools import wraps

from flask import Response, request, session
from flask_user import UserManager

from app.app import app, db
from app.models import User

user_manager = UserManager(app, db, User)


def custom_login(username, password, roles_accepted=None, users_accepted=None):
    user = user_manager.db_manager.find_user_by_username(username)

    if user is None:
        return False

    if not user_manager.verify_password(password, user.password):
        return False

    if roles_accepted or users_accepted:
        if roles_accepted:
            for role in user.roles:
                if role.name in roles_accepted:
                    return True

        if users_accepted:
            if user.username in users_accepted:
                return True

        return False

    return True


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not custom_login(auth.username, auth.password, roles_accepted=['admin', 'user']):
            return authenticate()
        session['username'] = auth.username
        return f(*args, **kwargs)
    return decorated
