from flask import Blueprint, request
from project.auth import authenticate
from project.logics import AuthLogics, NotFound
from project.views.utils import success_response, failed_response
from project.validators.exceptions import ValidatorException


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    user_data = request.get_json()

    try:
        token = AuthLogics().login(user_data)
        if token is False:
            return failed_response(
                message='invalid login data.', status_code=400)
        return success_response(data=token, status_code=200)
    except NotFound:
        return failed_response(message='not found.', status_code=404)
    except ValidatorException as e:
        return failed_response('invalid payload.', 400, e.errors)


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout(user):
    return success_response(status_code=204)


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def status(user):
    user = AuthLogics().get_status(user)
    return success_response(data=user, status_code=200)


@auth_blueprint.route('/auth/recover-password', methods=['POST'])
def recover_password():
    try:
        email = request.get_json()['email']
        AuthLogics().recover_password(email)
    except Exception as e:
        print('********', e)
    finally:
        return success_response(status_code=200)


@auth_blueprint.route('/auth/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        AuthLogics().change_password(data)

    except Exception:
        return failed_response(message="bad request", status_code=400)

    return success_response(status_code=200)
