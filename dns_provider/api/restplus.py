import logging
import traceback

from flask_restplus import Api
from dns_provider import settings
from flask_mongoengine import DoesNotExist
from dns_provider.providers.exceptions import JSONException
from flask import jsonify

log = logging.getLogger(__name__)

api = Api(version='1.0', title='DNS Provider API',
          description='API to manage DNS', doc='/docs/')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(DoesNotExist)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404


@api.errorhandler(JSONException)
def handle_json_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response