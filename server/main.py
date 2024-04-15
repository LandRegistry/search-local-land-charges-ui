# This file is the entry point.
# First we import the app object, which will get initialised as we do it. Then import methods we're about to use.
from urllib.parse import urlparse

import requests
from flask import g, request, session

from server.app import app
from server.blueprints import register_blueprints
from server.extensions import enhanced_logging, register_extensions
from server.locale import get_locale
from server.services.back_link_history import add_history


class RequestsSessionTimeout(requests.Session):
    """Custom requests session class to set some defaults on g.requests"""

    def request(self, *args, **kwargs):
        # Set a default timeout for the request.
        # Can be overridden in the same way that you would normally set a timeout
        # i.e. g.requests.get(timeout=5)
        if not kwargs.get("timeout"):
            kwargs["timeout"] = app.config["DEFAULT_TIMEOUT"]

        return super(RequestsSessionTimeout, self).request(*args, **kwargs)


def before_request():
    # is_xhr has been deprecated and removed so recreate for backwards compatibility
    request.is_xhr = request.environ.get("HTTP_X_REQUESTED_WITH", "").lower() == "xmlhttprequest"
    # Sets the transaction trace id on the global object if provided in the HTTP header from the caller.
    # Generate a new one if it has not.
    g.trace_id = enhanced_logging.tracer.current_trace_id

    # We also create a session-level requests object for the app to use with the header pre-set, so other APIs
    # will receive it. These lines can be removed if the app will not make requests to other LR APIs!
    g.requests = RequestsSessionTimeout()
    g.requests.headers.update({"X-Trace-ID": g.trace_id})
    g.requests.headers.update({"Source": "SEARCH"})

    if "/health" in request.path:
        return

    if "jwt_token" in session:
        g.requests.headers.update({"Authorization": "Bearer " + session["jwt_token"]})

    g.locale = str(get_locale())
    g.requests.headers.update({"Locale": g.locale})
    # Only record the referrer in the history if we're hitting an endpoint we're interested in
    if (
        request.referrer != request.url
        and request.referrer
        and request.endpoint
        and request.endpoint
        not in [
            "static",
            "babel_catalog",
            "main.back",
            "language.change_language",
            "ajax.ajax_llc1_pdf_poll",
        ]
        and urlparse(request.referrer).netloc == urlparse(request.url).netloc
    ):
        add_history(request.referrer)


# Now we register any extensions we use into the app
register_extensions(app)

app.before_request(before_request)

# Finally we register our blueprints to get our routes up and running.
register_blueprints(app)
