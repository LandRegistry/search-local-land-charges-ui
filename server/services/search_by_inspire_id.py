from server.dependencies.inspire_api.inspire_service import InspireService


class SearchByInspireId(object):
    def __init__(self, logger, config):
        self.logger = logger
        self.inspire_service = InspireService(config)

    def process(self, inspire_id):
        response = dict()

        self.logger.info("Searching for charge by inspire ID {}".format(inspire_id))
        search_response = self.inspire_service.get_llc_by_inspire_id(inspire_id)

        response["status"] = search_response.status_code
        if search_response.status_code == 200:
            response["data"] = search_response.json()

        return response
