from flask import current_app, g


class CategoryService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.base_url = "{}/categories".format(config['MAINTAIN_API_URL'])

    def get(self):
        current_app.logger.info("Calling maintain api via this URL: %s", self.base_url)

        return g.requests.get("{}".format(self.base_url),
                              headers={'Content-Type': 'application/json'}).json()

    def get_category(self, category):
        url = '{}/{}'.format(self.base_url, category)
        current_app.logger.info("Calling maintain api via this URL: %s", url)

        return g.requests.get("{}".format(url),
                              headers={'Content-Type': 'application/json'})

    def get_sub_category(self, category, sub_category):
        url = '{}/{}/sub-categories/{}'.format(self.base_url, category, sub_category)
        current_app.logger.info("Calling maintain api via this URL: %s", url)

        return g.requests.get("{}".format(url),
                              headers={'Content-Type': 'application/json'})

    def get_all_and_sub(self):
        url = '{}/all'.format(self.base_url)

        current_app.logger.info("Calling maintain api via this URL: %s", url)

        return g.requests.get(url,
                              headers={'Content-Type': 'application/json'}).json()
