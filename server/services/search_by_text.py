import re

from flask_babel import gettext
from landregistry.exceptions import ApplicationError

from server.dependencies.search_api.address_service import AddressesService
from server.dependencies.search_api.local_land_charge_service import (
    LocalLandChargeService,
)
from server.dependencies.search_api.search_type import SearchType

POSTCODE_REGEX = "^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}$"
UPRN_REGEX = "^[0-9]{6,12}$"
CHARGE_NUMBER_REGEX = "^(llc|LLC)(-)?([0123456789BCDFGHJKLMNPQRSTVWXYZ]){1,6}$"


class SearchByText(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, config):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        addresses_service = AddressesService(config)
        local_land_charge_service = LocalLandChargeService(config)

        search_query = search_query.strip().upper()

        if re.match(POSTCODE_REGEX, search_query):
            self.logger.info("Valid postcode provided: %s", search_query)
            response = addresses_service.get_by(SearchType.POSTCODE.value, search_query)
        elif re.match(UPRN_REGEX, search_query):
            self.logger.info("Valid UPRN provided: %s", search_query)
            response = addresses_service.get_by(SearchType.UPRN.value, search_query)
        elif re.match(CHARGE_NUMBER_REGEX, search_query):
            self.logger.info("Valid charge number provided: %s", search_query)
            response = local_land_charge_service.get_by_charge_number(search_query)
        else:
            self.logger.info("Free text provided: %s", search_query)
            response = addresses_service.get_by(SearchType.TEXT.value, search_query)

        return self.process_search_response(response)

    def process_search_response(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")

            response_data = {"data": response.json(), "status": "success"}

            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": gettext("Enter a valid postcode or location"),
                "status": "error",
            }

            return response_data
        else:
            raise ApplicationError("Error returned from a get_by function", "SEARCHTXT01", 500)

    def validate_request(self, search_query):
        if not search_query:
            self.logger.info("No search query provided")
            response_data = {
                "search_message": gettext("Enter a postcode or location"),
                "status": "error",
            }

            return response_data
