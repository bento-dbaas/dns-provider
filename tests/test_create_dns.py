from unittest import TestCase
from unittest.mock import patch
import json

from dns_provider.main import app


@patch('dns_provider.providers.gdns.DNSAPI.get_record_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.get_domain_id_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.create_record')
class ServiceCreateDNSTestCase(TestCase):
    """This class executes test for create_dns view."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_create_dns_success(self,
                                mock_create_record,
                                mock_get_domain_id_by_name,
                                mock_get_record_by_name):
        """It tests the dns creation through '/dns/' path and POST method."""
        success_msg = "DNS 'test-dns-provider.dev.globoi.com' successfully created."
        mock_create_record.return_value = 'test-dns-provider.dev.globoi.com'
        mock_get_domain_id_by_name.return_value  = 99999
        mock_get_record_by_name.return_value = None

        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test-dns-provider',
                                        'domain': 'dev.globoi.com',
                                        'environment': 'dev',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(dict(data=dict(message=success_msg)),
                         json.loads(response.data.decode('utf-8')))

    def test_create_dns_invalid_domain(self,
                                       mock_create_record,
                                       mock_get_domain_id_by_name,
                                       mock_get_record_by_name):
        """It tests the dns creation with an invalid domain."""
        mock_get_domain_id_by_name.return_value = None
        error_msg = "Domain 'invalid_domain_test' not found!"

        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test_dns_provider',
                                        'domain': 'invalid_domain_test',
                                        'environment': 'dev',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(dict(error=error_msg), json.loads(response.data.decode('utf-8')))

    def test_create_dns_name_already_exists(self,
                                            mock_create_record,
                                            mock_get_domain_id_by_name,
                                            mock_get_record_by_name):
        """It tests the dns creation with a name already exists."""
        error_msg = "Could not create dns 'test-exist.dev.globoi.com', it already exists!"
        mock_get_domain_id_by_name.return_value = 99999
        mock_get_record_by_name.return_value = 99998

        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test-exist',
                                        'domain': 'dev.globoi.com',
                                        'environment': 'dev',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(dict(error=error_msg), json.loads(response.data.decode('utf-8')))
