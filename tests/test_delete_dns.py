from unittest import TestCase
import json
from unittest.mock import patch

from mongoengine import connect, disconnect

from dns_provider.main import app
from dns_provider import models


@patch('dns_provider.providers.gdns.DNSAPI.get_record_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.get_domain_id_by_name')
@patch('dns_provider.providers.gdns.DNSAPI.delete_record')
class ServiceDeleteDNSTestCase(TestCase):
    """This class executes test for delete_dns view."""

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.fake_name = 'test-dns-provider'
        self.fake_domain = 'dev.globoi.com'
        self.fake_ip = '10.224.77.89'
        self.fake_data = dict(
            name=self.fake_name,
            domain=self.fake_domain,
            ip=self.fake_ip
        )
        dns = models.DNS(**self.fake_data)
        dns.save()

    def tearDown(self):
        models.DNS.objects().delete()

    def test_delete_dns_success(self,
                                mock_delete_record,
                                mock_get_domain_id_by_name,
                                mock_get_record_by_name):
        """It tests the dns deletion through '/dns/<dns_name>/<dns_domain>' path and DELETe method."""
        mock_delete_record.return_value = None
        mock_get_domain_id_by_name.return_value = 99998
        mock_get_record_by_name.return_value = 99999
        url = '/dns/{}/{}'.format(self.fake_name, self.fake_domain)
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(models.DNS.objects.all()), 0)

    def test_delete_dns_object_does_not_exist(self,
                                     mock_delete_record,
                                     mock_get_domain_id_by_name,
                                     mock_get_record_by_name):
        """It tests the dns creation with a name not created by the dns provider."""
        invalid_name = 'invalid_name'
        error_msg = "DNS '{}.{}' not found!".format(invalid_name, self.fake_domain)
        error_status_code = 404
        fake_error_response = dict(error=dict(message=error_msg, code=error_status_code))

        response = self.client.delete('/dns/{}/{}'.format(invalid_name, self.fake_domain), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(fake_error_response, response.json)
        self.assertEqual(len(models.DNS.objects.all()), 1)

    def test_delete_dns_invalid_domain(self,
                                       mock_delete_record,
                                       mock_get_domain_id_by_name,
                                       mock_get_record_by_name):
        """It tests the dns creation with an invalid domain."""
        mock_get_domain_id_by_name.return_value = None
        error_msg = "Domain '{}' not found!".format(self.fake_domain)
        error_status_code = 404
        fake_error_response = dict(error=dict(message=error_msg, code=error_status_code))

        response = self.client.delete('/dns/{}/{}'.format(self.fake_name, self.fake_domain), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(fake_error_response, response.json)
        self.assertEqual(len(models.DNS.objects.all()), 1)

    def test_delete_dns_invalid_name(self,
                                     mock_delete_record,
                                     mock_get_domain_id_by_name,
                                     mock_get_record_by_name):
        """It tests the dns creation with a name already exists."""
        mock_get_domain_id_by_name.return_value = 99998
        mock_get_record_by_name.return_value = None
        error_msg = "Name '{}' not found!".format(self.fake_name)
        error_status_code = 404
        fake_error_response = dict(error=dict(message=error_msg, code=error_status_code))

        response = self.client.delete('/dns/{}/{}'.format(self.fake_name, self.fake_domain), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(fake_error_response, response.json)
        self.assertEqual(len(models.DNS.objects.all()), 1)
