from flask import current_app, g


class StatProvService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.base_url = "{}/statutory-provisions".format(config["MAINTAIN_API_URL"])

    def get(self, selectable):
        url = self.base_url
        current_app.logger.info("Calling maintain api via this URL: %s", url)

        return g.requests.get(
            "{}".format(url),
            headers={"Content-Type": "application/json"},
            params={"selectable": selectable},
        ).json()

    def get_history(self):
        url = self.base_url + "/history"
        current_app.logger.info("Calling maintain api via this URL: %s", url)

        return g.requests.get("{}".format(url), headers={"Content-Type": "application/json"}).json()
