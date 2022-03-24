from flask_restplus import fields
from dns_provider.api.restplus import api

dns_serializer = api.model('DNS', {
    'ip': fields.String(required=True, description='Ip', max_length=15),
    'name': fields.String(required=True, description='Name', max_length=200),
    'domain': fields.String(required=True, description='Domain', max_length=150),
})

