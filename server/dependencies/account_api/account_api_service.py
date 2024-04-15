import json
import urllib

from flask import g, session
from landregistry.exceptions import ApplicationError


class AccountApiService(object):
    """Service class for making requests to Account API endpoints."""

    def __init__(self, current_app):
        self.logger = current_app.logger
        self.config = current_app.config
        self.url = current_app.config["ACCOUNT_API_URL"]

    def register(self, first_name, surname, email, password):
        body = {
            "first_name": first_name,
            "surname": surname,
            "email": email,
            "password": password,
        }

        url = self.url + "/users"
        self.logger.info("Calling Account API at {}".format(url))
        response = g.requests.post(url, json=body)

        if response.status_code == 409:
            self.logger.warning("Account already exists for this email address")
            return {
                "status": response.status_code,
                "message": "Account already exists for this email address",
            }

        if response.status_code == 400 and "Password is blacklisted" in response.text:
            self.logger.warning("Password is blacklisted")
            return {
                "status": response.status_code,
                "message": "Password is blacklisted",
            }

        if response.status_code != 201:
            self.logger.error("Error registering user")
            raise ApplicationError(response.status_code)

        self.logger.info("Successfully registered user")
        return {
            "status": response.status_code,
            "message": "Account successfully created",
            "data": response.json(),
        }

    def set_password(self, token, user_id, password):
        url = "{}/users/{}".format(self.url, urllib.parse.quote_plus(user_id))
        payload = json.dumps({"password": password, "status": self.config["NEW_USER_STATUS"]})
        headers = {
            "Content-Type": "application/merge-patch+json",
            "X-reset-token": token,
        }

        response = g.requests.patch(url, data=payload, headers=headers)

        return response

    def change_password(self, password):
        user_id = session["profile"]["user_id"]

        url = "{}/users/{}".format(self.url, urllib.parse.quote_plus(user_id))
        payload = json.dumps({"password": password})
        headers = {"Content-Type": "application/merge-patch+json"}

        response = g.requests.patch(url, data=payload, headers=headers)

        return response

    def change_name(self, first_name, surname):
        user_id = session["profile"]["user_id"]

        url = "{}/users/{}".format(self.url, urllib.parse.quote_plus(user_id))
        payload = json.dumps({"first_name": first_name, "surname": surname})
        headers = {"Content-Type": "application/merge-patch+json"}

        response = g.requests.patch(url, data=payload, headers=headers)

        return response

    def validate_token(self, token):
        verify_request = g.requests.get(self.url + "/password_reset/" + token)

        if verify_request.status_code == 200:
            return verify_request.json()
        return None

    def request_reset_password_email(self, email):
        self.logger.info("Reset request")
        username_json = {"username": email}

        reset_password_email_request = g.requests.post(
            "{}/password_reset".format(self.url),
            data=json.dumps(username_json),
            headers={"Content-Type": "application/json"},
        )

        if reset_password_email_request.status_code != 201:
            self.logger.error(
                "Error requesting password token: code: {} message: {}".format(
                    str(reset_password_email_request.status_code),
                    reset_password_email_request.text,
                )
            )

        return reset_password_email_request

    def activate_user(self, activate_token, user_id):
        url = "{}/users/{}".format(self.url, urllib.parse.quote_plus(user_id))
        payload = json.dumps({"status": "Active"})
        headers = {
            "Content-Type": "application/merge-patch+json",
            "X-reset-token": activate_token,
        }

        response = g.requests.patch(url, data=payload, headers=headers)

        return response

    def resend_email(self, email):
        url = "{}/users/resend-email".format(self.url)
        response = g.requests.post(url, json={"username": email})
        if response.status_code != 200:
            self.logger.error(
                "Error requesting email resend, code: {} message: {}".format(str(response.status_code), response.text)
            )
        return response
