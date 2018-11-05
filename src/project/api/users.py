from flask import Blueprint, request
from sqlalchemy import exc
from project.auth import authenticate
from project.logics import UserLogics, DoesNotExist
from project.validators.exceptions import ValidatorException
from project.api.utils import success_response, failed_response


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['GET'])
@authenticate
def list(user):
    users = UserLogics().list()
    return success_response(
        data=users,
        status_code=200)


@users_blueprint.route('/users/<id>', methods=['GET'])
@authenticate
def get(user, id):
    try:
        user = UserLogics().get(id)
        return success_response(
            data=user,
            status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users', methods=['POST'])
@authenticate
def create(user):
    user_data = request.get_json()
    user_data['created_by'] = user.id

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
@authenticate
def update(user, id):
    user_data = request.get_json()
    user_data['updated_by'] = user.id

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
@authenticate
def delete(user, id):
    try:
        UserLogics().delete(id)
        return success_response(status_code=204)

    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)
