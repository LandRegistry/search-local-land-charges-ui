from unittest import TestCase, mock
from unittest.mock import Mock

from landregistry.exceptions import ApplicationError

from server.dependencies.search_api.search_type import SearchType
from server.main import app
from server.services.search_by_text import SearchByText


class TestSearchByText(TestCase):
    SEARCH_BY_TEXT_PATH = "server.services.search_by_text"

    def setUp(self):
        self.search_by_text = SearchByText(Mock())

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_no_search_query(self, mock_local_land_charge_service, mock_addresses_service):
        with app.test_request_context():
            response = self.search_by_text.process(None, None)

            self.assertEqual(response["search_message"], "Enter a postcode or location")
            self.assertEqual(response["status"], "error")

            return None

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_postcode(self, mock_local_land_charge_service, mock_addresses_service):
        query_string = "BT1 1AA"

        expected_address_json = [{"geometry": {"type": "some type"}}]

        self.setup_successful_search_test(
            expected_address_json,
            mock_addresses_service,
            mock_local_land_charge_service,
        )

        response = self.search_by_text.process(query_string, None)

        self.assertEqual(response["data"], expected_address_json)
        self.assertEqual(response["status"], "success")
        mock_addresses_service.return_value.get_by.assert_called_with(SearchType.POSTCODE.value, query_string)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_uprn(self, mock_local_land_charge_service, mock_addresses_service):
        with app.test_request_context():
            query_string = "123456789012"

            expected_address_json = [{"geometry": {"type": "some type"}}]

            self.setup_successful_search_test(
                expected_address_json,
                mock_addresses_service,
                mock_local_land_charge_service,
            )

            response = self.search_by_text.process(query_string, None)

            self.assertEqual(response["data"], expected_address_json)
            self.assertEqual(response["status"], "success")
            mock_addresses_service.return_value.get_by.assert_called_with(SearchType.UPRN.value, query_string)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_charge_number(self, mock_local_land_charge_service, mock_addresses_service):
        query_string = "LLC-1"

        expected_address_json = [{"geometry": {"type": "some type"}, "display_id": "LLC-1"}]

        self.setup_successful_search_test(
            expected_address_json,
            mock_addresses_service,
            mock_local_land_charge_service,
        )

        response = self.search_by_text.process(query_string, None)

        self.assertEqual(response["data"], expected_address_json)
        self.assertEqual(response["status"], "success")

        mock_local_land_charge_service.return_value.get_by_charge_number.assert_called_with(query_string)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_charge_number_prefix(self, mock_local_land_charge_service, mock_addresses_service):
        query_string = "random search term"

        expected_address_json = [{"geometry": {"type": "some type"}}]

        self.setup_successful_search_test(
            expected_address_json,
            mock_addresses_service,
            mock_local_land_charge_service,
        )

        response = self.search_by_text.process(query_string, None)

        self.assertEqual(response["data"], expected_address_json)
        self.assertEqual(response["status"], "success")
        mock_addresses_service.return_value.get_by.assert_called_with(SearchType.TEXT.value, query_string.upper())

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_invalid_search(
        self,
        mock_local_land_charge_service,
        mock_addresses_service,
    ):
        query_string = "random search term"

        mock_addresses_service.return_value.get_by = Mock()
        get_by_address_mock = mock_addresses_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 500

        with self.assertRaises(ApplicationError) as context:
            self.search_by_text.process(query_string, None)

        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_response_404(
        self,
        mock_local_land_charge_service,
        mock_addresses_service,
    ):
        with app.test_request_context():
            query_string = "random search term"

            mock_addresses_service.return_value.get_by = Mock()
            get_by_address_mock = mock_addresses_service.return_value.get_by
            get_by_address_mock.return_value.status_code = 404

            response = self.search_by_text.process(query_string, None)

            self.assertEqual(response["search_message"], "Enter a valid postcode or location")
            self.assertEqual(response["status"], "error")

    @staticmethod
    def setup_successful_search_test(expected_response, mock_address_service, mock_local_land_charge_service):
        mock_address_service.return_value.get_by = Mock()
        mock_local_land_charge_service.return_value.get_by_charge_number = Mock()

        get_by_address_mock = mock_address_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 200
        get_by_address_mock.return_value.json.return_value = expected_response

        get_by_charge_id_mock = mock_local_land_charge_service.return_value.get_by_charge_number
        get_by_charge_id_mock.return_value.status_code = 200
        get_by_charge_id_mock.return_value.json.return_value = expected_response
