# encoding: utf-8

from http import client as http_client
from urllib.parse import urlparse
import json

from dns_provider.credentials.dev import Credential


class DNSAPI(object):
    """This class knows how to send request to the GDNS Service."""

    def __init__(self, environment):
        credential = Credential(environment=environment)

        self.base_url = credential.endpoint
        self.username = credential.user
        self.password = credential.password
        self.token = None

    def __request(self, method, path, data=None, use_token=True, retry=True):
        """This method knows how to send a request to the GDNS service. This
        method can do a retry (default) for every request sent.

        Parameters:
        method (str): HTTP method
        path (str): string that is concatenated to base url
        data (dict): request payload
        use_token (bool): It defines weather the token should or should not be used to make a request
        retry (bool): If true, this retries the request with a new token

        Returns:
        response (str): The HTTP response string
        """
        complete_url = self.base_url + path
        url = urlparse(complete_url)
        url_path = url.path

        headers = {'Content-type': 'application/json'}
        if use_token:
            data = data or {}
            data['auth_token'] = self.__request_token()

        data_string = json.dumps(data, indent=2) if data else None
        #LOG.debug(u'Requisição %s %s', method, complete_url)

        if url.scheme == 'https':
            http = http_client.HTTPSConnection(url.hostname, url.port or 443)
        else:
            http = http_client.HTTPConnection(url.hostname, url.port or 80)

        http.request(method, url_path, data_string, headers)
        response = http.getresponse()
        response_string = response.read()
        # LOG.debug(u'Response: %d %s\nContent-type: %s\n%s', response.status,
        #           response.reason, response.getheader('Content-type'), response_string)
        if response.status == 422:
            pass

        if response.status == 404:
            pass

        if response.status == 401 and retry:
            # LOG.info(u'Chamada DNSAPI com token inválido... gerando novo token e retentando...')
            self.__request_token(force=True)
            return self.__request(method, path, data, retry=False)

        if response.status == 204:  # no content
            return None

        if not (response.status in [200, 201]):
            pass

        if response.getheader('Content-type', 'application/json').startswith('application/json'):
            return json.loads(response_string)

        return response_string

    def __request_token(self, force=False):
        """This method sends a request to retrieve the authentication token.
        That token is required for authorization purposes on every request. When
        you need to force token validation even when you already have a token,
        call this method setting force = True.

        Parameters:
        force (bool): The force flag

        Returns:
        token (str): The authentication token
        """
        if not self.token or force:
            auth = self.__request('POST', '/users/sign_in.json', {'user': {
                                  'email': self.username, 'password': self.password}}, use_token=False, retry=False)
            self.token = auth['authentication_token']
        return self.token

    def get_domain_id_by_name(self, domain='globoi.com'):
        """It gets the id of a domain given its name.

        Parameters:
        domain (str): The domain name

        Returns:
        record_id (str) or None: The domain id or None for invalid domains
        """

        id = self.__request('GET', '/domains.json', data={'query': domain})

        if id:
            return id[0]['domain'].get('id')
        else:
            return None

    def get_record_by_name(self, name, record_type='A', domain_id=None):
        """It searchs a record id given a domain name.

        Parameters:
        name (str): The DNS name
        record_type (str): DNS type (A, CNAME, etc)
        domain_id (int): Id of a domain

        Returns:
        record_id (str) or None: The DNS record_id or None for invalid DNSs
        """
        if domain_id is not None:
            record = self.__request('GET', '/domains/' + str(domain_id) + '/records.json', data={'query': name})

        if record:
            return record[0][str(record_type.lower())].get('id')

        return None

    def create_record(self, name, content, domain_id=None, record_type='A'):
        """This method creates a record (DNS) on the GDNS service. It deals with
        CNAME and A record types. Before the actual creation, this method looks
        for the domain is being created. If the domain is already registered, then
        the old one is deleted and a new one written.

        Parameters:
        name (str): The DNS name
        content (str): the IP
        domain_id (int): Id of a domain
        record_type (str): DNS type (A, CNAME, etc)

        Returns:
        dns (str): The DNS record itself
        """
        if domain_id is not None:
            id_record = self.get_record_by_name(name, domain_id=domain_id)
        if id_record:
            pass
        if record_type == 'CNAME':
            content += '.'

        response = self.__request('POST', '/domains/%d/records.json' % domain_id,
                                {"record": {"name": name, "type": record_type, "content": content}})
        record = response['record']
        # LOG.info(u'Cadastrado a entrada: %s', record)
        return record

    def delete_record(self, record_id):
        """This method deletes a record (DNS) on the GDNS service.

        Parameters:
        record_id (int): The id of a given DNS

        Returns:
        response_string (str): The response from GDNS
        """
        self.__request('DELETE', '/records/%d.json' % record_id)
