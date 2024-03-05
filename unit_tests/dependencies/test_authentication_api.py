from landregistry.exceptions import ApplicationError
from flask import g, current_app, session
from unittest.mock import MagicMock
from unittest import TestCase
from server import main
from server.dependencies.authentication_api import AuthenticationApi
from unit_tests.utilities_tests import super_test_context
from jwt_validation.models import JWTPayload, SearchPrinciple


class TestAuthenticationApi(TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        main.app.config["WTF_CSRF_ENABLED"] = False
        main.app.testing = True

    def test_authentication_error(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 500
            g.requests.request.return_value = response
            g.trace_id = "1"
            with self.assertRaises(ApplicationError) as context:
                AuthenticationApi().authenticate("a password", "a userid")

            self.assertEqual(context.exception.http_code, 500)

    def test_authentication_fail(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 400
            g.requests.request.return_value = response
            g.trace_id = "1"

            status, result = AuthenticationApi().authenticate("a password", "a userid")

            self.assertFalse(status)

    def test_authentication_ok(self):
        with super_test_context(main.app):
            principle = SearchPrinciple("123", "A first name", "A surname", email="an@email.com")
            jwt_payload = JWTPayload("iss", "aud", "exp", "iat", "sub", "source", principle)
            session["jwt_payload"] = jwt_payload
            response = MagicMock()
            response.status_code = 200
            g.requests.request.return_value = response
            g.session = MagicMock()
            g.session.user.email = "anid"
            g.trace_id = "1"

            result = AuthenticationApi().authenticate("a password")

            self.assertTrue(result)
            g.requests.request.assert_called_with(
                "post",
                "{}/v2.0/authentication".format(current_app.config["AUTHENTICATION_URL"]),
                data={"username": "an@email.com", "password": "a password", "source": "search"},
            )
