class ValidationRuleException(Exception):
    def __init__(self, message):
        self.message = message


class ValidatorException(Exception):
    def __init__(self, errors):
        self.errors = errors
