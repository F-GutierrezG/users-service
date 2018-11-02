from flask import Blueprint, request, jsonify
from project.logics import UserLogics
from project.serializers import UserSerializer


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['POST'])
def create():
    user_data = request.get_json()

    user = UserLogics().create(user_data)

    return jsonify({
        'message': 'OK',
        'data': UserSerializer.to_json(user),
    }), 200
