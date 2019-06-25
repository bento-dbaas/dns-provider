from dns_provider import settings

class Credential(object):
    """This class holds the credentials and methods to work on dev env."""

    def __init__(self, environment):
        self.user = settings.DNS_PROVIDER_GDNS_USER
        self.password = settings.DNS_PROVIDER_GDNS_PWD
        self.endpoint = settings.DNS_PROVIDER_GDNS_ENDPOINT

    def get_credentials(self, environment):
        """This method returns the credential to a given environment.

        Parameters:
        environment (str): dev or prod

        Returns:
        credential (Credential): The Credential object itself
        """
        return self
