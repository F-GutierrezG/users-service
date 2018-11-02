from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from project.logics import UserLogics
from project.serializers import UserSerializer


users_blueprint = Blueprint('users', __name__)


def success_response(data):
    return jsonify({
        'message': 'ok',
        'data': data,
    }), 200


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
        return success_response(UserSerializer.to_json(user))
    except exc.IntegrityError:
        return failed_response('duplicate user.', 400)
    except ValueError:
        return failed_response('invalid payload.', 400)
