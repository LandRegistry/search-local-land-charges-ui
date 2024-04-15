import base64
import json
import urllib
from unittest import TestCase
from unittest.mock import MagicMock

from flask import current_app, g, session
from landregistry.exceptions import ApplicationError

from server import main
from server.dependencies.account_api.account_api_service import AccountApiService
from unit_tests.utilities_tests import super_test_context


class TestAccountApiService(TestCase):
    def setUp(self):
        main.app.config["TESTING"] = True
        main.app.config["WTF_CSRF_ENABLED"] = False
        main.app.testing = True

    def test_register_successful(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 201
            g.requests.post.return_value = response

            url = "abc"
            mock_current_app = MagicMock()
            mock_current_app.config = {"ACCOUNT_API_URL": url}

            first_name = "name"
            surname = "surname"
            email = "email@email.com"
            password = "apassword"

            account_service = AccountApiService(mock_current_app)
            register_response = account_service.register(first_name, surname, email, password)

            expected_request_body = {
                "first_name": first_name,
                "surname": surname,
                "email": email,
                "password": password,
            }

            g.requests.post.assert_called_with(url + "/users", json=expected_request_body)
            response.json.assert_called()
            self.assertEqual(register_response.get("status"), response.status_code)

    def test_register_email_exists(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 409
            g.requests.post.return_value = response

            url = "abc"
            mock_current_app = MagicMock()
            mock_current_app.config = {"ACCOUNT_API_URL": url}

            first_name = "name"
            surname = "surname"
            email = "email@email.com"
            password = "apassword"

            account_service = AccountApiService(mock_current_app)
            register_response = account_service.register(first_name, surname, email, password)

            expected_request_body = {
                "first_name": first_name,
                "surname": surname,
                "email": email,
                "password": password,
            }

            g.requests.post.assert_called_with(url + "/users", json=expected_request_body)
            self.assertEqual(register_response.get("status"), response.status_code)
            self.assertEqual(
                register_response.get("message"),
                "Account already exists for this email address",
            )

    def test_register_fail(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 500
            g.requests.post.return_value = response

            url = "abc"
            mock_current_app = MagicMock()
            mock_current_app.config = {"ACCOUNT_API_URL": url}

            first_name = "name"
            surname = "surname"
            email = "email@email.com"
            password = "apassword"

            account_service = AccountApiService(mock_current_app)

            with self.assertRaises(ApplicationError) as context:
                account_service.register(first_name, surname, email, password)

            self.assertEqual(context.exception.http_code, 500)

    def test_create_password(self):
        with super_test_context(main.app):
            g.requests.patch = MagicMock()
            mock_user_id = "abc"
            mock_token = create_token(mock_user_id, "abc")
            mock_password = "Unittest!1"
            account_api_service = AccountApiService(current_app)
            account_api_service.set_password(mock_token, mock_user_id, mock_password)

            g.requests.patch.assert_called_with(
                "{}/users/{}".format(
                    current_app.config["ACCOUNT_API_URL"],
                    urllib.parse.quote_plus(mock_user_id),
                ),
                data=json.dumps(
                    {
                        "password": mock_password,
                        "status": current_app.config["NEW_USER_STATUS"],
                    }
                ),
                headers={
                    "Content-Type": "application/merge-patch+json",
                    "X-reset-token": mock_token,
                },
            )

    def test_change_password(self):
        with super_test_context(main.app):
            g.requests.patch = MagicMock()

            mock_user_id = "abc"
            g.session = MagicMock()
            g.session.user.id = mock_user_id
            mock_password = "Unittest!1"
            session["profile"] = {"user_id": mock_user_id}
            account_api_service = AccountApiService(current_app)
            account_api_service.change_password(mock_password)

            g.requests.patch.assert_called_with(
                "{}/users/{}".format(
                    current_app.config["ACCOUNT_API_URL"],
                    urllib.parse.quote_plus(mock_user_id),
                ),
                data=json.dumps({"password": mock_password}),
                headers={"Content-Type": "application/merge-patch+json"},
            )

    def test_change_name(self):
        with super_test_context(main.app):
            g.requests.patch = MagicMock()
            mock_user_id = "abc"
            g.session = MagicMock()
            g.session.user.id = mock_user_id
            session["profile"] = {"user_id": mock_user_id}
            account_api_service = AccountApiService(current_app)
            account_api_service.change_name("first", "last")

            g.requests.patch.assert_called_with(
                "{}/users/{}".format(
                    current_app.config["ACCOUNT_API_URL"],
                    urllib.parse.quote_plus(mock_user_id),
                ),
                data=json.dumps({"first_name": "first", "surname": "last"}),
                headers={"Content-Type": "application/merge-patch+json"},
            )

    def test_validate_token_valid(self):
        with super_test_context(main.app):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "Valid"}
            g.requests.get.return_value = mock_response

            account_api_service = AccountApiService(current_app)
            result = account_api_service.validate_token("antoken")

            self.assertTrue(result)
            g.requests.get.assert_called_with(f"{current_app.config['ACCOUNT_API_URL']}/password_reset/antoken")

    def test_validate_token_invalid(self):
        with super_test_context(main.app):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "wack"}
            g.requests.get.return_value = mock_response

            account_api_service = AccountApiService(current_app)
            result = account_api_service.validate_token("antoken")

            self.assertEqual(result, {"status": "wack"})
            g.requests.get.assert_called_with(f"{current_app.config['ACCOUNT_API_URL']}/password_reset/antoken")

    def test_request_reset_password_email_valid(self):
        with super_test_context(main.app):
            mock_response = MagicMock()
            mock_response.status_code = 201
            g.requests.post.return_value = mock_response

            account_api_service = AccountApiService(current_app)
            result = account_api_service.request_reset_password_email("anemail@address.com")

            self.assertEqual(result, mock_response)
            g.requests.post.assert_called_with(
                f"{current_app.config['ACCOUNT_API_URL']}/password_reset",
                data='{"username": "anemail@address.com"}',
                headers={"Content-Type": "application/json"},
            )

    def test_request_reset_password_email_fail(self):
        with super_test_context(main.app):
            mock_response = MagicMock()
            mock_response.status_code = 500
            g.requests.post.return_value = mock_response

            account_api_service = AccountApiService(current_app)
            result = account_api_service.request_reset_password_email("anemail@address.com")

            self.assertEqual(result, mock_response)
            g.requests.post.assert_called_with(
                f"{current_app.config['ACCOUNT_API_URL']}/password_reset",
                data='{"username": "anemail@address.com"}',
                headers={"Content-Type": "application/json"},
            )

    def test_activate_user(self):
        with super_test_context(main.app):
            account_api_service = AccountApiService(current_app)
            mock_response = MagicMock()
            g.requests.patch.return_value = mock_response
            result = account_api_service.activate_user("atoken", "auserid")
            self.assertEqual(result, mock_response)
            g.requests.patch.assert_called_with(
                f"{current_app.config['ACCOUNT_API_URL']}/users/auserid",
                data='{"status": "Active"}',
                headers={
                    "Content-Type": "application/merge-patch+json",
                    "X-reset-token": "atoken",
                },
            )

    def test_resend_email_ok(self):
        with super_test_context(main.app):
            account_api_service = AccountApiService(current_app)
            mock_response = MagicMock()
            mock_response.status_code = 200
            g.requests.post.return_value = mock_response
            result = account_api_service.resend_email("anemail")
            self.assertEqual(result, mock_response)
            g.requests.post.assert_called_with(
                f"{current_app.config['ACCOUNT_API_URL']}/users/resend-email",
                json={"username": "anemail"},
            )

    def test_resend_email_fail(self):
        with super_test_context(main.app):
            account_api_service = AccountApiService(current_app)
            mock_response = MagicMock()
            mock_response.status_code = 500
            g.requests.post.return_value = mock_response
            result = account_api_service.resend_email("anemail")
            self.assertEqual(result, mock_response)
            g.requests.post.assert_called_with(
                f"{current_app.config['ACCOUNT_API_URL']}/users/resend-email",
                json={"username": "anemail"},
            )
            current_app.logger.error.assert_called()


def create_token(user_id, token):
    payload = {"user_id": user_id, "token": token}
    payload_string = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_bytes = payload_string.encode("UTF-8")
    base64_bytes = base64.urlsafe_b64encode(payload_bytes)
    return base64_bytes.decode()
