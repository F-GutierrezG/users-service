from project.validators import BaseValidator
from project.validators import rules
from project.models import User


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
