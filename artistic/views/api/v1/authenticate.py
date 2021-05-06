from flask import g, redirect, request, url_for
from functools import wraps
import os

TOKEN = os.getenv('API_TOKEN')


def authenticate_by_token(func):
    @wraps(func)
    def authenticate(*args, **kwargs):
        if 'Token' not in request.headers or request.headers['Token'] != TOKEN:
            return {'unauthorized': 'Token invalid'}, 401
        return func(*args, **kwargs)
    return authenticate
