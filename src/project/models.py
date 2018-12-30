import uuid
import datetime

from flask import current_app
from sqlalchemy.sql import func

from project import db, bcrypt


metadata = db.metadata
metadata.schema = 'users'

group_users = db.Table(
    'group_users',
    metadata,
    db.Column(
        'group_id',
        db.Integer,
        db.ForeignKey('users.groups.id'),
        primary_key=True),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.users.id'),
        primary_key=True)
)


group_permissions = db.Table(
    'group_permissions',
    metadata,
    db.Column(
        'group_id',
        db.Integer,
        db.ForeignKey('users.groups.id'),
        primary_key=True),
    db.Column(
        'permission_id',
        db.Integer,
        db.ForeignKey('users.permissions.id'),
        primary_key=True)
)


class User(db.Model):
    FIRST_NAME_MAX_LENGTH = 128
    LAST_NAME_MAX_LENGTH = 128

    __tablename__ = 'users'
    __table_args__ = {'schema': 'users'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(FIRST_NAME_MAX_LENGTH), nullable=False)
    last_name = db.Column(db.String(LAST_NAME_MAX_LENGTH), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    expiration = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=func.now(), nullable=False)
    created_by = db.Column(db.Integer, default=0, nullable=False)
    updated = db.Column(db.DateTime, onupdate=func.now(), nullable=True)
    updated_by = db.Column(db.Integer)
    hash = db.Column(db.String(32), default=uuid.uuid4().hex, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    groups = db.relationship('Group', secondary=group_users)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = self._generate_password_hash(**kwargs)

    def _generate_password_hash(self, **kwargs):
        if 'password' not in kwargs:
            return None

        return bcrypt.generate_password_hash(
            kwargs['password'],
            current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    @property
    def permissions(self):
        permissions = set()
        for group in self.groups:
            for permission in group.permissions:
                permissions.add(permission.code)
        return list(permissions)

    @property
    def status(self):
        if self.active is False:
            return False

        if self.expiration is None:
            return self.active

        return datetime.datetime.now() < self.expiration

    @status.setter
    def status(self, value):
        self.active = value

    def is_authorized(self, required_permissions):
        if self.admin:
            return True

        for permission in required_permissions:
            if permission not in self.permissions:
                return False
        return True


class Permission(db.Model):
    CODE_MAX_LENGTH = 128
    NAME_MAX_LENGTH = 128

    __tablename__ = 'permissions'
    __table_args__ = {'schema': 'users'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(CODE_MAX_LENGTH), nullable=False, unique=True)
    name = db.Column(db.String(NAME_MAX_LENGTH), nullable=False)
    groups = db.relationship('Group', secondary=group_permissions)


class Group(db.Model):
    NAME_MAX_LENGTH = 128

    __tablename__ = 'groups'
    __table_args__ = {'schema': 'users'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(NAME_MAX_LENGTH), nullable=False)
    users = db.relationship(User, secondary=group_users)
    permissions = db.relationship(Permission, secondary=group_permissions)
