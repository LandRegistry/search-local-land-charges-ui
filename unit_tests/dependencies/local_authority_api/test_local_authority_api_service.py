from unittest import TestCase
from unittest.mock import MagicMock

from flask import current_app, g
from landregistry.exceptions import ApplicationError

from server.dependencies.local_authority_api.local_authority_api_service import (
    LocalAuthorityAPIService,
)
from server.main import app
from unit_tests.utilities import Utilities
from unit_tests.utilities_tests import super_test_context


class TestLocalAuthorityAPISerivice(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_organisations_success(self):
        with super_test_context(app):
            Utilities.mock_request()
            g.requests.get.return_value = Utilities.mock_response(
                status_code=200,
                json=[
                    {"title": "org1", "migrated": False},
                    {"title": "org2", "migrated": False},
                ],
            )
            get_response = LocalAuthorityAPIService.get_organisations()

            self.assertEqual("org1", get_response[0]["title"])
            self.assertEqual(False, get_response[0]["migrated"])

    def test_get_organisations_non_200(self):
        with super_test_context(app):
            response_text = "No organisations found"
            Utilities.mock_request()
            g.requests.get.return_value = Utilities.mock_response(status_code=404, text=response_text)

            try:
                LocalAuthorityAPIService.get_organisations()
            except ApplicationError:
                pass

            current_app.logger.exception.assert_called_with(
                "Failed to get organisations from local-authority-api. " "Message: {}".format(response_text)
            )

    def test_get_bounding_box(self):
        with super_test_context(app):
            Utilities.mock_request()
            g.requests.get.return_value = Utilities.mock_response(status_code=200)

            LocalAuthorityAPIService.get_bounding_box("Test authority")

            args, kwargs = g.requests.get.call_args_list[0]

            self.assertIn("v1.0/local-authorities/Test authority/bounding_box", args[0])

    def test_get_authorities_by_extent_success(self):
        with super_test_context(app):
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"abc": True, "def": False}

            g.requests.post.return_value = response

            response = LocalAuthorityAPIService.get_authorities_by_extent({"test": "test"})
            self.assertEqual(response, {"abc": True, "def": False})

            args, kwargs = g.requests.post.call_args_list[0]

            self.assertIn("v1.0/local-authorities", args[0])
            self.assertEqual(kwargs["data"], '{"test": "test"}')
            self.assertEqual(kwargs["headers"], {"Content-Type": "application/json"})

    def test_get_authorities_by_extent_no_results(self):
        with super_test_context(app):
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 404

            g.requests.post.return_value = response

            response = LocalAuthorityAPIService.get_authorities_by_extent({"test": "test"})
            self.assertEqual(response, {})

            args, kwargs = g.requests.post.call_args_list[0]

            self.assertIn("v1.0/local-authorities", args[0])
            self.assertEqual(kwargs["data"], '{"test": "test"}')
            self.assertEqual(kwargs["headers"], {"Content-Type": "application/json"})

    def test_get_authorities_by_extent_exception(self):
        with app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500
            response.json.return_value = {"abc": True, "def": False}

            g.requests.post.return_value = response

            self.assertRaises(
                ApplicationError,
                LocalAuthorityAPIService.get_authorities_by_extent,
                {"test": "test"},
            )

            args, kwargs = g.requests.post.call_args_list[0]

            self.assertIn("v1.0/local-authorities", args[0])
            self.assertEqual(kwargs["data"], '{"test": "test"}')
            self.assertEqual(kwargs["headers"], {"Content-Type": "application/json"})

    def test_plus_minus_buffer_ok(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"some": "json"}
            g.requests.post.return_value = response

            result = LocalAuthorityAPIService.plus_minus_buffer({"an": "extent"})

            self.assertEqual(result, {"some": "json"})
            g.requests.post.assert_called_with(
                f"{current_app.config['LOCAL_AUTHORITY_API_URL']}/v1.0/local-authorities/plus_minus_buffer",
                data='{"an": "extent"}',
                headers={"Content-Type": "application/json"},
            )

    def test_plus_minus_buffer_invalid(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 400
            g.requests.post.return_value = response

            with self.assertRaises(ApplicationError) as raises_context:
                LocalAuthorityAPIService.plus_minus_buffer({"an": "extent"})

            self.assertEqual(raises_context.exception.code, "LAUTH03")
            g.requests.post.assert_called_with(
                f"{current_app.config['LOCAL_AUTHORITY_API_URL']}/v1.0/local-authorities/plus_minus_buffer",
                data='{"an": "extent"}',
                headers={"Content-Type": "application/json"},
            )

    def test_plus_minus_buffer(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 500
            g.requests.post.return_value = response

            with self.assertRaises(ApplicationError) as raises_context:
                LocalAuthorityAPIService.plus_minus_buffer({"an": "extent"})

            self.assertEqual(raises_context.exception.code, "LAUTH04")
            g.requests.post.assert_called_with(
                f"{current_app.config['LOCAL_AUTHORITY_API_URL']}/v1.0/local-authorities/plus_minus_buffer",
                data='{"an": "extent"}',
                headers={"Content-Type": "application/json"},
            )
