from flask import current_app
from sqlalchemy.sql import func

from project import db, bcrypt


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
    updated = db.Column(db.DateTime, onupdate=func.now())
    updated_by = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            password = kwargs['password']
            self.password = bcrypt.generate_password_hash(
                password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
