import json
import logging
import sys

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from flasgger import Swagger, swag_from
from mongoengine import connect
from pymongo.errors import ServerSelectionTimeoutError

from dns_provider.providers.gdns import DNSAPI
from dns_provider import utils, settings, models
from dns_provider.providers import exceptions, mongo_connect

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
swagger = Swagger(app)
auth = HTTPBasicAuth()
cors = CORS(app)
mongo_connect()


@app.errorhandler(exceptions.JSONException)
def handle_json_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/dns/", methods=['POST'])
@swag_from('schemas/create_dns.yml',
    validation=True,
    validation_error_handler=utils.validation_error_inform_error)
def create_dns():
    data = request.get_json()
    dns = '{}.{}'.format(data.get('name'), data.get('domain'))

    dnsapi = DNSAPI('dev')

    domain_id = dnsapi.get_domain_id_by_name(domain=data.get('domain'))
    if domain_id is None:
        error = "Domain '{}' not found!".format(data.get('domain'))
        return jsonify({'error': error }), 404

    record_id = dnsapi.get_record_by_name(name=data.get('name'), domain_id=domain_id)
    if record_id:
        error = "Could not create dns '{}', it already exists!".format(dns)
        return jsonify({'error': error }), 422

    dnsapi.create_record(data.get('name'), data.get('ip'), domain_id=domain_id)
    dns_document = models.DNS(
        ip=data.get('ip'),
        name=data.get('name'),
        domain=data.get('domain')
    )
    dns_document.save()

    return jsonify(data=dict(message="DNS '{}' successfully created.".format(dns))), 201

@app.route("/dns/<string:name>/<string:domain>", methods=['DELETE', 'GET'])
@swag_from('schemas/delete_dns.yml')
def delete_dns(name, domain):
    dnsapi = DNSAPI('dev')

    if request.method == 'DELETE':
        domain_id = dnsapi.get_domain_id_by_name(domain=domain)
        if not domain_id:
            error = "Domain '{}' not found!".format(domain)
            return jsonify({'error': error }), 404

        record_id = dnsapi.get_record_by_name(name, domain_id=domain_id)
        if not record_id:
            error = "Name '{}' not found!".format(name)
            return jsonify({'error': error }), 404

        dnsapi.delete_record(record_id)

        return jsonify({}), 204
    else:
        domain_id = dnsapi.get_domain_id_by_name(domain=domain)
        if not domain_id:
            error = "Domain '{}' not found!".format(domain)
            return jsonify({'error': error }), 404

        record_id = dnsapi.get_record_by_name(name, domain_id=domain_id)
        if not record_id:
            error = "Name '{}' not found!".format(name)
            return jsonify({'error': error }), 404

        return jsonify(dict(
            record_id=record_id,
            domain_id=domain_id,
            name=name,
            domain=domain)), 200


@app.route("/healthcheck/", methods=['GET'])
def healthcheck():
    try:
        models.DNS.objects.first()
    except ServerSelectionTimeoutError as connection_error:
        message = 'Could not connect to MongoDB: {}'.format(str(connection_error))
        raise exceptions.JSONException(message, 500)
    return 'SUCCESS', 200
