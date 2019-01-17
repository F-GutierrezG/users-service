from flask import Blueprint, request
from sqlalchemy import exc
from project.auth import authenticate, authorize
from project.logics import UserLogics, NotFound, Unauthorized
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


@users_blueprint.route('/users/admins', methods=['GET'])
@authenticate
def admins(user):
    if user.admin is not True:
        return failed_response(message='unauthorized', status_code=401)

    users = UserLogics().list_admins()
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
    except NotFound:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users', methods=['POST'])
@authorize(['ADD_USER'])
def create(user):
    user_data = request.get_json()

    try:
        user = UserLogics().create(user_data, user)
        return success_response(
            data=user,
            status_code=201)

    except exc.IntegrityError:
        return failed_response('duplicate user.', 400)

    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)

    except Unauthorized:
        return failed_response('unauthorized', 401)


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

    except NotFound:
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

    except NotFound:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users/<id>/activate', methods=['PUT'])
@authorize(['UPDATE_USER'])
def activate(user, id):
    try:
        user = UserLogics().activate(id, user)
        return success_response(data=user, status_code=200)

    except NotFound:
        return failed_response(message='not found.', status_code=404)


@users_blueprint.route('/users/byIds/<ids>', methods=['GET'])
@authenticate
def filter_by_ids(user, ids):
    users = UserLogics().filter_by_ids(ids.split(','))
    return success_response(
        data=users,
        status_code=200)


@users_blueprint.route('/users/<id>/password', methods=['PUT'])
@authenticate
def change_password(user, id):
    user_data = request.get_json()
    try:
        UserLogics().change_password(user_data, id, user)
    except NotFound:
        return failed_response(message='not found.', status_code=404)

    return success_response(status_code=204)
