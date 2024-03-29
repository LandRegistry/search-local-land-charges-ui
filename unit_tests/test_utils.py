import unittest

from server.main import app
from server.utils.content_negotiation_utils import request_wants_json


class TestContentNegotiationUtil(unittest.TestCase):
    def setup_method(self, method):
        self.app = app.test_client()

    def test_content_negotiation_util_returns_false_for_text_html(self):
        with self.app:
            self.app.get("/", headers=[("Accept", "text/html")])
            self.assertFalse(request_wants_json())

    def test_content_negotiation_util_returns_true_for_application_json(self):
        with self.app:
            self.app.get("/", headers=[("Accept", "application/json")])
            self.assertTrue(request_wants_json())
