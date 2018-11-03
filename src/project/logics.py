from project.validators import BaseValidator
from project.validators.decorators import validate
from project.validators import rules
from project.serializers import UserSerializer

from project.models import User
from project import db

from sqlalchemy.sql.expression import true


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
    def list(self):
        users = User.query.filter(User.active == true())

        return UserSerializer.to_array(users)

    def get(self, id):
        user = User.query.filter(User.id == id, User.active == true()).first()

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
        User.query.filter(
            User.id == id, User.active == true()).update(data)
        db.session.commit()

        return self.get(id)

    def delete(self, id):
        self.get(id)

        User.query.filter(
            User.id == id, User.active == true()).update({'active': False})
        db.session.commit()
