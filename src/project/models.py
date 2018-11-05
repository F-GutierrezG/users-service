from flask import current_app
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from project import db, bcrypt


Base = declarative_base()


company_has_users = db.Table(
    'company_has_users',
    db.Model.metadata,
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Company(db.Model):
    NAME_MAX_LENGTH = 128

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(NAME_MAX_LENGTH), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    users = db.relationship("User", secondary=company_has_users)


class User(db.Model):
    FIRST_NAME_MAX_LENGTH = 128
    LAST_NAME_MAX_LENGTH = 128

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(FIRST_NAME_MAX_LENGTH), nullable=False)
    last_name = db.Column(db.String(LAST_NAME_MAX_LENGTH), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime, default=func.now(), nullable=False)
    created_by = db.Column(db.Integer, default=0, nullable=False)
    updated = db.Column(db.DateTime, onupdate=func.now(), nullable=True)
    updated_by = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = self._generate_password_hash(**kwargs)

    def _generate_password_hash(self, **kwargs):
        if 'password' not in kwargs:
            return None

        return bcrypt.generate_password_hash(
            kwargs['password'],
            current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
