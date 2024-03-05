from flask import url_for, redirect, session
from unittest.mock import ANY, MagicMock, patch
from server import config
from server.main import app
from unittest import TestCase
from server.models.searches import PaidSearchItem, PaymentState, SearchState
from server.services.fee_functions import format_fee_for_gov_pay
from server.views.forms.search_area_description_form import SearchAreaDescriptionForm
from server.views.paid_search import continue_to_payment, search_description_continue, search_description_find
from unit_tests.utilities_tests import super_test_context


class TestPaidSearch(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch('server.views.paid_search.decode_validate_search_id')
    def test_search_area_description_no_state(self, mock_validate):
        mock_validate.return_value = None
        result = self.client.get(url_for('paid_search.search_area_description', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("search.search_by_post_code_address"))
        mock_validate.assert_called_with("anencodedid")

    @patch('server.views.paid_search.decode_validate_search_id')
    def test_search_area_description_with_address(self, mock_validate):
        mock_validate.return_value.address = "Anaddress"
        result = self.client.get(url_for('paid_search.search_area_description', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("paid_search.confirm_address", enc_search_id="anencodedid"))
        mock_validate.assert_called_with("anencodedid")

    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.SearchAreaDescriptionForm')
    @patch('server.views.paid_search.search_description_find')
    def test_search_area_description_post(self, mock_find, mock_form, mock_validate):
        mock_search_state = MagicMock()
        mock_search_state.address = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_validate.return_value = mock_search_state
        mock_form.return_value.has_address.data = None
        mock_form.return_value.selected_address.data = None
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.find.data = "thing"
        mock_form.return_value.errors = None
        # Weird but means that the address list is actually rendered
        mock_form.return_value.has_address = SearchAreaDescriptionForm().has_address
        mock_find.return_value = ["anaddress"]
        result = self.client.post(url_for('paid_search.search_area_description', enc_search_id="anencodedid",
                                          address="anaddress"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("How would you like to provide your search area description?", result.text)
        self.assertIn("anaddress", result.text)
        mock_validate.assert_called_with("anencodedid")
        mock_find.assert_called_with(mock_form.return_value)

    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.SearchAreaDescriptionForm')
    @patch('server.views.paid_search.search_description_continue')
    def test_search_area_description_post_nofind(self, mock_continue, mock_form, mock_validate):
        mock_search_state = MagicMock()
        mock_search_state.address = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_validate.return_value = mock_search_state
        mock_form.return_value.has_address.data = None
        mock_form.return_value.selected_address.data = None
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.find.data = None
        mock_form.return_value.errors = None
        mock_continue.return_value = redirect("blahblah")
        result = self.client.post(url_for('paid_search.search_area_description', enc_search_id="anencodedid",
                                          address="anaddress"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "blahblah")
        mock_validate.assert_called_with("anencodedid")

    @patch('server.views.paid_search.decode_validate_search_id')
    def test_confirm_address_no_state(self, mock_validate):
        mock_validate.return_value = None
        result = self.client.get(url_for('paid_search.confirm_address', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, (url_for("search.search_by_post_code_address")))
        mock_validate.assert_called_with("anencodedid")

    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.ConfirmAddressForm')
    @patch('server.views.paid_search.continue_to_payment')
    def test_confirm_address_post_matches(self, mock_continue, mock_form, mock_validate):
        mock_search_state = MagicMock()
        mock_search_state.address = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_validate.return_value = mock_search_state
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.address_matches.data = 'yes'
        mock_form.return_value.errors = None
        mock_continue.return_value = redirect("blahblah")
        result = self.client.post(url_for('paid_search.confirm_address', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "blahblah")
        mock_validate.assert_called_with("anencodedid")
        mock_continue.assert_called_with(None, mock_search_state, 'anencodedid')

    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.ConfirmAddressForm')
    @patch('server.views.paid_search.continue_to_payment')
    def test_confirm_address_post_no_match_no_desc(self, mock_continue, mock_form, mock_validate):
        mock_search_state = MagicMock()
        mock_search_state.address = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_validate.return_value = mock_search_state
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.address_matches.data = 'no'
        mock_form.return_value.search_area_description.data = None
        mock_form.return_value.search_area_description.errors = []
        mock_form.return_value.errors = None
        result = self.client.post(url_for('paid_search.confirm_address', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Does ‘None’ match the exact search area?", result.text)
        mock_validate.assert_called_with("anencodedid")
        self.assertEqual(mock_form.return_value.search_area_description.errors, ['Describe the search location'])

    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.ConfirmAddressForm')
    @patch('server.views.paid_search.continue_to_payment')
    def test_confirm_address_post_no_match_desc(self, mock_continue, mock_form, mock_validate):
        mock_search_state = MagicMock()
        mock_search_state.address = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_validate.return_value = mock_search_state
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.address_matches.data = 'no'
        mock_form.return_value.search_area_description.data = "andescription"
        mock_form.return_value.search_area_description.errors = []
        mock_form.return_value.errors = None
        mock_continue.return_value = redirect("blahblah")
        result = self.client.post(url_for('paid_search.confirm_address', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "blahblah")
        mock_validate.assert_called_with("anencodedid")
        mock_continue.assert_called_with("andescription", mock_search_state, 'anencodedid')

    def test_search_description_find_no_pc(self):
        mock_form = MagicMock()
        mock_form.search_postcode.data = None
        mock_form.search_postcode.errors = []
        result = search_description_find(mock_form)
        self.assertEqual(result, [])
        self.assertEqual(mock_form.search_postcode.errors, ['Enter a postcode'])

    @patch('server.views.paid_search.SearchByPostcode')
    def test_search_description_find_error(self, mock_search):
        mock_search.return_value.process.return_value = {"status": "error", "search_message": "anerror"}
        mock_form = MagicMock()
        mock_form.search_postcode.data = "apostcode"
        mock_form.search_postcode.errors = []
        result = search_description_find(mock_form)
        self.assertEqual(result, [])
        self.assertEqual(mock_form.search_postcode.errors, ['anerror'])

    @patch('server.views.paid_search.SearchByPostcode')
    def test_search_description_find_ok(self, mock_search):
        mock_search.return_value.process.return_value = {"status": "woop", "data": [{"address": "anaddress"}]}
        mock_form = MagicMock()
        mock_form.search_postcode.data = "apostcode"
        result = search_description_find(mock_form)
        self.assertEqual(result, ["anaddress"])

    @patch('server.views.paid_search.continue_to_payment')
    def test_search_description_continue_no_address(self, mock_continue):
        mock_state = MagicMock()
        mock_form = MagicMock()
        mock_form.has_address.data = "find_address"
        mock_form.selected_address.data = None
        mock_form.search_postcode.errors = []
        mock_form.search_postcode.data = "apostcode"
        result = search_description_continue(mock_form, mock_state, "anencodedid")
        self.assertIsNone(result)
        self.assertEqual(mock_form.search_postcode.errors,
                         ['Enter a postcode, select ‘Find address’ and choose an address from the list'])
        mock_continue.assert_not_called()

    @patch('server.views.paid_search.continue_to_payment')
    def test_search_description_continue_address(self, mock_continue):
        mock_state = MagicMock()
        mock_form = MagicMock()
        mock_form.has_address.data = "find_address"
        mock_form.selected_address.data = "anaddress"
        mock_form.search_postcode.errors = []
        mock_form.search_postcode.data = "apostcode"
        result = search_description_continue(mock_form, mock_state, "anencodedid")
        self.assertEqual(result, mock_continue.return_value)
        self.assertEqual(mock_form.search_postcode.errors, [])
        mock_continue.assert_called_with("anaddress", mock_state, "anencodedid")

    @patch('server.views.paid_search.continue_to_payment')
    def test_search_description_continue_no_desc(self, mock_continue):
        mock_state = MagicMock()
        mock_form = MagicMock()
        mock_form.has_address.data = "blah"
        mock_form.search_area_description.data = None
        mock_form.search_area_description.errors = []
        result = search_description_continue(mock_form, mock_state, "anencodedid")
        self.assertIsNone(result)
        self.assertEqual(mock_form.search_area_description.errors,
                         ["Describe the search location"])
        mock_continue.assert_not_called()

    @patch('server.views.paid_search.continue_to_payment')
    def test_search_description_continue_desc(self, mock_continue):
        mock_state = MagicMock()
        mock_form = MagicMock()
        mock_form.has_address.data = "blah"
        mock_form.search_area_description.data = "ansearchdescription"
        mock_form.search_area_description.errors = []
        result = search_description_continue(mock_form, mock_state, "anencodedid")
        self.assertEqual(result, mock_continue.return_value)
        self.assertEqual(mock_form.search_area_description.errors, [])
        mock_continue.assert_called_with("ansearchdescription", mock_state, "anencodedid")

    @patch('server.views.paid_search.GovPayService')
    @patch('server.views.paid_search.PaymentState')
    def test_continue_to_payment(self, mock_state, mock_pay):
        with super_test_context(app):
            mock_pay.return_value.request_payment.return_value = {"_links": {"next_url": {"href": "anurl"}}}
            mock_state.from_json.return_value = "anpaymentstate"
            mock_search_state = MagicMock()

            result = continue_to_payment("ansearchdescription", mock_search_state, "anencsearchid")
            self.assertEqual(result.location, "anurl")
            mock_pay.return_value.request_payment.assert_called_with(
                format_fee_for_gov_pay(config.SEARCH_FEE_IN_PENCE), ANY,
                'Official search result of local land charges', 'anencsearchid')
            session['paid_searches']["anencsearchid"] = {'payment_state': "anpaymentstate",
                                                         'address': mock_search_state.address}

    @patch('server.views.paid_search.clear_history')
    def test_process_pay_no_id(self, mock_clear):
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"anencodedid": {"payment_state": mock_pay_state}}
        result = self.client.get(url_for('paid_search.process_pay', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_clear.assert_called()

    @patch('server.views.paid_search.clear_history')
    @patch('server.views.paid_search.GovPayService')
    @patch('server.views.paid_search.PaymentState')
    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.SearchByArea')
    def test_process_pay_not_found(self, mock_area, mock_validate, mock_pay, mock_gov_pay, mock_clear):
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = "anid"
        mock_pay_state.state = {"status": "success"}
        mock_search_state = SearchState()
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.address = "anaddress"
        mock_search_state.search_extent = {"an": "extent"}
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"anencodedid": {"payment_state": mock_pay_state,
                                                     "search_state": mock_search_state,
                                                     "address": "anaddress"}}
        mock_gov_pay.return_value.get_payment.return_value = "anpayment"
        mock_pay.from_json.return_value = mock_pay_state
        mock_validate.return_value = mock_search_state
        mock_area.return_value.process.return_value = {"status": 500}
        result = self.client.get(url_for('paid_search.process_pay', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_clear.assert_called()
        mock_gov_pay.return_value.get_payment.assert_called_with("anid")
        mock_validate.assert_called_with('anencodedid')
        mock_area.return_value.process.assert_called_with({'an': 'extent'}, results_filter='cancelled')

    @patch('server.views.paid_search.clear_history')
    @patch('server.views.paid_search.GovPayService')
    @patch('server.views.paid_search.PaymentState')
    @patch('server.views.paid_search.decode_validate_search_id')
    @patch('server.views.paid_search.SearchByArea')
    @patch('server.views.paid_search.get_charge_items')
    def test_process_pay_found(self, mock_get_items, mock_area, mock_validate, mock_pay, mock_gov_pay, mock_clear):
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = "anid"
        mock_pay_state.state = {"status": "success"}
        mock_search_state = SearchState()
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.address = "anaddress"
        mock_search_state.search_extent = {"an": "extent"}
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"anencodedid": {"payment_state": mock_pay_state,
                                                     "search_state": mock_search_state,
                                                     "address": "anaddress"}}
        mock_gov_pay.return_value.get_payment.return_value = "anpayment"
        mock_pay.from_json.return_value = mock_pay_state
        mock_validate.return_value = mock_search_state
        mock_area.return_value.process.return_value = {"status": 200}
        mock_get_items.return_value = ["some", "charges"]
        result = self.client.get(url_for('paid_search.process_pay', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        mock_clear.assert_called()
        mock_gov_pay.return_value.get_payment.assert_called_with("anid")
        mock_validate.assert_called_with('anencodedid')
        mock_area.return_value.process.assert_called_with({'an': 'extent'}, results_filter='cancelled')
        mock_get_items.assert_called_with([])
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']['anencodedid']['search_state'].charges, ['some', 'charges'])

    @patch('server.views.paid_search.clear_history')
    @patch('server.views.paid_search.GovPayService')
    @patch('server.views.paid_search.PaymentState')
    def test_process_pay_fail(self, mock_pay, mock_gov_pay, mock_clear):
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = "anid"
        mock_pay_state.state = {"status": "cancelled"}
        mock_search_state = SearchState()
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.address = "anaddress"
        mock_search_state.search_extent = {"an": "extent"}
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"anencodedid": {"payment_state": mock_pay_state,
                                                     "search_state": mock_search_state,
                                                     "address": "anaddress"}}
        mock_gov_pay.return_value.get_payment.return_value = "anpayment"
        mock_pay.from_json.return_value = mock_pay_state
        result = self.client.get(url_for('paid_search.process_pay', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))
        mock_clear.assert_called()
        mock_gov_pay.return_value.get_payment.assert_called_with("anid")
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']['anencodedid']['search_state'].charges, None)

    @patch('server.views.paid_search.clear_history')
    @patch('server.views.paid_search.GovPayService')
    @patch('server.views.paid_search.PaymentState')
    def test_process_pay_weird(self, mock_pay, mock_gov_pay, mock_clear):
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = "anid"
        mock_pay_state.state = {"status": "weird"}
        mock_search_state = SearchState()
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.address = "anaddress"
        mock_search_state.search_extent = {"an": "extent"}
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"anencodedid": {"payment_state": mock_pay_state,
                                                     "search_state": mock_search_state,
                                                     "address": "anaddress"}}
        mock_gov_pay.return_value.get_payment.return_value = "anpayment"
        mock_pay.from_json.return_value = mock_pay_state
        result = self.client.get(url_for('paid_search.process_pay', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search_results.results'))
        mock_clear.assert_called()
        mock_gov_pay.return_value.get_payment.assert_called_with("anid")
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']['anencodedid']['search_state'].charges, None)

    def test_get_paid_search_notfound(self):
        mock_search_state = SearchState()
        mock_search_state.parent_search = None
        mock_search_state.previously_completed = False
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "search_state": mock_search_state,
                    "payment_state": mock_pay_state
                }
            }
        result = self.client.get(url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)

    @patch('server.views.paid_search.PaidSearchUtils')
    def test_get_paid_search_payment_success(self, mock_paid_utils):
        mock_search_state = SearchState()
        mock_search_state.parent_search = None
        mock_search_state.previously_completed = True
        mock_search_state.search_reference = None
        mock_search_state.search_extent = {"an": "extent"}
        mock_search_state.address = "anaddress"
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        mock_pay_state.payment_provider = "anprovider"
        mock_pay_state.card_brand = "ancardbrand"
        mock_pay_state.amount = "anamount"
        mock_pay_state.reference = "anreference"
        mock_paid_utils.request_search_generation.return_value = "ansearchref"
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "search_state": mock_search_state,
                    "payment_state": mock_pay_state
                }
            }
        result = self.client.get(url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Your payment was successful", result.text)

        mock_paid_utils.request_search_generation.assert_called_with({'an': 'extent'}, 'anaddress',
                                                                     None, contact_id='mock_user')
        mock_paid_utils.pre_associate_search.assert_called_with('ansearchref', None, {'an': 'extent'}, 'anaddress',
                                                                None, 'anprovider', 'ancardbrand', 'anamount',
                                                                'anreference', None)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']["anencodedid"]["search_state"].search_reference, "ansearchref")

    @patch('server.views.paid_search.PaidSearchUtils')
    def test_get_paid_search_payment_paid_fail(self, mock_paid_utils):
        mock_search_state = SearchState()
        mock_search_state.parent_search = None
        mock_search_state.previously_completed = True
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.search_extent = {"an": "extent"}
        mock_search_state.address = "anaddress"
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        mock_pay_state.payment_provider = "anprovider"
        mock_pay_state.card_brand = "ancardbrand"
        mock_pay_state.amount = "anamount"
        mock_pay_state.reference = "anreference"
        mock_paid_utils.get_search_result.side_effect = Exception()
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "search_state": mock_search_state,
                    "payment_state": mock_pay_state,
                    "paid_search_item": None
                }
            }
        result = self.client.get(url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Your official search result failed to load", result.text)
        mock_paid_utils.get_search_result.assert_called_with('ansearchref', None, {'an': 'extent'}, 'anaddress', None,
                                                             'anprovider', 'ancardbrand', 'anamount', 'anreference',
                                                             None)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']["anencodedid"]["search_state"].search_reference, "ansearchref")

    @patch('server.views.paid_search.PaidSearchUtils')
    def test_get_paid_search_pdf_poll(self, mock_paid_utils):
        mock_search_state = SearchState()
        mock_search_state.parent_search = None
        mock_search_state.previously_completed = True
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.search_extent = {"an": "extent"}
        mock_search_state.address = "anaddress"
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        mock_pay_state.payment_provider = "anprovider"
        mock_pay_state.card_brand = "ancardbrand"
        mock_pay_state.amount = "anamount"
        mock_pay_state.reference = "anreference"
        mock_paid_utils.get_search_result.return_value = None
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "search_state": mock_search_state,
                    "payment_state": mock_pay_state,
                    "paid_search_item": None
                }
            }
        result = self.client.get(url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Loading official search result", result.text)
        mock_paid_utils.get_search_result.assert_called_with('ansearchref', None, {'an': 'extent'}, 'anaddress', None,
                                                             'anprovider', 'ancardbrand', 'anamount', 'anreference',
                                                             None)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']["anencodedid"]["search_state"].search_reference, "ansearchref")

    @patch('server.views.paid_search.AuditAPIService')
    @patch('server.views.paid_search.PaidSearchUtils')
    @patch('server.views.paid_search.StorageAPIService')
    def test_get_paid_search_result(self, mock_storage, mock_paid_utils, mock_audit):
        mock_search_state = SearchState()
        mock_search_state.parent_search = None
        mock_search_state.previously_completed = True
        mock_search_state.search_reference = "ansearchref"
        mock_search_state.search_extent = {"an": "extent"}
        mock_search_state.address = "anaddress"
        mock_pay_state = PaymentState()
        mock_pay_state.payment_id = None
        mock_pay_state.payment_provider = "anprovider"
        mock_pay_state.card_brand = "ancardbrand"
        mock_pay_state.amount = "anamount"
        mock_pay_state.reference = "anreference"
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "documents-filed": "somedocuments"
            }
        ]
        mock_paid_search.search_extent = {"an": "extent"}
        mock_paid_search.document_url = "andocumenturl"
        mock_paid_utils.get_search_result.return_value = mock_paid_search
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "search_state": mock_search_state,
                    "payment_state": mock_pay_state,
                    "paid_search_item": None
                }
            }
        result = self.client.get(url_for('paid_search.get_paid_search', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Download your official local land charges search result", result.text)
        mock_paid_utils.get_search_result.assert_called_with('ansearchref', None, {'an': 'extent'}, 'anaddress', None,
                                                             'anprovider', 'ancardbrand', 'anamount', 'anreference',
                                                             None)
        mock_storage.return_value.get_external_url_for_document_url.assert_called_with('andocumenturl')
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['paid_searches']["anencodedid"]["search_state"].search_reference, "ansearchref")
            self.assertEqual(sess['paid_searches']["anencodedid"]['paid_search_item'], mock_paid_search)

    def test_pdf_poll_failure(self):
        result = self.client.get(url_for('paid_search.pdf_poll_failure'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Your official search result failed to load", result.text)

    @patch('server.views.paid_search.send_file')
    @patch('server.views.paid_search.PaidResultsConverter')
    def test_download_charges_json(self, mock_converter, mock_send_file):
        mock_send_file.return_value = redirect("ansendfile")
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "documents-filed": "somedocuments"
            }
        ]
        mock_paid_search.search_extent = {"an": "extent"}
        mock_paid_search.document_url = "andocumenturl"
        mock_converter.to_json.return_value = "somejson"
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        result = self.client.get(url_for('paid_search.download_charges', enc_search_id="anencodedid",
                                         download_format="json"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "ansendfile")
        mock_send_file.assert_called_with('somejson', mimetype='application/json', download_name=ANY,
                                          as_attachment=True)

    @patch('server.views.paid_search.send_file')
    @patch('server.views.paid_search.PaidResultsConverter')
    def test_download_charges_csv(self, mock_converter, mock_send_file):
        mock_send_file.return_value = redirect("ansendfile")
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "documents-filed": "somedocuments"
            }
        ]
        mock_paid_search.search_extent = {"an": "extent"}
        mock_paid_search.document_url = "andocumenturl"
        mock_converter.to_csv.return_value = "somecsv"
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        result = self.client.get(url_for('paid_search.download_charges', enc_search_id="anencodedid",
                                         download_format="csv"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "ansendfile")
        mock_send_file.assert_called_with('somecsv', mimetype='text/csv', download_name=ANY, as_attachment=True)

    @patch('server.views.paid_search.send_file')
    @patch('server.views.paid_search.PaidResultsConverter')
    def test_download_charges_xml(self, mock_converter, mock_send_file):
        mock_send_file.return_value = redirect("ansendfile")
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "documents-filed": "somedocuments"
            }
        ]
        mock_paid_search.search_extent = {"an": "extent"}
        mock_paid_search.document_url = "andocumenturl"
        mock_converter.to_xml.return_value = "somexml"
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        result = self.client.get(url_for('paid_search.download_charges', enc_search_id="anencodedid",
                                         download_format="xml"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "ansendfile")
        mock_send_file.assert_called_with('somexml', mimetype='application/xml', download_name=ANY, as_attachment=True)

    @patch('server.views.paid_search.send_file')
    @patch('server.views.paid_search.PaidResultsConverter')
    def test_download_charges_wtf(self, mock_converter, mock_send_file):
        mock_send_file.return_value = redirect("ansendfile")
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "documents-filed": "somedocuments"
            }
        ]
        mock_paid_search.search_extent = {"an": "extent"}
        mock_paid_search.document_url = "andocumenturl"
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        result = self.client.get(url_for('paid_search.download_charges', enc_search_id="anencodedid",
                                         download_format="wtf"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_send_file.assert_not_called()

    def test_supporting_document_list_no_paid(self):
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                }
            }
        result = self.client.get(url_for('paid_search.supporting_document_list', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.search_by_post_code_address'))

    @patch('server.views.paid_search.calculate_pagination_info')
    def test_supporting_document_list_ok(self, mock_paginate):
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "local-land-charge": 123,
                "documents-filed": {"some": "documents"}
            }
        ]
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        mock_paginate.return_value = [], {}, 0
        result = self.client.get(url_for('paid_search.supporting_document_list', enc_search_id="anencodedid"))
        self.assertEqual(result.status_code, 200)
        mock_paginate.assert_called_with(['LLC-3Z'], 'paid_search.supporting_document_list', 10, 1,
                                         {'enc_search_id': 'anencodedid'})
        self.assertIn("Download light obstruction notice documents", result.text)

    def test_charge_supporting_documents_no_search(self):
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                }
            }
        result = self.client.get(url_for('paid_search.charge_supporting_documents', enc_search_id="anencodedid",
                                         charge_id="anchargeid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.search_by_post_code_address'))

    def test_charge_supporting_documents_no_docs(self):
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "local-land-charge": 123
            }
        ]
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        result = self.client.get(url_for('paid_search.charge_supporting_documents', enc_search_id="anencodedid",
                                         charge_id="anchargeid"))
        self.assertEqual(result.status_code, 404)
        self.assertIn("Page not found", result.text)

    @patch('server.views.paid_search.StorageAPIService')
    def test_charge_supporting_documents_docs(self, mock_storage):
        mock_paid_search = PaidSearchItem()
        mock_paid_search.charges = [
            {
                "local-land-charge": 123,
                "documents-filed": {"blah": [{"subdirectory": "ansubdirectory", "bucket": "anbucket"}]}
            }
        ]
        with self.client.session_transaction() as sess:
            sess['paid_searches'] = {
                "anencodedid": {
                    "paid_search_item": mock_paid_search
                }
            }
        mock_storage.return_value.get_external_url.return_value = "andocumenturl"
        result = self.client.get(url_for('paid_search.charge_supporting_documents', enc_search_id="anencodedid",
                                         charge_id="LLC-3Z"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "andocumenturl")
        mock_storage.return_value.get_external_url.assert_called_with('ansubdirectory', 'anbucket')
