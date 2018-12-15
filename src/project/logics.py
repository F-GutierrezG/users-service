from project.validators.decorators import validate
from project.serializers import (
    UserSerializer, GroupSerializer, PermissionSerializer, TokenSerializer)
from project.validations import (
    CreateUserValidator, UpdateUserValidator, LoginValidator)
from project.models import User, Group, Permission
from project import db, bcrypt


class DoesNotExist(Exception):
    pass


class UserLogics:
    def list(self):
        users = User.query.filter_by(active=True)

        return UserSerializer.to_array(users)

    def get(self, id):
        user = User.query.filter_by(id=id, active=True).first()

        if not user:
            raise DoesNotExist

        return UserSerializer.to_dict(user)

    @validate(CreateUserValidator)
    def create(self, data):
        user = User(**data)

        db.session.add(user)
        db.session.commit()

        return UserSerializer.to_dict(user)

    @validate(UpdateUserValidator)
    def update(self, data, id):
        User.query.filter_by(id=id, active=True).update(data)
        db.session.commit()

        return self.get(id)

    def delete(self, id, deleted_by):
        self.get(id)

        User.query.filter_by(id=id, active=True).update({
            'active': False,
            'updated_by': deleted_by.id
        })
        db.session.commit()

    def filter_by_ids(self, ids):
        users = User.query.filter(User.id.in_(ids)).filter_by(active=True)

        return UserSerializer.to_array(users)


class GroupLogics:
    def get(self, id):
        group = Group.query.filter_by(id=id).first()

        if not group:
            raise DoesNotExist

        return GroupSerializer.to_dict(group)

    def list(self):
        groups = Group.query.all()

        return GroupSerializer.to_array(groups)

    def create(self, data):
        group = Group(**data)

        db.session.add(group)
        db.session.commit()

        return GroupSerializer.to_dict(group)

    def update(self, data, id):
        Group.query.filter_by(id=id).update(data)
        db.session.commit()

        return self.get(id)

    def delete(self, id):
        group = Group.query.filter_by(id=id).first()

        db.session.delete(group)
        db.session.commit()

    def users(self, id):
        users = Group.query.filter_by(id=id).first().users

        return UserSerializer.to_array(users)

    def add_user(self, data, id):
        group = Group.query.filter_by(id=id).first()
        user = User.query.filter_by(id=data['id']).first()

        group.users.append(user)

        db.session.add(group)
        db.session.commit()

        return UserSerializer.to_array(group.users)

    def delete_user(self, user_id, id):
        group = Group.query.filter_by(id=id).first()
        user = User.query.filter_by(id=user_id).first()

        group.users.remove(user)

        db.session.add(group)
        db.session.commit()

        return UserSerializer.to_array(group.users)


class PermissionLogics:
    def list(self):
        permissions = Permission.query.all()

        return PermissionSerializer.to_array(permissions)


class AuthLogics:
    @validate(LoginValidator)
    def login(self, data):
        user = User.query.filter_by(email=data['email'], active=True).first()

        if not user:
            raise DoesNotExist

        password = data['password']
        if bcrypt.check_password_hash(user.password, password) is False:
            return False

        return TokenSerializer.encode(user).decode()

    def get_status(self, user):
        return UserSerializer.to_dict(user)
