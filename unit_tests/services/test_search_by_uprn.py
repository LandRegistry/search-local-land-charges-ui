from unittest import TestCase
from unittest.mock import Mock, patch

from landregistry.exceptions import ApplicationError

from server.main import app
from server.services.search_by_uprn import SearchByUprn


class TestSearchByUprn(TestCase):
    SEARCH_BY_UPRN_PATH = "server.services.search_by_uprn"

    def setUp(self):
        self.search_by_uprn = SearchByUprn(Mock())

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_no_search_query(self, mock_addresses_service):
        with app.test_request_context():
            response = self.search_by_uprn.process(None, None)

            self.assertEqual(response["search_message"], "Enter a uprn")
            self.assertEqual(response["status"], "error")
            mock_addresses_service.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_invalid_query(self, mock_addresses_service):
        with app.test_request_context():
            response = self.search_by_uprn.process("ABC", None)

            self.assertEqual(response["search_message"], "Invalid uprn. Try again")
            self.assertEqual(response["status"], "error")
            mock_addresses_service.get_by.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_valid(self, mock_addresses_service):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [
            {
                "address": "abc",
                "geometry": "def",
                "test": "excluded",
                "uprn": 1234,
                "index_map": "blah",
            }
        ]

        mock_addresses_service.return_value.get_by.return_value = response
        response = self.search_by_uprn.process("1234", None)

        self.assertEqual(response["status"], "success")
        self.assertEqual(
            response["data"],
            [{"address": "abc", "geometry": "def", "uprn": 1234, "index_map": "blah"}],
        )

        mock_addresses_service.return_value.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_valid_400_response(self, mock_addresses_service):
        with app.test_request_context():
            response = Mock()
            response.status_code = 400

            mock_addresses_service.return_value.get_by.return_value = response
            response = self.search_by_uprn.process("1234", None)

            self.assertEqual(response["status"], "error")
            self.assertEqual(response["search_message"], "Invalid uprn. Try again")

            mock_addresses_service.return_value.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_valid_404_response(self, mock_addresses_service):
        with app.test_request_context():
            response = Mock()
            response.status_code = 404

            mock_addresses_service.return_value.get_by.return_value = response
            response = self.search_by_uprn.process("1234", None)

            self.assertEqual(response["status"], "error")
            self.assertEqual(response["search_message"], "No results found")

            mock_addresses_service.return_value.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_UPRN_PATH))
    def test_search_by_uprn_valid_500_response(self, mock_addresses_service):
        response = Mock()
        response.status_code = 500

        mock_addresses_service.return_value.get_by.return_value = response

        self.assertRaises(ApplicationError, self.search_by_uprn.process, "1234", None)
        mock_addresses_service.return_value.get_by.assert_called()
