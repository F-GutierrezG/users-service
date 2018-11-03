from flask import Blueprint, request
from sqlalchemy import exc
from project.logics import UserLogics, DoesNotExist
from project.validators.exceptions import ValidatorException
from project.api.utils import success_response, failed_response


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['GET'])
def list():
    users = UserLogics().list()
    return success_response(
        data=users,
        status_code=200)


@users_blueprint.route('/users/<id>', methods=['GET'])
def get(id):
    try:
        user = UserLogics().get(id)
        return success_response(
            data=user,
            status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users', methods=['POST'])
def create():
    user_data = request.get_json()

    try:
        user = UserLogics().create(user_data)
        return success_response(
            data=user,
            status_code=201)

    except exc.IntegrityError:
        return failed_response('duplicate user.', 400)

    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)


@users_blueprint.route('/users/<id>', methods=['PUT'])
def update(id):
    user_data = request.get_json()

    try:
        user = UserLogics().update(user_data, id)
        return success_response(
            data=user,
            status_code=200)

    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)

    except exc.IntegrityError:
        return failed_response('duplicate user.', 400)

    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)


@users_blueprint.route('/users/<id>', methods=['DELETE'])
def delete(id):
    try:
        UserLogics().delete(id)
        return success_response(status_code=204)

    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)
