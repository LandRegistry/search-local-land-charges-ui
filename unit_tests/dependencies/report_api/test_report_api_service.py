from unittest import TestCase
from unittest.mock import MagicMock

from flask import g
from landregistry.exceptions import ApplicationError

from server.dependencies.report_api.report_api_service import ReportAPIService
from server.main import app


class TestReportAPIService(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_event_ok(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "333"
            response = MagicMock()
            response.status_code = 201
            g.requests.post.return_value = response

            ReportAPIService.send_event("an event", {"some": "data"})

            args_tuple, kwargs = g.requests.post.call_args
            (url_called,) = args_tuple
            self.assertIn("event", url_called)
            g.requests.post.assert_called()

    def test_event_exception(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "333"
            response = MagicMock()
            response.status_code = 500
            g.requests.post.return_value = response

            with self.assertRaises(ApplicationError):
                ReportAPIService.send_event("an event", {"some": "data"})

            args_tuple, kwargs = g.requests.post.call_args
            (url_called,) = args_tuple
            self.assertIn("event", url_called)
            g.requests.post.assert_called()


def mock_request():
    g.trace_id = "333"
    g.session = MagicMock()
    g.requests = MagicMock()


def mock_response(status_code=200, text="", json=None):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    if json:
        response.json.return_value = json
    return response
