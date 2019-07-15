import json
from http import HTTPStatus
import logging

from flask import Response

from werkzeug.exceptions import abort
from jsonschema import ValidationError

LOG = logging.getLogger(__name__)


def validation_error_inform_error(error, data, schema):
    """Custom validation error handler which produces 400 Bad Request response
    in case validation fails and returns the error

    Parameters:
    error (ValidationError objects): Validation error thrown from flasgger
    data (dict): Request's payload
    schema (str): String containing the JSON Schema

    Returns:
    response (Response object): The HTTP response object
    """
    abort(format_response(str(error.message), HTTPStatus.BAD_REQUEST, True))

def log_and_response(msg, code, level=logging.DEBUG, is_error=False):
    """ Function designed to log using logging library and return a Response
    comprised of the msg and status code

    Parameters:
    msg (Object): Message is going to be returned
    code (integer): HTTP status code
    level (integer): Python's Logging Levels
    is_error (bool): Flag for errors

    Returns:
    response (Response object): The formated HTTP response object
    """
    LOG.log(level, msg)
    return format_response(msg, code, is_error)

def format_response(msg, code, is_error):
    """It formats a response following the json:api specification. For instance,
    it deals with simple responses for single and multiple objects or errors.

    Parameters:
    msg (Object): Message is going to be returned
    code (integer): HTTP status code
    is_error (bool): Flag for errors

    Returns:
    response (Response object): The HTTP response object
    """
    if is_error:
        return Response(json.dumps({'error': dict(code=code,
                                                  message=msg)}), status=code)
    return Response(json.dumps({'data': msg}), status=code)
