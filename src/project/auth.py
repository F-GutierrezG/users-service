from functools import wraps
from flask import request, jsonify
from project.models import User
from project.serializers import TokenSerializer, InvalidToken


def forbidden():
    return jsonify({'message': 'forbidden.'}), 403


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

            if not user:
                return forbidden()
        except InvalidToken:
            return forbidden()

        return f(*args, **kwargs)
    return decorated_function
