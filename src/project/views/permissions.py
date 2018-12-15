from flask import Blueprint
from project.logics import PermissionLogics
from project.views.utils import success_response


permissions_blueprint = Blueprint('permissions', __name__)


@permissions_blueprint.route('/auth/permissions', methods=['GET'])
def list():
    permissions = PermissionLogics().list()
    return success_response(
        data=permissions,
        status_code=200)
