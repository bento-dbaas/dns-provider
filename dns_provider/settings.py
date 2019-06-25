"""This file looks for all environment variables to credentials and providers."""

from os import getenv


#GDNS DEV
DNS_PROVIDER_GDNS_ENDPOINT = getenv("DNS_PROVIDER_GDNS_ENDPOINT")
DNS_PROVIDER_GDNS_USER = getenv("DNS_PROVIDER_GDNS_USER")
DNS_PROVIDER_GDNS_PWD = getenv("DNS_PROVIDER_GDNS_PWD")
