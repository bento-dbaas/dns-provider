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

class JSONException(Exception):

    def __init__(self, message, status_code, payload=None):
        Exception.__init__(self)
        self.status_code = status_code
        self.error_dict = dict(message=message, code=self.status_code)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.error_dict
        return rv
