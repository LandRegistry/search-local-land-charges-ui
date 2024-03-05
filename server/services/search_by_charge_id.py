import re

from server.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from landregistry.exceptions import ApplicationError
from flask_babel import gettext

CHARGE_NUMBER_REGEX = '^(llc|LLC)(-)?([0123456789BCDFGHJKLMNPQRSTVWXYZ]){1,6}$'


class SearchByChargeId(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, config):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        local_land_charge_service = LocalLandChargeService(config)

        search_query = search_query.strip().upper()

        if re.match(CHARGE_NUMBER_REGEX, search_query):
            self.logger.info("Valid charge id provided: %s", search_query)
            response = local_land_charge_service.get_by_charge_number(search_query)
        else:
            self.logger.info("Invalid charge id provided: %s", search_query)
            response_data = {
                "search_message": gettext("Invalid charge id. Try again"),
                "status": "error"
            }

            return response_data

        return self.process_search_response(response)

    def process_search_response(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")

            response_data = {
                "data": response.json(),
                "status": "success"
            }

            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": gettext("Enter a valid postcode or location"),
                "status": "error"
            }

            return response_data
        else:
            raise ApplicationError("Error returned from a get_by function", "SEARCHID01", 500)

    def validate_request(self, search_query):
        if not search_query:
            self.logger.info("No search query provided")
            response_data = {
                "search_message": gettext("Enter a postcode or location"),
                "status": "error"
            }

            return response_data
