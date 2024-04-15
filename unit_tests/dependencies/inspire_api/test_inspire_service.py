from unittest import TestCase
from unittest.mock import MagicMock

from flask import g

from server.dependencies.inspire_api.inspire_service import InspireService
from server.main import app
from unit_tests.utilities_tests import super_test_context


class TestLLC1DocumentAPIService(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_generate_ok(self):
        with super_test_context(app):
            response = MagicMock()
            g.requests.get.return_value = response

            service = InspireService({"INSPIRE_API_ROOT": "anurl"})
            result = service.get_llc_by_inspire_id("anid")
            self.assertEqual(result, response)
            g.requests.get.assert_called_with("anurl/local-land-charge-id/anid")
