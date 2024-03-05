import unittest
from unittest import mock

from landregistry.exceptions.application_error import ApplicationError

from server.main import app


class TestExceptions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_not_found_default(self):
        response = self.app.get("/does_not_exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")

    def test_not_found_wants_html(self):
        response = self.app.get("/does_not_exist", headers={"Accept": "text/html"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "text/html")

    def test_not_found_wants_json(self):
        response = self.app.get("/does_not_exist", headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

    @mock.patch("server.views.index.render_template")
    def test_unhandled_default(self, render_template):
        render_template.side_effect = ZeroDivisionError()
        response = self.app.get("/dummy-english")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.mimetype, "text/html")

    @mock.patch("server.views.index.render_template")
    def test_unhandled_wants_html(self, render_template):
        render_template.side_effect = ZeroDivisionError()
        response = self.app.get("/dummy-english", headers={"Accept": "text/html"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.mimetype, "text/html")

    @mock.patch("server.views.index.render_template")
    def test_unhandled_wants_json(self, render_template):
        render_template.side_effect = ZeroDivisionError()
        response = self.app.get("/dummy-english", headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.mimetype, "application/json")

    @mock.patch("server.views.index.render_template")
    def test_application_default(self, render_template):
        render_template.side_effect = ApplicationError("Test error", http_code=400)
        response = self.app.get("/dummy-english")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "text/html")

    @mock.patch("server.views.index.render_template")
    def test_application_wants_html(self, render_template):
        render_template.side_effect = ApplicationError("Test error", http_code=400)
        response = self.app.get("/dummy-english", headers={"Accept": "text/html"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "text/html")

    @mock.patch("server.views.index.render_template")
    def test_application_wants_json(self, render_template):
        render_template.side_effect = ApplicationError("Test error", http_code=400)
        response = self.app.get("/dummy-english", headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
