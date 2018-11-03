from flask import Blueprint, request
from project.logics import AuthLogics, DoesNotExist
from project.api.utils import success_response, failed_response


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    user_data = request.get_json()

    try:
        token = AuthLogics().login(user_data)
        return success_response(data=token, status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)
