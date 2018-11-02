from project import db
from sqlalchemy.orm import validates


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    @validates('first_name')
    def validate_first_name(self, key, first_name):
        if not first_name:
            raise ValueError('first_name')

        return first_name

    @validates('last_name')
    def validate_last_name(self, key, last_name):
        if not last_name:
            raise ValueError('last_name')

        return last_name

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('email')

        return email

    @validates('password')
    def validate_password(self, key, password):
        if not password:
            raise ValueError('password')

        return password
