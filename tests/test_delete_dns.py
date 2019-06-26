from unittest import TestCase
import json

from dns_provider.main import app


class ServiceDeleteDNSTestCase(TestCase):
    """This class executes test for delete_dns view."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_delete_dns_success(self):
        """It tests the dns deletion through '/dns/<dns_name>/<dns_domain>' path and DELETe method."""
        response = self.client.delete('/dns/test-dns-provider/dev.globoi.com', content_type='application/json')

        self.assertEqual(response.status_code, 204)
        self.assertEqual({}, dict(response.data))

    def test_delete_dns_invalid_domain(self):
        """It tests the dns creation with an invalid domain."""
        error_msg = "Domain 'invalid_domain_test' not found!"
        response = self.client.delete('/dns/test-dns-provider/invalid_domain_test', content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(dict(result=error_msg), json.loads(response.data))

    def test_delete_dns_invalid_name(self):
        """It tests the dns creation with a name already exists."""
        error_msg = "Name 'invalid_dns_name' not found!"
        response = self.client.delete('/dns/invalid_dns_name/dev.globoi.com', content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(dict(result=error_msg), json.loads(response.data))
