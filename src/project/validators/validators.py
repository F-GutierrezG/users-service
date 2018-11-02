from project.validators.exceptions import ValidationRuleException
from project.validators.exceptions import ValidatorException


class BaseValidator:
    def __init__(self):
        self.valid = True
        self.errors = {}

    def execute_validation(self, rule, field, data):
        rule.validate(field, data)

    def validate(self, data):
        rules = self.get_rules()
        for field in rules:
            try:
                for rule in rules[field]:
                    self.execute_validation(rule, field, data)
            except ValidationRuleException as e:
                self.errors[field] = e.message
                self.valid = False

        if self.valid is False:
            raise ValidatorException(self.errors)
