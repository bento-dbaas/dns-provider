from unittest import TestCase
from unittest.mock import patch
import json
import collections

from mongoengine import connect, disconnect

from dns_provider import models
from dns_provider.main import app


@patch('dns_provider.providers.gdns.DNSAPI.get_record_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.get_domain_id_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.create_record')
class ServiceCreateDNSTestCase(TestCase):
    """This class executes test for create_dns view."""

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_create_dns_success(self,
                                mock_create_record,
                                mock_get_domain_id_by_name,
                                mock_get_record_by_name):
        """It tests the dns creation through '/dns/' path and POST method."""
        success_status_code = 201
        name = 'test-dns-provider'
        domain = 'dev.globoi.com'
        ip = '10.224.77.89'
        fake_data = dict(name=name, domain=domain, ip=ip)
        fake_response = dict(data=fake_data)
        mock_create_record.return_value = 'test-dns-provider.dev.globoi.com'
        mock_get_domain_id_by_name.return_value  = 99999
        mock_get_record_by_name.return_value = None

        response = self.client.post('/dns/',
                                    data=json.dumps(fake_data),
                                    content_type='application/json')

        dns_object = models.DNS.objects.filter(
            name=name,
            domain=domain
        ).first()

        self.assertEqual(response.status_code, success_status_code)
        self.assertEqual(fake_response,
                         response.json)
        self.assertEqual(len(models.DNS.objects.all()), 1)

    def test_create_dns_invalid_domain(self,
                                       mock_create_record,
                                       mock_get_domain_id_by_name,
                                       mock_get_record_by_name):
        """It tests the dns creation with an invalid domain."""
        mock_get_domain_id_by_name.return_value = None
        error_msg = "Domain 'invalid_domain_test' not found!"
        error_status_code = 404
        fake_response = dict(error=dict(code=error_status_code, message=error_msg))

        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test_dns_provider',
                                        'domain': 'invalid_domain_test',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(models.DNS.objects.all()), 0)
        self.assertEqual(fake_response, response.json)

    def test_create_dns_name_already_exists(self,
                                            mock_create_record,
                                            mock_get_domain_id_by_name,
                                            mock_get_record_by_name):
        """It tests the dns creation with a name already exists."""
        error_msg = "Could not create dns 'test-exist.dev.globoi.com', it already exists!"
        error_status_code = 422
        fake_response = dict(error=dict(code=error_status_code, message=error_msg))
        mock_get_domain_id_by_name.return_value = 99999
        mock_get_record_by_name.return_value = 99998

        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test-exist',
                                        'domain': 'dev.globoi.com',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(models.DNS.objects.all()), 0)
        self.assertEqual(fake_response, response.json)
