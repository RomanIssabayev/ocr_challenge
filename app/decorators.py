from flask_login import current_user
from flask import request, redirect, url_for, jsonify, abort
from functools import wraps
from .models import User
import logging

# class CustomLogFilter(logging.Filter):
#     def filter(self, record):
#         if 'GET /' in record.getMessage() or 'POST /' in record.getMessage():
#             return False
#         return True
#
# logging.basicConfig(filename='access.log', level=logging.INFO, format='%(asctime)s - %(message)s')

logger = logging.getLogger()

# logger.addFilter(CustomLogFilter())
#
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

def log_access(user, endpoint):
    logger.info(f"User: {user}, Endpoint: {endpoint}")

def access_required(level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.access_level < level:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            log_access(current_user.username, request.endpoint)
            return f(*args, **kwargs)
        return redirect(url_for('login.index'))
    return decorated_function