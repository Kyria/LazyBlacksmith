# -*- encoding: utf-8 -*-
from flask import jsonify


def json_response(status, message, code):
    """ Shortcut to generate json response with specific values """
    response = jsonify({
        'status': status,
        'message': message
    })
    response.status_code = code
    return response
