class UserSerializer:
    @staticmethod
    def to_dict(user):
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'active': user.active
        }

    @staticmethod
    def to_array(users):
        users_list = []

        for user in users:
            users_list.append(UserSerializer.to_dict(user))

        return users_list
