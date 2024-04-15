import base64
import urllib.parse

from flask import current_app, g


class AddressesService(object):
    """Service class for making requests to /search/addresses endpoint"""

    def __init__(self, config):
        self.config = config
        self.url = "{}/search/addresses".format(config["SEARCH_API_URL"])

    # Call the search api using postcode, uprn, or free text depending on input.
    def get_by(self, type, value, index_map=False, value_2=None):
        url_value = urllib.parse.quote_from_bytes(base64.urlsafe_b64encode(value.encode("UTF8")))
        relative_path = "/" + type + "/" + url_value
        params = {"base64": "true"}
        if index_map:
            params["index_map"] = "true"
        if value_2:
            params["value_2"] = value_2
        request_path = self.url + relative_path
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        return g.requests.get(request_path, params=params)
