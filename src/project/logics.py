from project.validators import BaseValidator
from project.validators.decorators import validate
from project.validators import rules
from project.serializers import UserSerializer, TokenSerializer

from project.models import User
from project import db


class UpdateUserValidator(BaseValidator):
    def get_rules(self):
        return {
            'first_name': [
                rules.Required(),
                rules.Length(max=User.FIRST_NAME_MAX_LENGTH)
            ],
            'last_name': [
                rules.Required(),
                rules.Length(max=User.LAST_NAME_MAX_LENGTH)
            ],
            'email': [rules.Required()],
        }


class CreateUserValidator(UpdateUserValidator):
    def get_rules(self):
        new_rules = super().get_rules()

        new_rules['password'] = [rules.Required()]

        return new_rules


class LoginValidator(BaseValidator):
    def get_rules(self):
        return {
            'email': [rules.Required()],
            'password': [rules.Required()]
        }


class DoesNotExist(Exception):
    pass


class UserLogics:
    def list(self):
        users = User.query.filter_by(active=True)

        return UserSerializer.to_array(users)

    def get(self, id):
        user = User.query.filter_by(id=id, active=True).first()

        if not user:
            raise DoesNotExist

        return UserSerializer.to_dict(user)

    @validate(CreateUserValidator)
    def create(self, data):
        user = User(**data)

        db.session.add(user)
        db.session.commit()

        return UserSerializer.to_dict(user)

    @validate(UpdateUserValidator)
    def update(self, data, id):
        User.query.filter_by(id=id, active=True).update(data)
        db.session.commit()

        return self.get(id)

    def delete(self, id):
        self.get(id)

        User.query.filter_by(id=id, active=True).update({'active': False})
        db.session.commit()


class AuthLogics:
    @validate(LoginValidator)
    def login(self, data):
        user = User.query.filter_by(email=data['email'], active=True).first()

        if not user:
            raise DoesNotExist

        return TokenSerializer.encode(user).decode()

    def status(self, token):
        user_id = TokenSerializer.decode(token)['sub']

        return UserLogics().get(user_id)
