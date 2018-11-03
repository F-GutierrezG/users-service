from project.validators import BaseValidator
from project.validators.decorators import validate
from project.validators import rules
from project.serializers import UserSerializer

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


class DoesNotExist(Exception):
    pass


class UserLogics:
    @validate(CreateUserValidator)
    def create(self, data):
        user = User(**data)

        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return UserSerializer.to_dict(user)

    @validate(UpdateUserValidator)
    def update(self, data, id):
        User.query.filter(User.id == id).update(data)
        db.session.commit()

        user = User.query.get(id)

        if not user:
            raise DoesNotExist

        return UserSerializer.to_dict(user)

    def delete(self, id):
        user = User.query.get(id)

        if not user:
            raise DoesNotExist

        User.query.filter(User.id == id).update({'active': False})
        db.session.commit()
