import os
import logging
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

from flask import Flask, Blueprint
from dns_provider.database import db
from dns_provider.api.restplus import api
from dns_provider.api.dns.endpoints.dns import ns as dns_namespace
from dns_provider.api.dns.endpoints.healthcheck import ns as healthcheck_namespace
from dns_provider import settings

app = Flask(__name__)
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['MONGODB_SETTINGS'] = settings.MONGODB_PARAMS
    flask_app.config.from_object(os.environ['APP_SETTINGS'])

    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix='/')
    api.init_app(blueprint)
    api.add_namespace(dns_namespace)
    api.add_namespace(healthcheck_namespace)
    flask_app.register_blueprint(blueprint)
    db.init_app(flask_app)


def main():
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format('localhost:5000'))
    app.run(debug=True)

initialize_app(app)

if __name__ == '__main__':
    main()
