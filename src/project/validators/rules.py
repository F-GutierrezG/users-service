from project.validators.exceptions import ValidationRuleException


class Required:
    def __init__(self, message=None):
        self.message = message

    def __get_message(self, field):
        cleaned_field = field.replace('_', ' ')

        if self.message is None:
            return '{} is required.'.format(cleaned_field)

        return self.message.format(cleaned_field)

    def validate(self, field, data):
        if field not in data:
            raise ValidationRuleException(self.__get_message(field))

        elif data[field] is None:
            raise ValidationRuleException(self.__get_message(field))

        elif data[field].strip() is '':
            raise ValidationRuleException(self.__get_message(field))


class Length:
    def __init__(self, min=-1, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __get_message(self, field):
        cleaned_field = field.replace('_', ' ')

        if self.message is None and self.min == -1 and self.max is not None:
            return '{} must be less or equal than {} characters long.'.format(
                cleaned_field, self.max)

        return self.message.format(cleaned_field, self.max)

    def validate(self, field, data):
        if self.min == -1 and self.max is not None:
            if len(data[field]) > self.max:
                raise ValidationRuleException(self.__get_message(field))
