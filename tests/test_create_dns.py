from unittest import TestCase
import json

from dns_provider.main import app


class ServiceCreateDNSTestCase(TestCase):
    """This class executes test for create_dns view."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_create_dns_success(self):
        """It tests the dns creation through '/dns/' path and POST method."""
        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'test-dns-provider3',
                                        'domain': 'dev.globoi.com',
                                        'environment': 'dev',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn("DNS 'test-dns-provider3.dev.globoi.com' successfully created.", response.data)

    def test_create_dns_invalid_domain(self):
        """It tests the dns creation with an invalid domain."""
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
        self.assertEqual(dict(result=error_msg), json.loads(response.data))

    def test_create_dns_name_already_exists(self):
        """It tests the dns creation with a name already exists."""
        error_msg = "Could not create dns 'dbaas.dev.globoi.com', it already exists!"
        response = self.client.post('/dns/',
                                    data=json.dumps({
                                        'name':'dbaas',
                                        'domain': 'dev.globoi.com',
                                        'environment': 'dev',
                                        'ip': '10.224.77.89'
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(dict(result=error_msg), json.loads(response.data))
