import os
import jwt
import datetime

from flask import current_app

from project.validators.decorators import validate
from project.serializers import (
    UserSerializer, GroupSerializer, PermissionSerializer, TokenSerializer)
from project.validations import (
    CreateUserValidator, UpdateUserValidator, LoginValidator)
from project.models import User, Group, Permission
from project import db, bcrypt
from mailer_service.factories import MailerServiceFactory


class NotFound(Exception):
    pass


class Unauthorized(Exception):
    pass


class UserLogics:
    def list(self):
        users = User.query.order_by(User.id.asc()).all()

        return UserSerializer.to_array(users)

    def list_admins(self):
        users = User.query.filter_by(admin=True).order_by(User.id.asc())

        return UserSerializer.to_array(users)

    def get(self, id):
        user = User.query.filter_by(id=id).first()

        if not user:
            raise NotFound

        return UserSerializer.to_dict(user)

    @validate(CreateUserValidator)
    def create(self, data, user):
        if 'admin' in data and data['admin'] is True and user.admin is False:
            raise Unauthorized

        data['created_by'] = user.id
        data['email'] = data['email'].lower()
        group_id = data['group_id']

        del data['group_id']

        user = User(**data)

        db.session.add(user)
        db.session.commit()

        self.__add_user_to_group(user.id, group_id)

        return UserSerializer.to_dict(user)

    @validate(CreateUserValidator)
    def create_admin(self, data, user):
        if user.admin is False:
            raise Unauthorized

        data['created_by'] = user.id
        data['admin'] = True
        data['email'] = data['email'].lower()
        group_id = data['group_id']

        del data['group_id']

        user = User(**data)

        db.session.add(user)
        db.session.commit()

        self.__add_user_to_group(user.id, group_id)

        return UserSerializer.to_dict(user)

    @validate(UpdateUserValidator)
    def update(self, data, id):
        if 'expiration' in data and data['expiration'] is not None \
                and data['expiration'].strip() == '':
            data['expiration'] = None

        self.__add_user_to_group(id, data['group_id'])

        data['email'] = data['email'].lower()
        del data['group_id']

        User.query.filter_by(id=id).update(data)
        db.session.commit()

        return self.get(id)

    def deactivate(self, id, updated_by):
        User.query.filter_by(id=id).update({
            'active': False,
            'updated_by': updated_by.id
        })
        db.session.commit()

        return self.get(id)

    def activate(self, id, updated_by):
        User.query.filter_by(id=id).update({
            'active': True,
            'updated_by': updated_by.id
        })
        db.session.commit()

        return self.get(id)

    def filter_by_ids(self, ids):
        users = User.query.filter(User.id.in_(ids)).order_by(User.id.asc())

        return UserSerializer.to_array(users)

    def change_password(self, user_data, id, user):
        user = User.query.filter_by(id=id).first()

        if user is None:
            raise NotFound()

        user.updated_by = user.id
        user.password = user.generate_password_hash(
            password=user_data['password'])

        db.session.add(user)
        db.session.commit()

    def __add_user_to_group(self, user_id, group_id):
        user = User.query.filter_by(id=user_id).first()
        group = Group.query.filter_by(id=group_id).first()

        if user is None:
            raise NotFound("user not found")

        if group is None:
            raise NotFound("group not found")

        user.groups.clear()

        user.groups.append(group)

        db.session.add(user)
        db.session.commit()


class GroupLogics:
    def get(self, id):
        group = Group.query.filter_by(id=id).first()

        if not group:
            raise NotFound

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

    def permissions(self, id):
        permissions = Group.query.filter_by(id=id).first().permissions

        return PermissionSerializer.to_array(permissions)

    def add_permission(self, data, id):
        group = Group.query.filter_by(id=id).first()
        permission = Permission.query.filter_by(code=data['code']).first()

        group.permissions.append(permission)

        db.session.add(group)
        db.session.commit()

        return PermissionSerializer.to_array(group.permissions)

    def delete_permission(self, code, id):
        group = Group.query.filter_by(id=id).first()
        permission = Permission.query.filter_by(code=code).first()

        group.permissions.remove(permission)

        db.session.add(group)
        db.session.commit()

        return PermissionSerializer.to_array(group.permissions)


class PermissionLogics:
    def list(self):
        permissions = Permission.query.all()

        return PermissionSerializer.to_array(permissions)


class AuthLogics:
    EMAIL_FROM = "recovery@onelike.cl"
    EMAIL_SUBJECT = "Recuperación de contraseña"

    @validate(LoginValidator)
    def login(self, data):
        user = User.query.filter_by(
            email=data['email'].lower(), active=True).first()

        if not user:
            raise NotFound

        password = data['password']
        if bcrypt.check_password_hash(user.password, password) is False:
            return False

        return TokenSerializer.encode(user).decode()

    def get_status(self, user):
        serialized_user = UserSerializer.to_dict(user)
        serialized_user['permissions'] = user.permissions

        return serialized_user

    def recover_password(self, email):
        user = User.query.filter_by(email=email, active=True).first()

        if not user or (
                user.expiration and user.expiration <= datetime.date.today()):
            raise NotFound
        service = MailerServiceFactory.get_instance()
        email_to = [email]
        email_from = self.EMAIL_FROM
        email_subject = self.EMAIL_SUBJECT
        email_body = self.__create_recover_password_email(
            email, user.full_name)

        service.send(
            recipients=email_to,
            sender=email_from,
            subject=email_subject,
            message=email_body)

    def change_password(self, data):
        token = data['token']
        password = data['password']

        token_data = TokenSerializer.decode(token)

        email = token_data['sub']

        user = User.query.filter_by(email=email, active=True).first()
        user.password = user.generate_password_hash(
            password=password)

        db.session.add(user)
        db.session.commit()

    def __create_recover_password_email(self, email, name):
        token = self.__generate_token(email)
        recover_url = current_app.config.get('CHANGE_PASSWORD_URL')

        with open(os.path.join(
                current_app.root_path,
                'templates',
                'recover_password.html'), 'r') as template:
            html = template.read().format(name, recover_url, token)

        return html

    def __generate_token(self, email):
        secret = current_app.config.get('SECRET_KEY')
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                hours=current_app.config.get('RECOVER_TOKEN_EXPIRATION_HOURS'),
            ),
            'iat': datetime.datetime.utcnow(),
            'sub': email,
        }
        return jwt.encode(payload, secret, algorithm='HS256').decode()
