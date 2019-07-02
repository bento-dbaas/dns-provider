import json
import logging
import sys

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from flasgger import Swagger, swag_from
from mongoengine import connect

from dns_provider.providers.gdns import DNSAPI
from dns_provider import utils, settings, models
from dns_provider.providers import exceptions

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
swagger = Swagger(app)
auth = HTTPBasicAuth()
cors = CORS(app)
connect(settings.MONGODB_DB, **settings.MONGODB_PARAMS)


@app.route("/dns/", methods=['POST'])
@swag_from('schemas/create_dns.yml',
    validation=True,
    validation_error_handler=utils.validation_error_inform_error)
def create_dns():
    data = request.get_json()
    dns = '{}.{}'.format(data.get('name'), data.get('domain'))

    dnsapi = DNSAPI(data.get('environment'))

    domain_id = dnsapi.get_domain_id_by_name(domain=data.get('domain'))
    if domain_id is None:
        error = "Domain '{}' not found!".format(data.get('domain'))
        return jsonify({'result': error }), 404

    record_id = dnsapi.get_record_by_name(name=data.get('name'), domain_id=domain_id)
    if record_id:
        error = "Could not create dns '{}', it already exists!".format(dns)
        return jsonify({'result': error }), 422

    try:
        dnsapi.create_record(data.get('name'), data.get('ip'), domain_id=domain_id)
    except exceptions.DNSMissingParameter as error_mp:
        utils.log_and_response(str(error_mp), 422, level=logging.ERROR, is_error=True)
    except exceptions.DNSNotFound as error_nf:
        utils.log_and_response(str(error_nf), 404, level=logging.ERROR, is_error=True)
    except exceptions.DNSUnknownError as error_ue:
        utils.log_and_response(str(error_nf), error_nf.status, level=logging.ERROR, is_error=True)

    return jsonify(data=dict(message="DNS '{}' successfully created.".format(dns))), 201

@app.route("/dns/<string:name>/<string:domain>", methods=['DELETE'])
def delete_dns(name, domain):
    """This function exposes the uri /dns/<name>/<domain>. That endpoint deleted
    a DNS on GDNS provider given the proper parameters. The HTTP methods accepted
    are: ['Delete'].

    Path Parameters:
    name (str): DNS name
    domain (str): domain name

    Returns:
    response (JSON): A JSON response and the status code
    """
    dnsapi = DNSAPI('dev')

    domain_id = dnsapi.get_domain_id_by_name(domain=domain)
    if not domain_id:
        error = "Domain '{}' not found!".format(domain)
        return jsonify({'result': error }), 404

    record_id = dnsapi.get_record_by_name(name, domain_id=domain_id)
    if not record_id:
        error = "Name '{}' not found!".format(name)
        return jsonify({'result': error }), 404

    dnsapi.delete_record(record_id)

    return jsonify({}), 204
