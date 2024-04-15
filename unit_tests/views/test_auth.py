import base64
from unittest import TestCase
from unittest.mock import patch

from flask import redirect, session, url_for
from jwt_validation.models import JWTPayload, SearchPrinciple

from server.app import app
from server.views.auth import authenticated
from unit_tests.utilities_tests import super_test_context


class TestAuth(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()

    def test_login(self):
        response = self.client.get(url_for("auth.login", requestedpath="anurl"))

        self.assertEqual(
            response.location,
            url_for(
                "sign_in.handle_sign_in",
                redirect_uri=url_for("auth.authorized", requestedpath="anurl", _external=True),
            ),
        )

    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}
        response = self.client.get(url_for("auth.logout"))
        self.assertEqual(response.location, url_for("index.index_page", _external=True))
        with self.client.session_transaction() as sess:
            self.assertNotIn("profile", sess)

    @patch("server.views.auth.validate")
    def test_authorized_base64_requestedpath(self, mock_validate):
        with self.client.session_transaction() as sess:
            sess["jwt_token"] = "atoken"
        principle = SearchPrinciple("123", "A first name", "A surname")
        jwt_payload = JWTPayload("iss", "aud", "exp", "iat", "sub", "source", principle)
        mock_validate.return_value = jwt_payload
        response = self.client.get(
            url_for(
                "auth.authorized",
                requestedpath=base64.urlsafe_b64encode("base64".encode()),
            )
        )
        self.assertEqual(response.location, "base64")

    @patch("server.views.auth.validate")
    def test_authorized_no_requestedpatch(self, mock_validate):
        with self.client.session_transaction() as sess:
            sess["jwt_token"] = "atoken"
        principle = SearchPrinciple("123", "A first name", "A surname")
        jwt_payload = JWTPayload("iss", "aud", "exp", "iat", "sub", "source", principle)
        mock_validate.return_value = jwt_payload
        response = self.client.get(url_for("auth.authorized"))
        self.assertEqual(
            response.location,
            url_for("search.search_by_post_code_address", _external=True),
        )

    def test_authenticated_ok(self):
        @authenticated
        def do_a_thing(x):
            return x

        with super_test_context(app):
            session["profile"] = {"user_id": "mock_user"}
            self.assertEqual(do_a_thing("aarvark"), "aarvark")

    @patch("server.views.auth.request")
    def test_authenticated_not(self, mock_request):
        mock_request.path = "/rhubarb"
        mock_request.full_path = "http://custard/rhubarb"

        @authenticated
        def do_a_thing(x):
            return x

        with super_test_context(app):
            result = do_a_thing("aarvark")
            expected = redirect(
                url_for(
                    "auth.login",
                    requestedpath=base64.urlsafe_b64encode(("http://custard/rhubarb").encode("utf-8")),
                    _external=True,
                )
            )
            self.assertEqual(result.status, expected.status)
            self.assertEqual(result.headers, expected.headers)
