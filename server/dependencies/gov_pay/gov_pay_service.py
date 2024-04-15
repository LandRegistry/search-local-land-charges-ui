from flask import current_app, g, url_for
from landregistry.exceptions import ApplicationError


class GovPayService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.url = self.config["GOV_PAY_URL"]

    def request_payment(self, amount, reference, description, enc_search_id):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.config["GOV_PAY_API_KEY"],
        }
        body = {
            "amount": amount,
            "reference": reference,
            "description": description,
            "return_url": url_for("paid_search.process_pay", enc_search_id=enc_search_id, _external=True),
            "language": g.locale,
        }

        current_app.logger.info("Requesting gov payment with reference {}".format(reference))
        payment_request = g.requests.post(self.url, json=body, headers=headers)

        if payment_request.status_code != 201:
            raise ApplicationError(
                f"Fail response from gov pay API: {repr(payment_request.json())}",
                "GOVP01",
                payment_request.status_code,
            )
        else:
            return payment_request.json()

    def get_payment(self, payment_id):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.config["GOV_PAY_API_KEY"],
        }

        current_app.logger.info("Finding gov payment with id {}".format(payment_id))
        payment_info = g.requests.get(self.url + "/" + payment_id, headers=headers)

        if payment_info.status_code != 200:
            raise ApplicationError(
                f"Fail response from gov pay API: {repr(payment_info.json())}",
                "GOVP01",
                payment_info.status_code,
            )
        else:
            return payment_info.json()
