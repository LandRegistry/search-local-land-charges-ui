from server.app import app
from landregistry.exceptions import ApplicationError
from server.services.paid_search_utils import PaidSearchUtils
from unittest.mock import patch, MagicMock
from unittest import TestCase
from flask import g, session, current_app


class TestPaidSearchUtils(TestCase):

    def setUp(self):
        app.config['Testing'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True

    @patch('server.services.paid_search_utils.SearchLocalLandChargeService')
    @patch('server.services.paid_search_utils.LLC1DocumentAPIService')
    def test_get_search_result(self, mock_document_service, mock_search_llc_service):
        session['profile'] = {}
        session['profile']['user_id'] = "mock_user"

        mock_document_service.return_value.poll.return_value = {
            "reference_number": '000 000 001',
            "document_url": "test_url"
        }

        payment_id = 'test',
        search_extent = MagicMock()
        charges = MagicMock()
        address = 'abc'
        payment_provider = 'test_provider'
        card_brand = 'test_card'
        amount = 10
        reference = 'abcd'
        search_ref = 123

        result = PaidSearchUtils.get_search_result(search_ref, payment_id, search_extent, address, charges,
                                                   payment_provider, card_brand, amount, reference)

        mock_search_llc_service.return_value.save_users_paid_search.assert_called()
        current_app.logger.info.assert_called_with('Saving paid search')
        self.assertEqual(result.search_id, 1)
        self.assertEqual(result.document_url, 'test_url')
        self.assertEqual(result.search_extent, search_extent)
        self.assertEqual(result.charges, charges)
        self.assertEqual(result.payment_id, payment_id)
        self.assertEqual(result.user_id, "mock_user")
        self.assertEqual(result.payment_provider, payment_provider)
        self.assertEqual(result.card_brand, card_brand)
        self.assertEqual(result.amount, amount)
        self.assertEqual(result.reference, reference)

    @patch('server.services.paid_search_utils.SearchLocalLandChargeService')
    @patch('server.services.paid_search_utils.LLC1DocumentAPIService')
    def test_get_search_result_not_yet(self, mock_document_service,
                                       mock_search_llc_service):
        session['profile'] = {}
        session['profile']['user_id'] = "mock_user"

        mock_document_service.return_value.poll.return_value = None

        payment_id = 'test',
        search_extent = MagicMock()
        charges = MagicMock()
        address = 'abc'
        payment_provider = 'test_provider'
        card_brand = 'test_card'
        amount = 10
        reference = 'abcd'
        search_ref = 123

        result = PaidSearchUtils.get_search_result(search_ref, payment_id, search_extent, address, charges,
                                                   payment_provider, card_brand, amount, reference)

        self.assertIsNone(result)

    @patch('server.services.paid_search_utils.get_charge_items')
    @patch('server.services.paid_search_utils.SearchByArea')
    def test_charges_found(self, mock_search_by_area, mock_get_charge_items):
        mock_charges = []
        mock_get_charge_items.return_value = mock_charges
        mock_search_by_area.return_value.process.return_value = {
            'status': 200,
            'data': mock_charges
        }

        mock_extent = MagicMock()
        charges = PaidSearchUtils.search_by_area(mock_extent)

        current_app.logger.info.assert_called_with("Charges found")
        mock_get_charge_items.assert_called_with(mock_charges)
        mock_search_by_area.return_value.process.assert_called_with(mock_extent, results_filter='cancelled')
        self.assertEqual(charges, mock_charges)

    @patch('server.services.paid_search_utils.LLC1DocumentAPIService')
    def test_request_generation(self, mock_doc_service):
        mock_doc_service.return_value.generate.return_value = {"search_reference": 123}

        result = PaidSearchUtils.request_search_generation(None, None, None)

        self.assertEqual(result, 123)

    @patch('server.services.paid_search_utils.SearchByArea')
    def test_no_charges_found(self, mock_search_by_area):
        mock_search_by_area.return_value.process.return_value = {
            'status': 404
        }

        mock_extent = MagicMock()
        charges = PaidSearchUtils.search_by_area(mock_extent)

        mock_search_by_area.return_value.process.assert_called_with(mock_extent, results_filter='cancelled')
        current_app.logger.info.assert_called_with("No search results found")
        self.assertIsNone(charges)

    @patch('server.services.paid_search_utils.SearchByArea')
    def test_error(self, mock_search_by_area):

        mock_search_by_area.return_value.process.return_value = {
            'status': 500
        }

        with self.assertRaises(ApplicationError) as context:
            mock_extent = MagicMock()
            PaidSearchUtils.search_by_area(mock_extent)

        self.assertEqual(context.exception.http_code, 500)
        mock_search_by_area.return_value.process.assert_called_with(mock_extent, results_filter='cancelled')

    def test_format_search_id(self):
        search_id = 1
        formatted_id = PaidSearchUtils.format_search_id(search_id)
        expected = "000 000 001"
        self.assertEqual(formatted_id, expected)

        search_id = 999999999
        formatted_id = PaidSearchUtils.format_search_id(search_id)
        expected = "999 999 999"
        self.assertEqual(formatted_id, expected)

        search_id = 9999999999
        formatted_id = PaidSearchUtils.format_search_id(search_id)
        expected = "999 999 999"
        self.assertEqual(formatted_id, expected)

    @patch('server.services.paid_search_utils.SearchLocalLandChargeService')
    @patch('server.services.paid_search_utils.LocalAuthorityAPIService')
    @patch('server.services.paid_search_utils.ReportAPIService')
    def test_pre_associate_search(self, mock_report_api, mock_auth_api, mock_search_llc):
        g.trace_id = 123
        search_extent = MagicMock()
        session['profile'] = {}
        session['profile']['user_id'] = "mock_user"

        PaidSearchUtils.pre_associate_search("000 000 001", "payment_id", search_extent, "address", "charges",
                                             "payment_provider", "card_brand", "amount", "reference",
                                             parent_search_id="2")
        mock_search_llc.return_value.save_users_paid_search.assert_called()
