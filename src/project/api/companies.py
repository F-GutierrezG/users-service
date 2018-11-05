from flask import Blueprint
from project.auth import authenticate
from project.logics import CompanyLogics, DoesNotExist
from project.api.utils import success_response, failed_response


companies_blueprint = Blueprint('companies', __name__)


@companies_blueprint.route('/companies', methods=['GET'])
@authenticate
def companies(user):
    companies = CompanyLogics().list(user)
    return success_response(
        data=companies,
        status_code=200)


@companies_blueprint.route('/companies/<id>', methods=['GET'])
@authenticate
def company(user, id):
    try:
        company = CompanyLogics().get(user, id)
        return success_response(
            data=company,
            status_code=200)
    except DoesNotExist:
        return failed_response(message='not found.', status_code=404)
