from flask import Blueprint, jsonify


health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/users-service/health', methods=['GET'])
def health():
    return jsonify({
        'message': 'ok'
    })
