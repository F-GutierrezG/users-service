from flask import jsonify


def success_response(data=None, status_code=200):
    return jsonify(data), status_code


def failed_response(message, status_code, data=None):
    return jsonify({
        'message': message,
        'data': data
    }), status_code
