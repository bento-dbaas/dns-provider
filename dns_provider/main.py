import json

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from dns_provider.providers.gdns import DNSAPI


app = Flask(__name__)
auth = HTTPBasicAuth()
cors = CORS(app)


@app.route("/dns/", methods=['POST'])
def create_dns():
    """This function exposes the uri /dns/. That endpoint creates a DNS on GDNS
    provider. The HTTP methods accepted are: ['POST'].

    Payload Parameters:
    name (str): DNS name
    domain (str): domain name
    environment (str): environment
    ip (str): IP address

    Returns:
    response (JSON): A JSON response and the status code
    """
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

    dnsapi.create_record(data.get('name'), data.get('ip'), domain_id=domain_id)

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
