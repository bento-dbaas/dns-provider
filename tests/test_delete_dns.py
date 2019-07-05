from unittest import TestCase
import json
from unittest.mock import patch

from dns_provider.main import app


@patch('dns_provider.providers.gdns.DNSAPI.get_record_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.get_domain_id_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.delete_record')
class ServiceDeleteDNSTestCase(TestCase):
    """This class executes test for delete_dns view."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_delete_dns_success(self,
                                mock_delete_record,
                                mock_get_domain_id_by_name,
                                mock_get_record_by_name):
        """It tests the dns deletion through '/dns/<dns_name>/<dns_domain>' path and DELETe method."""
        mock_delete_record.return_value = None
        mock_get_domain_id_by_name.return_value = 99998
        mock_get_record_by_name.return_value = 99999

        response = self.client.delete('/dns/test-dns-provider/dev.globoi.com', content_type='application/json')

        self.assertEqual(response.status_code, 204)
        self.assertEqual({}, dict(response.data))

    def test_delete_dns_invalid_domain(self,
                                       mock_delete_record,
                                       mock_get_domain_id_by_name,
                                       mock_get_record_by_name):
        """It tests the dns creation with an invalid domain."""
        mock_get_domain_id_by_name.return_value = None
        error_msg = "Domain 'invalid_domain_test' not found!"

        response = self.client.delete('/dns/test-dns-provider/invalid_domain_test', content_type='application/json')

        self.assertEqual(response.status_code, 404)
        print(response.data)
        self.assertEqual(dict(error=error_msg), json.loads(response.data.decode('utf-8')))

    def test_delete_dns_invalid_name(self,
                                     mock_delete_record,
                                     mock_get_domain_id_by_name,
                                     mock_get_record_by_name):
        """It tests the dns creation with a name already exists."""
        mock_get_domain_id_by_name.return_value = 99998
        mock_get_record_by_name.return_value = None
        error_msg = "Name 'invalid_dns_name' not found!"

        response = self.client.delete('/dns/invalid_dns_name/dev.globoi.com', content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(dict(error=error_msg), json.loads(response.data.decode('utf-8')))
