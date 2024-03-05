import re

from server.dependencies.search_api.address_service import AddressesService
from server.dependencies.search_api.search_type import SearchType
from landregistry.exceptions import ApplicationError
from flask_babel import gettext

USRN_REGEX = r'^\d+$'


class SearchByUsrn(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, postcode, config):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        addresses_service = AddressesService(config)

        search_query = search_query.strip().upper()
        postcode = postcode.strip().upper()

        if self.search_valid(search_query, USRN_REGEX):
            self.logger.info("Valid usrn provided: %s", search_query)
            response = addresses_service.get_by(SearchType.USRN.value, search_query, value_2=postcode)
        else:
            self.logger.info("Invalid usrn provided: %s", search_query)
            response_data = {
                "search_message": gettext("Invalid usrn, please try again"),
                "status": "error"
            }

            return response_data

        return self.process_search_response(response)

    def search_valid(self, search_query, regex):
        search_term_valid = re.match(regex, search_query)

        return search_term_valid is not None

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
                "search_message": gettext("No results found"),
                "status": "error"
            }

            return response_data
        else:
            raise ApplicationError("Error returned from a get_by function", "SEARCHUSRN01", 500)

    def validate_request(self, search_query):
        if not search_query:
            self.logger.info("No search query provided")
            response_data = {
                "search_message": gettext("Enter a usrn"),
                "status": "error"
            }

            return response_data
