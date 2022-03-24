import logging
import json

from flask import request, jsonify
from flask_restplus import Resource
from dns_provider.api.restplus import api
from dns_provider.database.models import DNS
from dns_provider.providers import exceptions
from pymongo.errors import ServerSelectionTimeoutError

ns = api.namespace('healthcheck', description='Operations related to dns')


@ns.route('/')
class Healthcheck(Resource):
    @api.response(200, 'SUCCESS')
    def get(self):
        try:
            DNS.objects.first()
        except ServerSelectionTimeoutError as connection_error:
            message = 'Could not connect to MongoDB: {}'.format(str(connection_error))
            raise exceptions.JSONException(message, 500)
        return 'SUCCESS', 200