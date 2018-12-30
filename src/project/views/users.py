from flask import Blueprint, request
from sqlalchemy import exc
from project.auth import authenticate, authorize
from project.logics import UserLogics, DoesNotExist
from project.validators.exceptions import ValidatorException
from project.views.utils import success_response, failed_response


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['GET'])
@authorize(['LIST_USERS'])
def list(user):
    users = UserLogics().list()
    return success_response(
        data=users,
        status_code=200)


@users_blueprint.route('/users/<id>', methods=['GET'])
@authorize(['VIEW_USER'])
def get(user, id):
    try:
        user = UserLogics().get(id)
        return success_response(
            data=user,
            status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users', methods=['POST'])
@authorize(['ADD_USER'])
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
@authorize(['UPDATE_USER'])
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


@users_blueprint.route('/users/<id>/deactivate', methods=['PUT'])
@authorize(['UPDATE_USER'])
def deactivate(user, id):
    try:
        user = UserLogics().deactivate(id, user)
        return success_response(data=user, status_code=200)

    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users/<id>/activate', methods=['PUT'])
@authorize(['UPDATE_USER'])
def activate(user, id):
    try:
        user = UserLogics().activate(id, user)
        return success_response(data=user, status_code=200)

    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users/byIds/<ids>', methods=['GET'])
@authenticate
def filter_by_ids(user, ids):
    users = UserLogics().filter_by_ids(ids.split(','))
    return success_response(
        data=users,
        status_code=200)
