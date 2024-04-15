import json

from flask import current_app, g
from landregistry.exceptions import ApplicationError

from server.config import LOCAL_AUTHORITY_API_URL


class LocalAuthorityAPIService(object):
    @staticmethod
    def get_organisations(params=None):
        if params is None:
            params = {"organisation_type": "la"}
        current_app.logger.info("Attempting to get organisations")
        response = g.requests.get("{}/v1.0/organisations".format(LOCAL_AUTHORITY_API_URL), params=params)

        if response.status_code != 200:
            current_app.logger.exception(
                "Failed to get organisations from local-authority-api. Message: {}".format(response.text)
            )
            raise ApplicationError("Failed to retrieve organisations", "LAUTH01", 500)

        return response.json()

    @staticmethod
    def get_authorities_by_extent(bounding_box):
        request_path = "{}/v1.0/{}".format(LOCAL_AUTHORITY_API_URL, "local-authorities")
        current_app.logger.info("Calling local authority api by area via this URL: %s", request_path)
        response = g.requests.post(
            request_path,
            data=json.dumps(bounding_box),
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            current_app.logger.info("Authorities found")
            return response.json()
        elif response.status_code == 404:
            current_app.logger.info("No authorities found")
            return {}
        else:
            raise ApplicationError("Error occurred when getting authorities", "LAUTH02", 500)

    @staticmethod
    def get_bounding_box(authority):
        endpoint = "local-authorities/" + authority + "/bounding_box"
        request_path = "{}/v1.0/{}".format(LOCAL_AUTHORITY_API_URL, endpoint)

        current_app.logger.info("Calling local authority api via this URL: %s", request_path)
        return g.requests.get(request_path)

    @staticmethod
    def plus_minus_buffer(extent):
        current_app.logger.info("Posting extent to discover migration status")
        response = g.requests.post(
            "{}/v1.0/local-authorities/plus_minus_buffer".format(LOCAL_AUTHORITY_API_URL),
            data=json.dumps(extent),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            current_app.logger.info("Successfully determined if the given extent is within a migrated area")
            return response.json()
        elif response.status_code == 400:
            raise ApplicationError("local-authority-api reports invalid request", "LAUTH03", 400)
        else:
            raise ApplicationError(
                "Failed to determine if the given extent is within a migrated area",
                "LAUTH04",
                400,
            )
