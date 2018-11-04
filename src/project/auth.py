from functools import wraps
from flask import request, jsonify
from project.models import User
from project.serializers import TokenSerializer, InvalidToken


def forbidden():
    return jsonify({'message': 'forbidden.'}), 403


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return forbidden()

        token_parts = auth_header.split(' ')

        if len(token_parts) != 2:
            return forbidden()

        token = token_parts[1]

        try:
            payload = TokenSerializer.decode(token)
            user = User.query.filter_by(id=payload['sub'], active=True).first()

            if not user:
                return forbidden()
        except InvalidToken:
            return forbidden()

        return f(*args, **kwargs)
    return decorated_function
