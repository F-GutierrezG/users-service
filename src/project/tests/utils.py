import json
import random
import string

from project import db
from project.logics import UserLogics

from project.models import User, Group, Permission


def add_permission():
    permission = Permission(code=random_string(), name=random_string())
    db.session.add(permission)
    db.session.commit()

    return permission


def add_group():
    group = Group(name=random_string())
    db.session.add(group)
    db.session.commit()

    return group


def add_user():
    user = User(
        first_name=random_string(),
        last_name=random_string(),
        email="{}@test.com".format(random_string()),
        password=random_string(32))
    db.session.add(user)
    db.session.commit()
    return user


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
