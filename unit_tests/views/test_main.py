import base64
from unittest import TestCase
from unittest.mock import patch

from flask import g, url_for

from server import config
from server.main import app
from server.services.datetime_formatter import format_long_date
from unit_tests.utilities_tests import super_test_context


class TestMain(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    def test_accessibility_statement(self):
        response = self.client.get(url_for("main.accessibility_statement"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accessibility statement", response.text)

    def test_cookies_get_noconsent(self):
        response = self.client.get(url_for("main.cookies_page"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cookies", response.text)

    @patch("server.views.main.CookiesForm")
    def test_cookies_get_consent(self, mock_form):
        mock_form.return_value.analytics.data = "rhubarb"
        mock_form.return_value.validate_on_submit.return_value = False
        self.client.set_cookie(
            "cookies_policy",
            base64.b64encode('{"analytics":"aardvark"}'.encode()).decode(),
        )
        response = self.client.get(url_for("main.cookies_page"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cookies", response.text)
        self.assertEqual(mock_form.return_value.analytics.data, "aardvark")

    @patch("server.views.main.CookiesForm")
    def test_cookies_post(self, mock_form):
        mock_form.return_value.analytics.data = "no"
        mock_form.return_value.validate_on_submit.return_value = True
        self.client.set_cookie(
            "cookies_policy",
            base64.b64encode('{"analytics":"aardvark"}'.encode()).decode(),
        )
        self.client.set_cookie("_googleything", "donkey")
        self.client.set_cookie("_googleything2", "custard")
        response = self.client.post(
            url_for("main.cookies_page"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cookies", response.text)
        cookies = response.headers.get_all("Set-Cookie")
        [print(cookie) for cookie in cookies]
        self.assertTrue(
            any("_googleything=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0;" in cookie for cookie in cookies)
        )
        self.assertTrue(
            any("_googleything2=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0;" in cookie for cookie in cookies)
        )
        self.assertTrue(any("cookies_policy" in cookie for cookie in cookies))

    def test_terms_and_conditions(self):
        response = self.client.get(url_for("main.terms_and_conditions"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Terms and conditions", response.text)

    @patch("server.views.main.get_back_url")
    def test_back(self, mock_back):
        mock_back.return_value = "/rhubarb"
        response = self.client.get(url_for("main.back"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/rhubarb")

    def test_map_help(self):
        response = self.client.get(url_for("main.map_help"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("How to use the map", response.text)

    def test_release_notices_welsh_test(self):
        with super_test_context(app):
            self.client.set_cookie("language", "cy")
            response = self.client.get(url_for("main.release_notices"))
            self.assertEqual(response.status_code, 200)
            self.assertIn(format_long_date("22nd January 2023"), response.text)
            self.assertIn(format_long_date("10th May 2023"), response.text)
            self.assertIn(format_long_date("1st January 2020"), response.text)
            self.assertIn(format_long_date("2nd June 2021"), response.text)
            self.assertIn(format_long_date("3rd July 2022"), response.text)
            self.assertIn(format_long_date("11th November 2019"), response.text)
            self.assertIn(format_long_date("5th September 2022"), response.text)
            self.assertIn("google.com", response.text)

    @patch("server.views.main.config")
    def test_release_notices_en(self, mock_config):
        with super_test_context(app):
            mock_config.RELEASE_NOTICES_URL = "aurl"
            g.requests.get.return_value.json.return_value = [{"name": "22nd January 2007", "link": "https://pp.com"}]
            response = self.client.get(url_for("main.release_notices"))
            self.assertEqual(response.status_code, 200)
            self.assertIn("22nd January 2007", response.text)
            self.assertIn("https://pp.com", response.text)

    def test_contact_us_redirect_en(self):
        response = self.client.get(url_for("main.contact_us_redirect"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, config.CONTACT_US_URL)

    def test_contact_us_redirect_cy(self):
        with super_test_context(app):
            self.client.set_cookie("language", "cy")
            response = self.client.get(url_for("main.contact_us_redirect"))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, config.CONTACT_US_WELSH_URL)

    def test_not_authorised(self):
        response = self.client.get(url_for("main.not_authorised"))
        self.assertEqual(response.status_code, 401)
        self.assertIn("Sorry, there is a problem with the service", response.text)

    def test_error(self):
        response = self.client.get(url_for("main.error"))
        self.assertEqual(response.status_code, 500)
        self.assertIn("Sorry, there is a problem with the service", response.text)

    def test_too_many_attempts(self):
        response = self.client.get(url_for("main.too_many_attempts"))
        self.assertEqual(response.status_code, 429)
        self.assertIn("You’ve submitted this form too many times", response.text)
