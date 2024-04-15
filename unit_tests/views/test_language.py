from unittest import TestCase
from unittest.mock import patch

from flask import url_for

from server.config import HOME_PAGE_CY_URL
from server.main import app


class TestLanguage(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch("server.views.language.request")
    def test_change_language_from_welsh(self, mock_request):
        mock_request.referrer = HOME_PAGE_CY_URL
        response = self.client.get(url_for("language.change_language", language="cy"))
        self.assertIn("language=cy", response.headers["Set-Cookie"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for("index.index_page"))

    @patch("server.views.language.request")
    def test_change_language_from_welsh_index(self, mock_request):
        mock_request.referrer = HOME_PAGE_CY_URL
        response = self.client.get(url_for("language.change_language", language="cy"))
        self.assertIn("language=cy", response.headers["Set-Cookie"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for("index.index_page"))

    @patch("server.views.language.request")
    def test_change_language_en(self, mock_request):
        mock_request.referrer = "/aardvark"
        response = self.client.get(url_for("language.change_language", language="en"))
        self.assertIn("language=en", response.headers["Set-Cookie"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/aardvark")
