import pickle
import re
from urllib.parse import urlparse

from flask import Flask
from flask_babel import Babel, get_translations
from flask_session.base import Serializer, ServerSideSession
from itsdangerous import Signer
from landregistry.enhanced_logging import FlaskEnhancedLogging
from landregistry.exceptions import ExceptionHandlers
from landregistry.healthchecks import HealthChecks
from landregistry.security_headers import SecurityHeaders, UIDefaultHeaders

from flask_session import Session
from server import config
from server.config import DEPENDENCIES
from server.custom_extensions.cachebust_static_assets.main import CachebustStaticAssets
from server.custom_extensions.csrf.main import CSRF
from server.custom_extensions.flask_babel_js.main import BabelJS
from server.custom_extensions.google_analytics.main import GoogleAnalytics
from server.custom_extensions.gzip_static_assets.main import GzipStaticAssets
from server.custom_extensions.jinja_markdown_filter.main import JinjaMarkdownFilter
from server.custom_extensions.wtforms.main import WTFormsHelpersGroups
from server.exceptions import (
    application_error_renderer,
    http_error_renderer,
    unhandled_error_renderer,
)
from server.locale import get_locale

# Create empty extension objects here
cachebust_static_assets = CachebustStaticAssets()
gzip_static_assets = GzipStaticAssets()
jinja_markdown_filter = JinjaMarkdownFilter()
csrf = CSRF()
wtforms_helpers = WTFormsHelpersGroups()
google_analytics = GoogleAnalytics()
enhanced_logging = FlaskEnhancedLogging()
exception_handlers = ExceptionHandlers()
health = HealthChecks()
headers = SecurityHeaders()

babel = Babel()
sess = Session()
babel_js = BabelJS()


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""
    enhanced_logging.init_app(app)
    jinja_markdown_filter.init_app(app)
    csrf.init_app(app)
    wtforms_helpers.init_app(app)
    google_analytics.init_app(app)
    exception_handlers.init_app(app)

    exception_handlers.on_http_error_render = http_error_renderer
    exception_handlers.on_application_error_render = application_error_renderer
    exception_handlers.on_unhandled_error_render = unhandled_error_renderer

    health.init_app(app)
    health.add_dependencies(DEPENDENCIES)
    # Change a few of the default headers for geoserver and viaeuropa mapping to work
    # Note boundary geoserver is probably the same host but just for safety
    for header in UIDefaultHeaders.as_list:
        if header.header_name == "Content-Security-Policy":
            img_src_replace = f"\\1 {urlparse(config.WMTS_SERVER_URL).netloc} {urlparse(config.GEOSERVER_URL).netloc};"
            connect_src_replace = f"\\1 {urlparse(config.WFS_SERVER_URL).netloc} *.google-analytics.com;"
            header.default = re.sub(r"(img-src[^;]+);", img_src_replace, header.default)
            header.default = re.sub(r"(connect-src[^;]+);", connect_src_replace, header.default)
        elif header.header_name == "Cross-Origin-Embedder-Policy":
            header.default = "same-origin"
    headers.init_app(app, UIDefaultHeaders)

    if config.STATIC_ASSETS_MODE == "production":
        cachebust_static_assets.init_app(app)
        if config.STATIC_ASSETS_GZIP == "yes":
            gzip_static_assets.init_app(app)

    # Flask-babel for translation handling
    babel.init_app(app, locale_selector=get_locale)
    # Flask-babel-js for javascript translations
    babel_js.init_app(app)

    # Override default callables to allow for pgettext and npgettext since Flask-babel doesn't support them yet
    app.jinja_env.install_gettext_callables(
        gettext=lambda s: get_translations().ugettext(s),
        ngettext=lambda s, p, n: get_translations().ungettext(s, p, n),
        newstyle=True,
        pgettext=lambda c, s: get_translations().upgettext(c, s),
        npgettext=lambda c, s, p, n: get_translations().unpgettext(c, s, p, n),
    )

    # Flask-session
    sess.init_app(app)

    # Use pickle serializer
    app.session_interface.serializer = PickleSerializer(app)

    # All done!
    app.logger.info("Extensions registered")


class PickleSerializer(Serializer):

    def __init__(self, app: Flask):
        self.app: Flask = app

    def _get_signer(self, app: Flask) -> Signer:
        if not hasattr(app, "secret_key") or not app.secret_key:
            raise KeyError("SECRET_KEY must be set")
        return Signer(
            app.secret_key, salt="flask-session-signing", key_derivation="hmac"
        )

    def _unsign(self, sess: bytes) -> bytes:
        signer = self._get_signer(self.app)
        return signer.unsign(sess)

    def _sign(self, sess: bytes) -> bytes:
        signer = self._get_signer(self.app)
        return signer.sign(sess)

    def encode(self, session: ServerSideSession) -> bytes:
        """Serialize the session data."""
        try:
            return self._sign(pickle.dumps(dict(session)))
        except Exception as e:
            self.app.logger.error(f"Failed to serialize session data: {e}")
            raise

    def decode(self, serialized_data: bytes) -> dict:
        """Deserialize the session data."""
        return pickle.loads(self._unsign(serialized_data))
