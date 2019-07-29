import json
import logging
import sys
import os

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask.views import MethodView
from flask_httpauth import HTTPBasicAuth

from flasgger import Swagger, swag_from, validate
from mongoengine import connect
from pymongo.errors import ServerSelectionTimeoutError

from dns_provider.providers.gdns import DNSAPI
from dns_provider import utils, settings, models
from dns_provider.providers import exceptions, mongo_connect

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def create_app(testing=False):
    app = Flask(__name__)
    swagger = Swagger(app)
    auth = HTTPBasicAuth()
    cors = CORS(app)

    app.config.from_object(os.environ['APP_SETTINGS'])

    if app.config['TESTING']:
        app.testing = True
    else:
        mongo_connect()

    return app

app = create_app()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if settings.APP_USERNAME and username != settings.APP_USERNAME:
        return False
    if settings.APP_PASSWORD and password != settings.APP_PASSWORD:
        return False
    return True


class DNSCreateAPIView(MethodView):
    """This class handles requests to /dns/ endpoint."""
    decorators = [auth.login_required]

    def post(self):
        '''
        file: schemas/create_dns.yml
        '''
        data = request.get_json()
        validate(
            data,
            'DnsModel',
            'schemas/create_dns.yml',
            validation_error_handler=utils.validation_error_inform_error
        )

        dns = '{}.{}'.format(data.get('name'), data.get('domain'))
        dnsapi = DNSAPI('dev')

        domain_id = dnsapi.get_domain_id_by_name(domain=data.get('domain'))
        if domain_id is None:
            error = "Domain '{}' not found!".format(data.get('domain'))
            return jsonify(error=dict(message=error, code=404)), 404

        record_id = dnsapi.get_record_by_name(name=data.get('name'), domain_id=domain_id)
        if record_id:
            error = "Could not create dns '{}', it already exists!".format(dns)
            return jsonify(error=dict(message=error, code=422)), 422

        dnsapi.create_record(data.get('name'), data.get('ip'), domain_id=domain_id)
        dns_document = models.DNS(
            ip=data.get('ip'),
            name=data.get('name'),
            domain=data.get('domain')
        )
        dns_document.save()

        return jsonify(data=dns_document.serialize()), 201


dns_create_view = DNSCreateAPIView.as_view('dns_api')
app.add_url_rule('/dns/', view_func=dns_create_view, methods=['POST'])


class DNSRetrieveDestroyAPIView(MethodView):
    """This class handles requests to /dns/<name>/<domain> endpoint."""
    decorators = [auth.login_required]

    def delete(self, name, domain):
        '''
        file: schemas/delete_dns.yml
        '''
        dnsapi = DNSAPI('dev')

        dns = models.DNS.objects(name=name, domain=domain).first()

        if not dns:
            error = "DNS '{}.{}' not found!".format(name, domain)
            return jsonify(error=dict(message=error, code=404)), 404

        domain_id = dnsapi.get_domain_id_by_name(domain=domain)
        if not domain_id:
            error = "Domain '{}' not found!".format(domain)
            return jsonify(error=dict(message=error, code=404)), 404

        record_id = dnsapi.get_record_by_name(name, domain_id=domain_id)
        if not record_id:
            error = "Name '{}' not found!".format(name)
            return jsonify(error=dict(message=error, code=404)), 404

        dnsapi.delete_record(record_id)
        dns.delete()

        return jsonify(), 204

    def get(self, name, domain):
        '''
        file: schemas/get_dns.yml
        '''
        dnsapi = DNSAPI('dev')

        dns = models.DNS.objects(name=name, domain=domain).first()

        if not dns:
            error = "DNS '{}.{}' not found!".format(name, domain)
            return jsonify(error=dict(message=error, code=404)), 404

        return jsonify(data=dns.serialize()), 200

dns_retrive_destroy_view = DNSRetrieveDestroyAPIView.as_view('single_dns_api')
app.add_url_rule('/dns/<string:name>/<string:domain>', view_func=dns_retrive_destroy_view, methods=['DELETE', 'GET'])


@app.route("/healthcheck/", methods=['GET'])
def healthcheck():
    try:
        models.DNS.objects.first()
    except ServerSelectionTimeoutError as connection_error:
        message = 'Could not connect to MongoDB: {}'.format(str(connection_error))
        raise exceptions.JSONException(message, 500)
    return 'SUCCESS', 200

"""This method performs dns creation through Post Http method."""
@app.errorhandler(exceptions.JSONException)
def handle_json_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
