class UserSerializer:
    @staticmethod
    def to_dict(user):
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'active': user.active
        }
