from urllib.parse import urljoin

import requests
from flask import current_app, g
from landregistry.exceptions import ApplicationError


class ApiClient:
    """Base client to interact with APIs."""

    def __init__(self, api_domain=None):
        """Bind a custom API domain to the object."""
        if api_domain is not None:
            self.api_domain = api_domain

    def get_endpoint(self, controller, method):
        """Return an endpoint URL for a given API controller and method.

        Inputs:
            method (str) -- The desired HTTP method endpoint to be returned.
            controller (str) -- The desired controller for the endpoint to be returned.

        Returns:
            str -- The URL for the specified endpoint.
        """
        return urljoin(self.api_domain, self.endpoints[controller][method])

    def make_request(self, url, http_method, *args, **kwargs):
        """Make a request to the API using using requests.request and catch request exceptions.

        Inputs:
            url (str) -- The URL to make the request to.
            http_method (str) -- The HTTP method to use when making the request (one of 'GET', 'POST', 'PUT' etc)
            *args -- Additional args supported by requests.request
            **kwargs -- Additional kwargs supported by requests.request

        Returns:
            requests.models.Response -- The response to the request.

        Raises:
            ApplicationError -- When there is an error receiving a response from the underlaying requests library.
        """
        current_app.logger.info(
            "Making {} request to URL: {}".format(
                http_method.upper(),
                url
            )
        )

        try:
            req = g.requests.request(http_method.lower(), url, *args, **kwargs)
        except requests.exceptions.RequestException as execinfo:
            raise ApplicationError(str(execinfo)) from execinfo
        return req
