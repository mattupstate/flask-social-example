
from functools import wraps

from flask import Response, current_app, request


def check_auth(username, password):
    creds = current_app.config['ADMIN_CREDENTIALS'].split(',')
    return username == creds[0] and password == creds[1]


def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
