import jwt
import datetime
from flask import current_app


class UserSerializer:
    @staticmethod
    def to_dict(user):
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'active': user.active
        }

    @staticmethod
    def to_array(users):
        users_list = []

        for user in users:
            users_list.append(UserSerializer.to_dict(user))

        return users_list


class InvalidToken(Exception):
    pass


class TokenSerializer:
    @staticmethod
    def encode(user):
        secret = current_app.config.get('SECRET_KEY')
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
            ),
            'iat': datetime.datetime.utcnow(),
            'sub': user.id
        }
        return jwt.encode(payload, secret, algorithm='HS256')

    @staticmethod
    def decode(token):
        secret = current_app.config.get('SECRET_KEY')
        try:
            return jwt.decode(token, secret)
        except jwt.exceptions.DecodeError:
            raise InvalidToken
