from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import current_app

from server.main import app
from server.services.search_by_inspire_id import SearchByInspireId
from unit_tests.utilities_tests import super_test_context


class TestSearchByInspireId(TestCase):
    @patch("server.services.search_by_inspire_id.InspireService")
    def test_process_valid_200(self, mock_inspire_service):
        with super_test_context(app):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"some": "json"}
            mock_inspire_service.return_value.get_llc_by_inspire_id.return_value = mock_response
            search_by_inspire_id = SearchByInspireId(current_app.logger, current_app.config)
            result = search_by_inspire_id.process("aninspireid")
            self.assertEqual(result, {"status": 200, "data": {"some": "json"}})

    @patch("server.services.search_by_inspire_id.InspireService")
    def test_process_valid_500(self, mock_inspire_service):
        with super_test_context(app):
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_inspire_service.return_value.get_llc_by_inspire_id.return_value = mock_response
            search_by_inspire_id = SearchByInspireId(current_app.logger, current_app.config)
            result = search_by_inspire_id.process("aninspireid")
            self.assertEqual(result, {"status": 500})
