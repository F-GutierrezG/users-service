from project.validators.exceptions import ValidationRuleException


class Required:
    def __init__(self, message=None):
        self.message = message

    def __get_message(self, field):
        if self.message is None:
            return '{} is required.'.format(field.replace('_', ' '))

        return self.message

    def validate(self, field, data):
        if field not in data:
            raise ValidationRuleException(self.__get_message(field))


class Length:
    def __init__(self, min=0, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __get_message(self, field):
        if self.message is None and self.min == 0 and self.max is not None:
            return '{} must be less or equal than {} characters long.'.format(
                field.replace('_', ' '), self.max)

        return self.message

    def validate(self, field, data):
        if self.min == 0 and self.max is not None:
            if len(data[field]) > self.max:
                raise ValidationRuleException(self.__get_message(field))
