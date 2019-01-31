import random
import string

from project import db

from project.models import User, Group, Permission
from project.serializers import TokenSerializer


def add_permission(code=None):
    if code is None:
        code = random_string()
    permission = Permission(code=code, name=random_string())
    db.session.add(permission)
    db.session.commit()

    return permission


def add_group():
    group = Group(name=random_string())
    db.session.add(group)
    db.session.commit()

    return group


def add_user(admin=False):
    user = User(
        first_name=random_string(),
        last_name=random_string(),
        email="{}@test.com".format(random_string()).lower(),
        password=random_string(32),
        admin=admin)
    db.session.add(user)
    db.session.commit()
    return user


def add_admin():
    admin = add_user(admin=True)
    add_permissions(admin, ['LIST_USERS'])
    return admin


def login_user(user):
    return TokenSerializer.encode(user).decode()


def add_permission_to_group(permission, group):
    group.permissions.append(permission)
    db.session.add(group)
    db.session.commit()


def add_user_to_group(user, group):
    group.users.append(user)
    db.session.add(group)
    db.session.commit()


def add_permissions(user, permissions):
    group = add_group()
    for permission in permissions:
        permission = add_permission(code=permission)
        add_permission_to_group(permission, group)
    add_user_to_group(user, group)


def random_string(length=32):
    return ''.join(
        [random.choice(
            string.ascii_letters + string.digits
        ) for n in range(length)]
    )
