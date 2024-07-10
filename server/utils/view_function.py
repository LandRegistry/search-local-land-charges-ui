from urllib.parse import urlparse
from werkzeug.routing import RequestRedirect
from werkzeug.exceptions import MethodNotAllowed, NotFound

from server.main import app


def get_view_function(url, method='GET'):
    """Match a url and return the view and arguments
    it will be called with, or None if there is no view.
    """

    parsed_url = urlparse(url)

    adapter = app.url_map.bind(parsed_url.netloc)

    relative_url = parsed_url.path
    if parsed_url.query:
        relative_url += f"?{parsed_url.query}"
    if parsed_url.fragment:
        relative_url += f"#{parsed_url.fragment}"

    try:
        match = adapter.match(relative_url, method=method)
    except RequestRedirect as e:
        # recursively match redirects
        return get_view_function(e.new_url, method)
    except (MethodNotAllowed, NotFound):
        # no match
        return None

    try:
        # return the view function and arguments
        return app.view_functions[match[0]], match[1]
    except KeyError:
        # no view is associated with the endpoint
        return None
