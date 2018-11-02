def validate(validation_class):
    def decorator(function):
        def wrapper(*args, **kwargs):
            validation_class().validate(args[1])
            return function(*args, **kwargs)
        return wrapper
    return decorator
