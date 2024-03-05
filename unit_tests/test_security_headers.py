import unittest

from server.main import app


class TestSecurityHeaders(unittest.TestCase):
    def setup_method(self, method):
        self.app = app.test_client()

    def test_headers_present(self):
        response = self.app.get("/")

        expected_headers = [
            "Permissions-Policy",
            "Referrer-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
        ]

        for header in expected_headers:
            self.assertIn(header, response.headers)
