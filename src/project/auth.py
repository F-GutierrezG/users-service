from functools import wraps
from flask import request, jsonify
from project.models import User
from project.serializers import TokenSerializer, InvalidToken, ExpiredToken


def unauthorized(message='unauthorized'):
    return jsonify({'message': message}), 401


def forbidden(message='forbidden'):
    return jsonify({'message': message}), 403


def parse_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return False

    token_parts = auth_header.split(' ')

    if len(token_parts) != 2:
        return False

    return token_parts[1]


def do_authentication():
    token = parse_token(request)

    if token is False:
        return unauthorized()

    try:
        payload = TokenSerializer.decode(token)
        user = User.query.filter_by(id=payload['sub']).first()

        if user is None or user.active is False:
            return forbidden()

        if user:
            return user
    except InvalidToken:
        return unauthorized('invalid token.')
    except ExpiredToken:
        return unauthorized('expired token.')

    return unauthorized()


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = do_authentication()
        if isinstance(response, User):
            return f(response, *args, **kwargs)
        return response
    return decorated_function


def authorize(required_permissions=[]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = do_authentication()
            if isinstance(response, User):
                if response.is_authorized(required_permissions):
                    return f(response, *args, **kwargs)
                return forbidden()
            return response
        return decorated_function
    return decorator
