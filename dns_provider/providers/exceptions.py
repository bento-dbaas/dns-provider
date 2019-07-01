class DNSNotFound(Exception):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'DNSNotFound({})'.format(str(self.path))


class DNSMissingParameter(Exception):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'DNSMissingParameter({})'.format(str(self.path))


class DNSUnknownError(Exception):

    def __init__(self, path, status):
        self.path = path
        self.status = status

    def __str__(self):
        return 'DNSUnknownError({0}, http={1})'.format(str(self.path), self.status)
