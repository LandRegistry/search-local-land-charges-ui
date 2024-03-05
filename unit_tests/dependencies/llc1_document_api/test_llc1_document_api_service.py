from unittest import TestCase
from unittest.mock import MagicMock
from flask import g
from server.dependencies.llc1_document_api.llc1_document_api_service import LLC1DocumentAPIService
from server.main import app
from landregistry.exceptions import ApplicationError

from unit_tests.utilities_tests import super_test_context


class TestLLC1DocumentAPIService(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_generate_ok(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 202
            response.json.return_value = {"some": "json"}
            g.requests.post.return_value = response
            g.locale = "en"

            service = LLC1DocumentAPIService({"LLC1_API_URL": "AnUrl"})
            result = service.generate({"some": "extents"}, "an address", "anparentid", "ancontactid")

            g.requests.post.assert_called_with(
                "AnUrl/generate_async",
                json={
                    "description": "an address",
                    "extents": {"some": "extents"},
                    "source": "SEARCH",
                    "contact_id": "ancontactid",
                    "language": "en",
                    "parent_search_id": "anparentid",
                },
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(result, {"some": "json"})

    def test_generate_fail(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 500
            g.requests.post.return_value = response
            g.locale = "en"

            service = LLC1DocumentAPIService({"LLC1_API_URL": "AnUrl"})
            with self.assertRaises(ApplicationError) as raise_context:
                service.generate({"some": "extents"}, "an address", "anparentid", "ancontactid")
                self.assertEqual(raise_context.exception.code, "LLC101")

            g.requests.post.assert_called_with(
                "AnUrl/generate_async",
                json={
                    "description": "an address",
                    "extents": {"some": "extents"},
                    "source": "SEARCH",
                    "contact_id": "ancontactid",
                    "language": "en",
                    "parent_search_id": "anparentid",
                },
                headers={"Content-Type": "application/json"},
            )

    def test_poll_not_yet(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 202
            g.requests.get.return_value = response

            service = LLC1DocumentAPIService({"LLC1_API_URL": "AnUrl"})
            result = service.poll("anref")
            g.requests.get.assert_called_with("AnUrl/poll_llc1/anref", headers={"Content-Type": "application/json"})
            self.assertIsNone(result)

    def test_poll_generated(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 201
            response.json.return_value = {"some": "json"}
            g.requests.get.return_value = response

            service = LLC1DocumentAPIService({"LLC1_API_URL": "AnUrl"})
            result = service.poll("anref")
            g.requests.get.assert_called_with("AnUrl/poll_llc1/anref", headers={"Content-Type": "application/json"})
            self.assertEqual(result, {"some": "json"})

    def test_poll_fail(self):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 500
            g.requests.get.return_value = response

            service = LLC1DocumentAPIService({"LLC1_API_URL": "AnUrl"})
            with self.assertRaises(ApplicationError) as raise_context:
                service.poll("anref")
                self.assertEqual(raise_context.exception.code, "LLC102")

            g.requests.get.assert_called_with("AnUrl/poll_llc1/anref", headers={"Content-Type": "application/json"})
