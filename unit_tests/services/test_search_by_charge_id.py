from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import current_app
from landregistry.exceptions import ApplicationError

from server.main import app
from server.services.search_by_charge_id import SearchByChargeId
from unit_tests.utilities_tests import super_test_context


class TestSearchByChargeId(TestCase):
    def test_process_empty_query(self):
        with super_test_context(app):
            search_by_charge_id = SearchByChargeId(current_app.logger)
            result = search_by_charge_id.process(None, None)
            self.assertEqual(
                result,
                {"search_message": "Enter a postcode or location", "status": "error"},
            )

    def test_process_invalid_query(self):
        with super_test_context(app):
            search_by_charge_id = SearchByChargeId(current_app.logger)
            result = search_by_charge_id.process("NOTACHARGEID", current_app.config)
            self.assertEqual(
                result,
                {"search_message": "Invalid charge id. Try again", "status": "error"},
            )

    @patch("server.services.search_by_charge_id.LocalLandChargeService")
    def test_process_valid_200(self, mock_llc_service):
        with super_test_context(app):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"some": "json"}
            mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
            search_by_charge_id = SearchByChargeId(current_app.logger)
            result = search_by_charge_id.process("LLC-1", current_app.config)
            self.assertEqual(result, {"data": {"some": "json"}, "status": "success"})

    @patch("server.services.search_by_charge_id.LocalLandChargeService")
    def test_process_valid_404(self, mock_llc_service):
        with super_test_context(app):
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
            search_by_charge_id = SearchByChargeId(current_app.logger)
            result = search_by_charge_id.process("LLC-1", current_app.config)
            self.assertEqual(
                result,
                {
                    "search_message": "Enter a valid postcode or location",
                    "status": "error",
                },
            )

    @patch("server.services.search_by_charge_id.LocalLandChargeService")
    def test_process_valid_500(self, mock_llc_service):
        with super_test_context(app):
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
            search_by_charge_id = SearchByChargeId(current_app.logger)
            with self.assertRaises(ApplicationError):
                search_by_charge_id.process("LLC-1", current_app.config)
