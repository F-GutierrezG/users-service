from project.validators.exceptions import ValidationRuleException


class Required:
    def __init__(self, message=None):
        self.message = message

    def __get_message(self, field):
        if self.message is None:
            return '{} is required.'.format(field.replace('_', ' '))
        else:
            return self.message

    def validate(self, field, data):
        if field not in data:
            raise ValidationRuleException(self.__get_message(field))
