from flask import current_app, g


class CategoryService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.base_url = "{}/search/categories".format(config['SEARCH_API_URL'])

    def get(self):
        current_app.logger.info("Calling search api category via this URL: %s", self.base_url)

        return g.requests.get("{}".format(self.base_url),
                              headers={'Content-Type': 'application/json'}).json()
