from project.validators import BaseValidator
from project.validators.decorators import validate
from project.validators import rules

from project.models import User
from project import db


class CreateUserValidator(BaseValidator):
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
            'password': [rules.Required()],
        }


class UserLogics:
    @validate(CreateUserValidator)
    def create(self, data):
        user = User(**data)

        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return user
