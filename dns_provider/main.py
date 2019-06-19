import json

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from providers.gdns import DNSAPI


app = Flask(__name__)
auth = HTTPBasicAuth()
cors = CORS(app)


@app.route("/dns/", methods=['POST'])
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

    dnsapi.create_record(data.get('name'), data.get('ip'), domain_id=domain_id)

    return jsonify(data=dict(message="DNS '{}' successfully created.".format(dns))), 201
