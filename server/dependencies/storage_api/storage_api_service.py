from flask import current_app, g
from landregistry.exceptions import ApplicationError


class StorageAPIService(object):
    """Service class for making requests to /search/addresses endpoint."""

    def __init__(self, config):
        self.config = config
        self.url = config["STORAGE_API_URL"]

    def get_external_url_for_document_url(self, document_url):
        current_app.logger.info("Generate external URL for document_url {}".format(document_url))
        request_path = "{}{}/external-url".format(self.url, document_url)

        current_app.logger.info("Calling storage api via this URL: {}".format(request_path))
        response = g.requests.get(request_path)

        current_app.logger.info("Calling storage api responded with status: {}".format(response.status_code))

        if response.status_code == 200:
            json = response.json()
            return json["external_reference"]
        if response.status_code == 404:
            current_app.logger.warning("Failed to find external document url for url {}".format(document_url))
            raise ApplicationError("Failed to find external document url", "STORE01", 404)

        current_app.logger.warning(
            "Failed to get external url - TraceID : {} - Status: {}, Message: {}".format(
                g.trace_id, response.status_code, response.text
            )
        )
        raise ApplicationError("Failed to get external url", "STORE02", 500)

    def get_external_url(self, file, bucket, subdirectories=None):
        current_app.logger.info("Generate external URL for {}".format(file))
        params = {}
        if subdirectories:
            params["subdirectories"] = subdirectories

        request_path = "{}/{}/{}/external-url".format(self.url, bucket, file)

        current_app.logger.info("Calling storage api via this URL: {}".format(request_path))
        response = g.requests.get(request_path, params=params)

        current_app.logger.info("Calling storage api responded with status: {}".format(response.status_code))

        if response.status_code == 200:
            json = response.json()
            return json["external_reference"]
        if response.status_code == 404:
            current_app.logger.warning("Failed to find external document url for file {}".format(file))
            raise ApplicationError("Failed to find external document url", "STORE03", 404)

        current_app.logger.warning(
            "Failed to get external url - TraceID : {} - Status: {}, Message: {}".format(
                g.trace_id, response.status_code, response.text
            )
        )
        raise ApplicationError("Failed to get external url", "STORE04", 500)
