from flask import current_app, g


class LocalLandChargeService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.base_url = "{}/search/local_land_charges".format(config["SEARCH_API_URL"])

    def request(self, url, params=None):
        current_app.logger.info("Calling search api via this URL: %s", url)
        return g.requests.get(url, params=params)

    def get(self, encoded_bounding_box, results_filter=None):
        current_app.logger.info("Calling search api by area via this URL: %s", self.base_url)

        params = {
            "maxResults": self.config["SEARCH_API_MAX_RESULTS"],
            "filter_sensitive_geometry": "true",
        }

        if results_filter is not None:
            params["filter"] = results_filter

        return g.requests.post(
            "{}".format(self.base_url),
            params=params,
            data=encoded_bounding_box,
            headers={"Content-Type": "application/json"},
        )

    def get_by_charge_number(self, charge_number):
        request_path = self.base_url + "/" + charge_number
        return self.request(request_path)

    def get_by_reference_number(self, reference_number):
        params = {"furtherInformationReference": reference_number}
        return self.request(self.base_url, params)

    def get_history_for_charge(self, charge_number):
        request_path = self.base_url + "/" + charge_number + "/history"
        return self.request(request_path)
