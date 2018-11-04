import json
import random
import string

from project.logics import UserLogics


def random_string(length=32):
    return ''.join(
        [random.choice(
            string.ascii_letters + string.digits
        ) for n in range(length)]
    )


class LoginMixin:
    def add(self, email, password):
        return UserLogics().create({
            'first_name': random_string(32),
            'last_name': random_string(32),
            'email': email,
            'password': password
        })

    def login(self, email, password):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': email,
                    'password': password
                }),
                content_type='application/json'
            )
            return json.loads(response.data.decode())

    def add_and_login(self, email=None, password=None):
        if email is None:
            email = '{}@test.com'.format(random_string(16))

        if password is None:
            password = random_string(32)

        self.add(email=email, password=password)
        return self.login(email=email, password=password)
