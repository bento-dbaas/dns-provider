""" In providers we have the implementation of the most important primitives for
each specific provider. Regarding DNS, 'create_dns' is a good example of primitive.
For instance we have GDNS as the only implementation available.
"""
import logging

from mongoengine import connect

from dns_provider import settings

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def mongo_connect(*args, **kwargs):
    """Connect mongoengine to mongo db. This connection is reused everywhere"""
    exc = None
    for _ in range(2):
        try:
            LOG.info("Attempting to connect to %s at %s...", settings.MONGODB_DB,
                     settings.MONGODB_HOST)
            connect(settings.MONGODB_DB, **settings.MONGODB_PARAMS)
        except Exception as e:
            LOG.warning("Error connecting to mongo, will retry in 1 sec: %r", e)
            time.sleep(1)
            exc = e
        else:
            LOG.info("Connected...")
            break
    else:
        LOG.critical("Unable to connect to %s at %s: %r", config.MONGO_DB,
                     config.MONGO_URI, exc)
        raise exc
