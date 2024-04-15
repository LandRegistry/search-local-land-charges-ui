from flask import current_app, session
from landregistry.exceptions import ApplicationError

from server import config
from server.dependencies.api_client import ApiClient


class AuthenticationApi(ApiClient):
    """API client to interact with the Authentication API."""

    api_domain = config.AUTHENTICATION_URL
    endpoints = {"authentication": {"post": "/v2.0/authentication"}}

    def authenticate(self, password, user_id=None):
        current_app.logger.info("Calling Authentication API")
        api_endpoint = self.get_endpoint(controller="authentication", method="post")
        if not user_id:
            user_id = session["jwt_payload"].principle.email
        payload = {"username": user_id, "password": password, "source": "search"}
        req = self.make_request(api_endpoint, "post", data=payload)

        if req.status_code == 200:
            return True, req.text
        elif req.status_code == 400:
            return False, req.json()

        raise ApplicationError("Failure during authentication", "AUTH01", 500)
