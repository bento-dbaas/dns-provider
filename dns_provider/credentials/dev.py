class Credential(object):

    def __init__(self, environment):
        self.user='dbproducao@corp.globo.com'
        self.password='123456'
        self.endpoint = 'http://int.gdns.qa.globoi.com'

    def get_credentials(self, environment):
        return self
