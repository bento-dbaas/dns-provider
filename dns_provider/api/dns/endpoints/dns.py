import logging

from flask import request, jsonify
from flask_restplus import Resource
from dns_provider.api.dns.business import create_dns, delete_dns
from dns_provider.api.dns.serializers import dns_serializer
from dns_provider.api.restplus import api
from dns_provider.database.models import DNS
from dns_provider.providers.gdns import DNSAPI
from flask_httpauth import HTTPBasicAuth
from dns_provider import settings

ns = api.namespace('dns', description='Operations related to dns')
auth = HTTPBasicAuth()
LOG = logging.getLogger(__name__)


@auth.verify_password
def verify_password(username, password):
    if settings.APP_USERNAME and username != settings.APP_USERNAME:
        return False
    if settings.APP_PASSWORD and password != settings.APP_PASSWORD:
        return False
    return True


@ns.route('/')
class DnsCollection(Resource):
    @api.response(200, "Dns successfully listed")
    @auth.login_required()
    def get(self):
        """
        Return all registered dns`s
        """
        dns = DNS.objects.all()
        return jsonify(dns)

    @api.response(201, "Dns successfully created")
    @api.expect(dns_serializer)
    @auth.login_required()
    def post(self):
        """
        Create new DNS
        """
        data = request.json
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
        dns_document = create_dns(data)
        return dns_document.serialize(), 201


@ns.route('/<string:name>/<string:domain>')
@api.response(404, "DNS not found")
class DnsItem(Resource):

    @api.marshal_with(dns_serializer)
    @auth.login_required()
    def get(self, name, domain):
        """
        Return one DNS
        """
        dns = DNS.objects(name=name, domain=domain).first()
        if not dns:
            error = "DNS '{}.{}' not found!".format(name, domain)
            return jsonify(error=dict(message=error, code=404)), 404
        return dns

    @api.response(204, 'Dns successfully deleted')
    @auth.login_required()
    def delete(self, name, domain):
        """
        Delete one DNS
        """
        dnsapi = DNSAPI('dev')

        dns = DNS.objects(name=name, domain=domain).first()

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

        delete_dns(name, domain)

        return jsonify(), 204
