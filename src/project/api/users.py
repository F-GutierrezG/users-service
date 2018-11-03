from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from project.logics import UserLogics
from project.validators.exceptions import ValidatorException


users_blueprint = Blueprint('users', __name__)


def success_response(data, status_code=200):
    return jsonify({
        'message': 'ok',
        'data': data,
    }), status_code


def failed_response(message, status_code, data=None):
    return jsonify({
        'message': message,
        'data': data
    }), status_code


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


@users_blueprint.route('/user/<id>', methods=['PUT'])
def update(id):
    user_data = request.get_json()

    try:
        user = UserLogics().update(user_data, id)
        return success_response(
            data=user,
            status_code=200)

    except exc.IntegrityError:
        return failed_response('duplicate user.', 400)

    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)
