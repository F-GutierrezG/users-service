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
            'active': user.status,
            'expiration': str(user.expiration) if user.expiration else None,
            'created': str(user.created),
            'created_by': user.created_by,
            'updated': str(user.updated),
            'updated_by': user.updated_by,
            'hash': user.hash,
            'admin': user.admin,
            'group_id': user.groups[0].id if len(user.groups) > 0 else ""
        }

    @staticmethod
    def to_array(users):
        return list(map(lambda user: UserSerializer.to_dict(user), users))


class GroupSerializer:
    @staticmethod
    def to_dict(group):
        return {
            'id': group.id,
            'name': group.name
        }

    @staticmethod
    def to_array(groups):
        return list(map(lambda group: GroupSerializer.to_dict(group), groups))


class PermissionSerializer:
    @staticmethod
    def to_dict(permission):
        return {
            'code': permission.code,
            'name': permission.name
        }

    @staticmethod
    def to_array(permissions):
        return list(
            map(
                lambda permission: PermissionSerializer.to_dict(permission),
                permissions))


class InvalidToken(Exception):
    pass


class ExpiredToken(Exception):
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
            'sub': user.id,
            'admin': user.admin
        }
        return jwt.encode(payload, secret, algorithm='HS256')

    @staticmethod
    def decode(token):
        secret = current_app.config.get('SECRET_KEY')
        try:
            return jwt.decode(token, secret)
        except jwt.exceptions.DecodeError:
            raise InvalidToken
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredToken
