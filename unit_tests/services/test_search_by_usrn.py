from unittest.mock import Mock, patch
from unittest import TestCase
from landregistry.exceptions import ApplicationError
from server.services.search_by_usrn import SearchByUsrn
from server.main import app


class TestSearchByUsrn(TestCase):
    SEARCH_BY_USRN_PATH = 'server.services.search_by_usrn'

    def setUp(self):
        self.search_by_usrn = SearchByUsrn(Mock())

    @patch("{}.AddressesService".format(SEARCH_BY_USRN_PATH))
    def test_search_by_usrn_no_search_query(self, mock_addresses_service):
        with app.test_request_context():
            response = self.search_by_usrn.process(None, None, None)

            self.assertEqual(response['search_message'], "Enter a usrn")
            self.assertEqual(response['status'], "error")
            mock_addresses_service.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_USRN_PATH))
    def test_search_by_usrn_invalid_query(self, mock_addresses_service):
        with app.test_request_context():
            response = self.search_by_usrn.process('ABC', 'EX4', None)

            self.assertEqual(response['search_message'], "Invalid usrn, please try again")
            self.assertEqual(response['status'], "error")
            mock_addresses_service.get_by.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_USRN_PATH))
    def test_search_by_usrn_valid(self, mock_addresses_service):
        response = Mock()
        response.status_code = 200
        test_json = [{"address": "abc", "geometry": "def", "test": "excluded", "usrn": 1234, "index_map": "blah"}]
        response.json.return_value = test_json

        mock_addresses_service.return_value.get_by.return_value = response
        response = self.search_by_usrn.process('1234', 'EX4', None)

        self.assertEqual(response['status'], "success")
        self.assertEqual(response['data'], test_json)

        mock_addresses_service.return_value.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_USRN_PATH))
    def test_search_by_usrn_valid_400_response(self, mock_addresses_service):
        with app.test_request_context():
            response = Mock()
            response.status_code = 404

            mock_addresses_service.return_value.get_by.return_value = response
            response = self.search_by_usrn.process('1234', 'EX4', None)

            self.assertEqual(response['status'], "error")
            self.assertEqual(response['search_message'], "No results found")

            mock_addresses_service.return_value.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_USRN_PATH))
    def test_search_by_usrn_valid_500_response(self, mock_addresses_service):
        response = Mock()
        response.status_code = 500

        mock_addresses_service.return_value.get_by.return_value = response

        self.assertRaises(ApplicationError, self.search_by_usrn.process, '1234', 'EX4', None)
        mock_addresses_service.return_value.get_by.assert_called()
