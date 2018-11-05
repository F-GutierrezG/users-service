from sqlalchemy.sql.expression import true

from project.validators.decorators import validate
from project.serializers import (
    UserSerializer, CompanySerializer, TokenSerializer)
from project.validations import (
    CreateUserValidator, UpdateUserValidator, LoginValidator)
from project.models import User, Company
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


class CompanyLogics:
    def list(self, user):
        companies = Company.query.filter(
            Company.active == true(),
            Company.users.any(User.id == user.id))

        return CompanySerializer.to_array(companies)
