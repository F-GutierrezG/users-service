from flask import Blueprint, request
from project.auth import authenticate
from project.logics import AuthLogics, DoesNotExist
from project.api.utils import success_response, failed_response
from project.validators.exceptions import ValidatorException


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    user_data = request.get_json()

    try:
        token = AuthLogics().login(user_data)
        return success_response(data=token, status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)
    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout():
    return success_response(status_code=204)


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def status():
    token = request.headers.get('Authorization').split(' ')[1]

    user = AuthLogics().status(token)
    return success_response(data=user, status_code=200)
