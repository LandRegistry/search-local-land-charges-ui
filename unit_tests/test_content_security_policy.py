import json
import unittest

from server.main import app


class TestContentSecurityPolicy(unittest.TestCase):
    def setup_method(self, method):
        self.app = app.test_client()

    def test_reporting_mode(self):
        app.config["CONTENT_SECURITY_POLICY_MODE"] = "report-only"

        response = self.app.get("/")
        self.assertIn("script-src", response.headers["Content-Security-Policy-Report-Only"])

    def test_full_mode(self):
        app.config["CONTENT_SECURITY_POLICY_MODE"] = "full"

        response = self.app.get("/")
        self.assertIn("script-src", response.headers["Content-Security-Policy"])
        self.assertIn("script-src", response.headers["X-Content-Security-Policy"])

    def test_report_route(self):
        response = self.app.post(
            "/content-security-policy-report/",
            data=json.dumps({"csp-report": {"foo": "bar"}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 204)
