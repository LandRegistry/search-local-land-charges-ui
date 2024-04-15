import re

from flask_babel import gettext
from landregistry.exceptions import ApplicationError

from server.dependencies.search_api.address_service import AddressesService
from server.dependencies.search_api.search_type import SearchType

POSTCODE_REGEX = (
    "^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z]"
    "[A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|"
    "([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$"
)


class SearchByPostcode(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, config):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        addresses_service = AddressesService(config)

        search_query = search_query.strip().upper()

        if self.search_valid(search_query, POSTCODE_REGEX):
            self.logger.info("Valid postcode provided: %s", search_query)
            response = addresses_service.get_by(SearchType.POSTCODE.value, search_query)
        else:
            self.logger.info("Invalid postcode provided: %s", search_query)
            response_data = {
                "search_message": gettext("Invalid postcode. Try again"),
                "status": "error",
            }

            return response_data

        return self.process_search_response(response)

    def search_valid(self, search_query, regex):
        search_term_valid = re.match(regex, search_query)

        return search_term_valid is not None

    def build_response_data(self, response):
        addresses = []

        for item in response:
            address = {
                "address": item["address"],
                "geometry": item["geometry"],
                "uprn": item["uprn"],
            }
            addresses.append(address)

        return addresses

    def process_search_response(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")

            addresses = self.build_response_data(response.json())

            response_data = {"data": addresses, "status": "success"}

            return response_data
        elif response.status_code == 400:
            self.logger.info("Invalid search. {0}".format(response.json()))
            response_data = {
                "search_message": gettext("Invalid postcode. Try again"),
                "status": "error",
            }
            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": gettext("No results found"),
                "status": "error",
            }

            return response_data
        else:
            raise ApplicationError("Error returned from a get_by function", "SEARCHPC01", 500)

    def validate_request(self, search_query):
        if not search_query:
            self.logger.info("No search query provided")
            response_data = {
                "search_message": gettext("Enter a postcode"),
                "status": "error",
            }

            return response_data
