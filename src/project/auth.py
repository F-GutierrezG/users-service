from functools import wraps
from flask import request, jsonify
from project.models import User
from project.serializers import TokenSerializer, InvalidToken, ExpiredToken


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


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = parse_token(request)

        if token is False:
            return forbidden()

        try:
            payload = TokenSerializer.decode(token)
            user = User.query.filter_by(id=payload['sub'], active=True).first()

            if user:
                return f(user, *args, **kwargs)
        except InvalidToken:
            return forbidden('invalid token.')
        except ExpiredToken:
            return forbidden('expired token.')

        return forbidden()
    return decorated_function
