from urllib.parse import quote_plus

from flask import g
from flask_babel import gettext as _
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.middleware.proxy_fix import ProxyFix

from server import config
from server.landregistry_flask import LandRegistryFlask
from server.services.back_link_history import show_back_link
from server.utils.base64_cookie import check_valid_base64_json_cookie
from server.utils.geoserver_token import geoserver_token
from server.utils.repeat_searches import (
    has_free_searches_to_repeat,
    has_paid_searches_to_repeat,
)

app = LandRegistryFlask(
    __name__,
    template_folder="templates",
    static_folder="assets/dist",
    static_url_path="/ui",
)


# Set Jinja up to be able to load templates from packages (See gadget-govuk-ui for a full example)
app.jinja_loader = ChoiceLoader(
    [
        PackageLoader("server"),
        PrefixLoader(
            {
                "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                "hmlr_frontend_jinja": PackageLoader("hmlr_frontend_jinja"),
            }
        ),
    ]
)
app.jinja_env.autoescape = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.jinja_env.add_extension("jinja2.ext.do")
app.jinja_env.filters["quote_plus"] = quote_plus
app.config.from_pyfile("config.py")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=0, x_prefix=0)


@app.context_processor
def inject_global_values():
    """Inject global template values

    Use this to inject values into the templates that are used globally.
    This might be things such as the current username
    """
    if g.locale == "cy":
        contact_url = config.CONTACT_US_WELSH_URL
    else:
        contact_url = config.CONTACT_US_URL

    return dict(
        service_name=_("Search for local land charges"),
        contact_url=contact_url,
        geoserver_token=geoserver_token,
        show_back_link=show_back_link,
        check_valid_base64_json_cookie=check_valid_base64_json_cookie,
        htmlLang=g.locale,
        has_free_searches_to_repeat=has_free_searches_to_repeat,
        has_paid_searches_to_repeat=has_paid_searches_to_repeat,
    )
