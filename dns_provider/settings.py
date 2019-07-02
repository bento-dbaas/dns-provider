"""This file looks for all environment variables to credentials, database and
providers."""

from os import getenv
from collections import OrderedDict


#GDNS DEV
DNS_PROVIDER_GDNS_ENDPOINT = getenv("DNS_PROVIDER_GDNS_ENDPOINT")
DNS_PROVIDER_GDNS_USER = getenv("DNS_PROVIDER_GDNS_USER")
DNS_PROVIDER_GDNS_PWD = getenv("DNS_PROVIDER_GDNS_PWD")

#MONGODB SETTINGS
MONGODB_HOST = getenv("MONGODB_HOST", "127.0.0.1")
MONGODB_PORT = int(getenv("MONGODB_PORT", 27017))
MONGODB_DB = getenv("MONGODB_DB", "dns_provider")
MONGODB_USER = getenv("MONGODB_USER", None)
MONGODB_PWD = getenv("MONGODB_PWD", None)
MONGODB_ENDPOINT = getenv("DNS_PROVIDER_MONGODB_ENDPOINT", None)

MONGODB_PARAMS = {'document_class': OrderedDict}
if MONGODB_ENDPOINT:
    MONGODB_PARAMS["host"] = MONGODB_ENDPOINT
else:
    MONGODB_PARAMS['host'] = MONGODB_HOST
    MONGODB_PARAMS['port'] = MONGODB_PORT
    MONGODB_PARAMS['username'] = MONGODB_USER
    MONGODB_PARAMS['password'] = MONGODB_PWD