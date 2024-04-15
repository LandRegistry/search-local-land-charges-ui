from flask import current_app, g


class InspireService(object):
    """Service class for making requests to the inspire API."""

    def __init__(self, config):
        self.config = config
        self.base_url = "{}/local-land-charge-id".format(config["INSPIRE_API_ROOT"])

    def get_llc_by_inspire_id(self, inspire_id):
        url = "{}/{}".format(self.base_url, inspire_id)
        current_app.logger.info("Calling inspire api via this URL: {}".format(url))

        return g.requests.get(url)
