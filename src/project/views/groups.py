from flask import Blueprint, request
from project.logics import GroupLogics
from project.views.utils import success_response


groups_blueprint = Blueprint('groups', __name__)


@groups_blueprint.route('/auth/groups', methods=['GET'])
def list():
    groups = GroupLogics().list()
    return success_response(
        data=groups,
        status_code=200)


@groups_blueprint.route('/auth/groups', methods=['POST'])
def create():
    data = request.get_json()

    group = GroupLogics().create(data)
    return success_response(
        data=group,
        status_code=201)


@groups_blueprint.route('/auth/groups/<id>', methods=['PUT'])
def update(id):
    data = request.get_json()

    group = GroupLogics().update(data, id)

    return success_response(
        data=group,
        status_code=200)


@groups_blueprint.route('/auth/groups/<id>', methods=['DELETE'])
def delete(id):
    GroupLogics().delete(id)

    return success_response(status_code=204)


@groups_blueprint.route('/auth/groups/<id>/users', methods=['GET'])
def users(id):
    users = GroupLogics().users(id)

    return success_response(
        data=users,
        status_code=200)


@groups_blueprint.route('/auth/groups/<id>/users', methods=['POST'])
def add_user(id):
    data = request.get_json()

    users = GroupLogics().add_user(data, id)

    return success_response(
        data=users,
        status_code=200)


@groups_blueprint.route(
    '/auth/groups/<id>/users/<user_id>', methods=['DELETE'])
def delete_user(id, user_id):
    users = GroupLogics().delete_user(user_id, id)

    return success_response(
        data=users,
        status_code=200)


@groups_blueprint.route('/auth/groups/<id>/permissions', methods=['GET'])
def permissions(id):
    permissions = GroupLogics().permissions(id)

    return success_response(
        data=permissions,
        status_code=200)


@groups_blueprint.route('/auth/groups/<id>/permissions', methods=['POST'])
def add_permission(id):
    data = request.get_json()

    permissions = GroupLogics().add_permission(data, id)

    return success_response(
        data=permissions,
        status_code=200)


@groups_blueprint.route(
    '/auth/groups/<id>/permissions/<code>', methods=['DELETE'])
def delete_permission(id, code):
    permissions = GroupLogics().delete_permission(code, id)

    return success_response(
        data=permissions,
        status_code=200)
