from flask import url_for, redirect
from unittest.mock import MagicMock, call, patch
from server.main import app
from unittest import TestCase
from jwt_validation.models import SearchPrinciple, JWTPayload
from server.models.searches import PaidSearchItem, PaymentState, SearchState
from server.views.my_account import search_in_searches


class TestMyAccount(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.flash')
    def test_my_account_page(self, mock_flash, mock_sllc):
        mock_sllc.return_value.get_service_messages.return_value = "Aardvark"
        test_principle = SearchPrinciple("anuserid", "anfirstname", "ansurname", "Active", "an@email.com")
        test_jwt_payload = JWTPayload(None, None, None, None, None, None, test_principle)
        with self.client.session_transaction() as sess:
            sess["jwt_payload"] = test_jwt_payload
        result = self.client.get(url_for('my_account.my_account_page'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("My account", result.text)
        mock_flash.assert_called_with("Aardvark", "service_message")

    @patch('server.views.my_account.ChangeDetailsForm')
    def test_change_details_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        mock_form.return_value.errors = []
        test_principle = SearchPrinciple("anuserid", "anfirstname", "ansurname", "Active", "an@email.com")
        test_jwt_payload = JWTPayload(None, None, None, None, None, None, test_principle)
        with self.client.session_transaction() as sess:
            sess["jwt_payload"] = test_jwt_payload
        result = self.client.get(url_for('my_account.change_details'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Change your details", result.text)
        mock_form.assert_called_with(first_name='anfirstname', last_name='ansurname')

    @patch('server.views.my_account.ChangeDetailsForm')
    @patch('server.views.my_account.AccountApiService')
    def test_change_details_post_error(self, mock_account, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.first_name.data = "Rhubarb"
        mock_form.return_value.last_name.data = "Custard"
        test_principle = SearchPrinciple("anuserid", "anfirstname", "ansurname", "Active", "an@email.com")
        test_jwt_payload = JWTPayload(None, None, None, None, None, None, test_principle)
        with self.client.session_transaction() as sess:
            sess["jwt_payload"] = test_jwt_payload
        mock_account.return_value.change_name.return_value.status_code = 500
        result = self.client.post(url_for('my_account.change_details'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.change_name.assert_called_with("Rhubarb", "Custard")

    @patch('server.views.my_account.ChangeDetailsForm')
    @patch('server.views.my_account.AccountApiService')
    @patch('server.views.my_account.AuditAPIService')
    def test_change_details_post_ok(self, mock_audit, mock_account, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.first_name.data = "Rhubarb"
        mock_form.return_value.last_name.data = "Custard"
        test_principle = SearchPrinciple("anuserid", "anfirstname", "ansurname", "Active", "an@email.com")
        test_jwt_payload = JWTPayload(None, None, None, None, None, None, test_principle)
        with self.client.session_transaction() as sess:
            sess["jwt_payload"] = test_jwt_payload
        mock_account.return_value.change_name.return_value.status_code = 200
        result = self.client.post(url_for('my_account.change_details'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("my_account.my_account_page"))
        mock_account.return_value.change_name.assert_called_with("Rhubarb", "Custard")
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["jwt_payload"].principle.first_name, "Rhubarb")
            self.assertEqual(sess["jwt_payload"].principle.surname, "Custard")

    @patch('server.views.my_account.ChangePasswordForm')
    def test_change_password_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        result = self.client.get(url_for('my_account.change_password'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Change your password", result.text)

    @patch('server.views.my_account.ChangePasswordForm')
    @patch('server.views.my_account.AuthenticationApi')
    @patch('server.views.my_account.AuditAPIService')
    @patch('server.views.my_account.flash')
    @patch('server.views.my_account.AccountApiService')
    def test_change_password_post_ok(self, mock_account, mock_flask, mock_audit, mock_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.current_password.data = "anpassword"
        mock_form.return_value.new_passwords.new_password.data = "anotherpassword"
        mock_auth.return_value.authenticate.return_value = True, None
        mock_account.return_value.change_password.return_value.status_code = 200
        result = self.client.post(url_for('my_account.change_password'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("my_account.my_account_page"))
        mock_auth.return_value.authenticate.assert_called_with("anpassword")
        mock_account.return_value.change_password.assert_called_with("anotherpassword")
        mock_flask.assert_called_with("Your password has been changed", category="success")

    @patch('server.views.my_account.ChangePasswordForm')
    @patch('server.views.my_account.AuthenticationApi')
    def test_change_password_post_current_wrong(self, mock_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.current_password.data = "anpassword"
        mock_form.return_value.current_password.errors = []
        mock_auth.return_value.authenticate.return_value = False, None
        result = self.client.post(url_for('my_account.change_password'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Change your password", result.text)
        mock_auth.return_value.authenticate.assert_called_with("anpassword")
        self.assertEqual(mock_form.return_value.current_password.errors, ["Current password is not correct"])

    @patch('server.views.my_account.ChangePasswordForm')
    @patch('server.views.my_account.AuthenticationApi')
    @patch('server.views.my_account.AccountApiService')
    def test_change_password_post_blacklisted(self, mock_account, mock_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.current_password.data = "anpassword"
        mock_form.return_value.new_passwords.new_password.data = "anotherpassword"
        mock_form.return_value.new_passwords.new_password.errors = []
        mock_form.return_value.new_passwords.confirm_new_password.errors = []
        mock_auth.return_value.authenticate.return_value = True, None
        mock_account.return_value.change_password.return_value.status_code = 400
        mock_account.return_value.change_password.return_value.text = "Password is blacklisted"
        result = self.client.post(url_for('my_account.change_password'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Change your password", result.text)
        self.assertEqual(mock_form.return_value.new_passwords.errors, {
            'new_passwords': 'This password is not secure enough'})
        mock_auth.return_value.authenticate.assert_called_with("anpassword")
        mock_account.return_value.change_password.assert_called_with("anotherpassword")

    @patch('server.views.my_account.ChangePasswordForm')
    @patch('server.views.my_account.AuthenticationApi')
    @patch('server.views.my_account.AccountApiService')
    def test_change_password_post_fail(self, mock_account, mock_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.current_password.data = "anpassword"
        mock_form.return_value.new_passwords.new_password.data = "anotherpassword"
        mock_form.return_value.new_passwords.new_password.errors = []
        mock_form.return_value.new_passwords.confirm_new_password.errors = []
        mock_auth.return_value.authenticate.return_value = True, None
        mock_account.return_value.change_password.return_value.status_code = 500
        result = self.client.post(url_for('my_account.change_password'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_auth.return_value.authenticate.assert_called_with("anpassword")
        mock_account.return_value.change_password.assert_called_with("anotherpassword")

    @patch('server.views.my_account.SearchSearchesForm')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    def test_active_searches_get_no_search(self, mock_paginate, mock_sllc, mock_form):
        mock_form.return_value.validate.return_value = False
        mock_form.return_value.errors = []
        mock_search_1 = MagicMock()
        mock_search_1.document_url = None
        mock_search_1.repeat_searches = []
        mock_repeat_search = MagicMock()
        mock_repeat_search.document_url = "andocumenturl"
        mock_search_2 = MagicMock()
        mock_search_2.document_url = "andocumenturl"
        mock_search_2.lapsed_date = None
        mock_search_2.repeat_searches = [mock_repeat_search]
        mock_sllc.return_value.get_paid_search_items.return_value = [mock_search_1, mock_search_2]
        mock_paginate.return_value = [], {}, 0
        result = self.client.get(url_for('my_account.active_searches'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Active searches", result.text)
        mock_sllc.return_value.get_paid_search_items.assert_called_with('mock_user')
        mock_sllc.return_value.check_for_completed_doc_url.assert_has_calls(
            [call(mock_search_1), call(mock_search_2), call(mock_repeat_search)])
        mock_paginate.assert_called_with([mock_search_2], 'my_account.active_searches', 15, 1, {'search_term': None})

    @patch('server.views.my_account.SearchSearchesForm')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    @patch('server.views.my_account.search_in_searches')
    def test_active_searches_get_search(self, mock_sins, mock_paginate, mock_sllc, mock_form):
        mock_form.return_value.validate.return_value = True
        mock_form.return_value.errors = []
        mock_search_1 = MagicMock()
        mock_search_1.document_url = None
        mock_search_1.repeat_searches = []
        mock_repeat_search = MagicMock()
        mock_repeat_search.document_url = "andocumenturl"
        mock_search_2 = MagicMock()
        mock_search_2.document_url = "andocumenturl"
        mock_search_2.lapsed_date = None
        mock_search_2.repeat_searches = [mock_repeat_search]
        mock_sllc.return_value.get_paid_search_items.return_value = [mock_search_1, mock_search_2]
        mock_paginate.return_value = [], {}, 0
        mock_sins.return_value = [], []
        result = self.client.get(url_for('my_account.active_searches', submit="y"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Active searches", result.text)
        mock_sllc.return_value.get_paid_search_items.assert_called_with('mock_user')
        mock_sllc.return_value.check_for_completed_doc_url.assert_has_calls(
            [call(mock_search_1), call(mock_search_2), call(mock_repeat_search)])
        mock_paginate.assert_called_with([], 'my_account.active_searches', 15, 1, {'search_term': None})

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.Fernet')
    def test_view_search(self, mock_fernet, mock_sllc):
        mock_search = PaidSearchItem()
        mock_search.search_id = "ansearchid"
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_fernet.return_value.encrypt.return_value = b'anencryptedthing'
        result = self.client.get(url_for('my_account.view_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("paid_search.get_paid_search", enc_search_id="anencryptedthing"))
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')
        mock_fernet.return_value.encrypt.assert_called_with(b"view_ansearchid")
        expected_search_state = SearchState(search_reference="ansearchid")
        expected_search_state.previously_completed = True
        expected_search_state.charges = []
        with self.client.session_transaction() as sess:
            sess["paid_searches"]['anencryptedthing'] = {"paid_search_item": mock_search,
                                                         "search_state": expected_search_state}

    @patch('server.views.my_account.SearchSearchesForm')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    def test_expired_searches_get_no_search(self, mock_paginate, mock_sllc, mock_form):
        mock_form.return_value.validate.return_value = False
        mock_form.return_value.errors = []
        mock_search_1 = MagicMock()
        mock_search_1.document_url = None
        mock_search_1.repeat_searches = []
        mock_repeat_search = MagicMock()
        mock_repeat_search.document_url = "andocumenturl"
        mock_search_2 = MagicMock()
        mock_search_2.document_url = "andocumenturl"
        mock_search_2.lapsed_date = None
        mock_search_2.repeat_searches = [mock_repeat_search]
        mock_sllc.return_value.get_paid_search_items.return_value = [mock_search_1, mock_search_2]
        mock_paginate.return_value = [], {}, 0
        result = self.client.get(url_for('my_account.expired_searches'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Active searches", result.text)
        mock_sllc.return_value.get_paid_search_items.assert_called_with('mock_user')
        mock_paginate.assert_called_with([mock_search_1], 'my_account.expired_searches', 15, 1, {'search_term': None})

    @patch('server.views.my_account.SearchSearchesForm')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    @patch('server.views.my_account.search_in_searches')
    def test_expired_searches_get_search(self, mock_sins, mock_paginate, mock_sllc, mock_form):
        mock_form.return_value.validate.return_value = True
        mock_form.return_value.errors = []
        mock_search_1 = MagicMock()
        mock_search_1.document_url = None
        mock_search_1.repeat_searches = []
        mock_repeat_search = MagicMock()
        mock_repeat_search.document_url = "andocumenturl"
        mock_search_2 = MagicMock()
        mock_search_2.document_url = "andocumenturl"
        mock_search_2.lapsed_date = None
        mock_search_2.repeat_searches = [mock_repeat_search]
        mock_sllc.return_value.get_paid_search_items.return_value = [mock_search_1, mock_search_2]
        mock_paginate.return_value = [], {}, 0
        mock_sins.return_value = [], []
        result = self.client.get(url_for('my_account.expired_searches', submit="y"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Active searches", result.text)
        mock_sllc.return_value.get_paid_search_items.assert_called_with('mock_user')
        mock_paginate.assert_called_with([], 'my_account.expired_searches', 15, 1, {'search_term': None})

    @patch('server.views.my_account.SearchLocalLandChargeService')
    def test_repeat_search_lapsed(self, mock_sllc):
        mock_search = MagicMock()
        mock_search.lapsed_date = "andate"
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        result = self.client.get(url_for('my_account.repeat_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')

    @patch('server.views.my_account.GovPayService')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.flash')
    def test_repeat_search_refund(self, mock_flash, mock_sllc, mock_gov_pay):
        mock_search = MagicMock()
        mock_search.lapsed_date = None
        mock_search.payment_id = "anpaymentid"
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_gov_pay.return_value.get_payment.return_value = {
            "refund_summary": {
                "status": "FULL"
            }
        }
        result = self.client.get(url_for('my_account.repeat_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("my_account.paid_search_review", search_id="ansearchid"))
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')
        mock_gov_pay.return_value.get_payment.assert_called_with("anpaymentid")
        mock_flash.assert_called_with('You cannot request a repeat on this search as it has been refunded to you.<br>'
                                      'You can request and download another official search result.<br>'
                                      'Official search results are &pound;15.00.')

    @patch('server.views.my_account.GovPayService')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.CheckMigrationStatus')
    def test_repeat_search_maintenance(self, mock_mig_status, mock_sllc, mock_gov_pay):
        mock_search = MagicMock()
        mock_search.lapsed_date = None
        mock_search.payment_id = "anpaymentid"
        mock_search.search_extent = {"an": "extent"}
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_gov_pay.return_value.get_payment.return_value = {
            "refund_summary": {
                "status": "NOT"
            }
        }
        mock_mig_status.process.return_value = {"flag": "fail_maintenance"}
        result = self.client.get(url_for('my_account.repeat_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("search.no_information_available"))
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')
        mock_gov_pay.return_value.get_payment.assert_called_with("anpaymentid")
        mock_mig_status.process.assert_called_with({"an": "extent"})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["authority_data"], {"flag": "fail_maintenance"})

    @patch('server.views.my_account.GovPayService')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.CheckMigrationStatus')
    def test_repeat_search_weird(self, mock_mig_status, mock_sllc, mock_gov_pay):
        mock_search = MagicMock()
        mock_search.lapsed_date = None
        mock_search.payment_id = "anpaymentid"
        mock_search.search_extent = {"an": "extent"}
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_gov_pay.return_value.get_payment.return_value = {
            "refund_summary": {
                "status": "NOT"
            }
        }
        mock_mig_status.process.return_value = {"flag": "aardvark"}
        result = self.client.get(url_for('my_account.repeat_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')
        mock_gov_pay.return_value.get_payment.assert_called_with("anpaymentid")
        mock_mig_status.process.assert_called_with({"an": "extent"})

    @patch('server.views.my_account.GovPayService')
    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.CheckMigrationStatus')
    @patch('server.views.my_account.PaidSearchUtils')
    @patch('server.views.my_account.Fernet')
    @patch('server.views.my_account.AuditAPIService')
    def test_repeat_search_ok(self, mock_audit, mock_fernet, mock_paid_utils, mock_mig_status, mock_sllc,
                              mock_gov_pay):
        mock_search = MagicMock()
        mock_search.lapsed_date = None
        mock_search.payment_id = "anpaymentid"
        mock_search.search_id = "ansearchid"
        mock_search.search_area_description = "ansearchdescription"
        mock_search.search_extent = {"an": "extent"}
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_gov_pay.return_value.get_payment.return_value = {
            "refund_summary": {
                "status": "NOT"
            }
        }
        mock_mig_status.process.return_value = {"flag": "pass"}
        mock_paid_utils.search_by_area.return_value = ["some", "charges"]
        mock_fernet.return_value.encrypt.return_value = b'encryptedthing'
        result = self.client.get(url_for('my_account.repeat_search', search_id="ansearchid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("paid_search.get_paid_search", enc_search_id="encryptedthing"))
        mock_sllc.return_value.get_paid_search_item.assert_called_with('mock_user', 'ansearchid')
        mock_gov_pay.return_value.get_payment.assert_called_with("anpaymentid")
        mock_mig_status.process.assert_called_with({"an": "extent"})
        mock_paid_utils.search_by_area.assert_called_with({"an": "extent"})
        mock_fernet.return_value.encrypt.assert_called_with(b"repeat_ansearchid")
        with self.client.session_transaction() as sess:
            self.assertEqual(
                sess["paid_searches"]['encryptedthing'],
                {
                    'payment_state': PaymentState(payment_id='anpaymentid',
                                                  description='ansearchdescription',
                                                  state={},
                                                  reference='N/A',
                                                  amount=0,
                                                  payment_provider=None,
                                                  card_brand=None),
                    'search_state': SearchState(search_extent={'an': 'extent'},
                                                charges=['some', 'charges'],
                                                address='ansearchdescription',
                                                parent_search='ansearchid',
                                                search_reference=None,
                                                previously_completed=None,
                                                free_search_id=None)
                }
            )

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.search_by_area')
    @patch('server.views.my_account.AuditAPIService')
    def test_paid_search_review(self, mock_audit, mock_by_area, mock_sllc):
        mock_search = MagicMock()
        mock_search.search_id = "ansearchid"
        mock_search.search_area_description = "ansearchdescription"
        mock_search.search_extent = {"an": "extent"}
        mock_sllc.return_value.get_paid_search_item.return_value = mock_search
        mock_by_area.return_value = redirect("anurl")
        result = self.client.get(url_for('my_account.paid_search_review', search_id="ansearchid"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")

    def test_search_in_searches_with_number_parent(self):
        mock_repeat_search_1 = MagicMock()
        mock_repeat_search_1.search_id = 12
        mock_repeat_search_2 = MagicMock()
        mock_repeat_search_2.search_id = 34
        mock_search_1 = MagicMock()
        mock_search_1.repeat_searches = [mock_repeat_search_1, mock_repeat_search_2]
        mock_search_1.search_id = 56
        mock_search_1.search_area_description = "An area description"
        mock_search_2 = MagicMock()
        mock_search_2.repeat_searches = []
        mock_search_2.search_id = 78
        mock_search_2.search_area_description = "A different thing"
        result = search_in_searches("7 8", [mock_search_1, mock_search_2])
        self.assertEqual(([mock_search_2], []), result)

    def test_search_in_searches_with_number_repeat(self):
        mock_repeat_search_1 = MagicMock()
        mock_repeat_search_1.search_id = 12
        mock_repeat_search_2 = MagicMock()
        mock_repeat_search_2.search_id = 34
        mock_search_1 = MagicMock()
        mock_search_1.repeat_searches = [mock_repeat_search_1, mock_repeat_search_2]
        mock_search_1.search_id = 56
        mock_search_1.search_area_description = "An area description"
        mock_search_2 = MagicMock()
        mock_search_2.repeat_searches = []
        mock_search_2.search_id = 78
        mock_search_2.search_area_description = "A different thing"
        result = search_in_searches("3 4", [mock_search_1, mock_search_2])
        self.assertEqual(([mock_search_1], [56]), result)

    def test_search_in_searches_with_string(self):
        mock_repeat_search_1 = MagicMock()
        mock_repeat_search_1.search_id = 12
        mock_repeat_search_2 = MagicMock()
        mock_repeat_search_2.search_id = 34
        mock_search_1 = MagicMock()
        mock_search_1.repeat_searches = [mock_repeat_search_1, mock_repeat_search_2]
        mock_search_1.search_id = 56
        mock_search_1.search_area_description = "An area description"
        mock_search_2 = MagicMock()
        mock_search_2.repeat_searches = []
        mock_search_2.search_id = 78
        mock_search_2.search_area_description = "A different thing"
        result = search_in_searches("different", [mock_search_1, mock_search_2])
        self.assertEqual(([mock_search_2], []), result)

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    @patch('server.views.my_account.SearchFreeSearchesForm')
    def test_free_searches_get(self, mock_form, mock_paginate, mock_sllc):
        mock_form.return_value.validate_on_submit.return_value = False
        mock_sllc.return_value.get_free_search_items.return_value = {
            "pages": 1, "total": 1, "items": [{"search-date": "2020-02-01"}]
        }
        mock_paginate.return_value = [], {}, 0
        result = self.client.get(url_for('my_account.free_searches'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Free searches", result.text)
        mock_sllc.return_value.get_free_search_items.assert_called_with('mock_user', 15, 1)
        mock_paginate.assert_called_with(None, 'my_account.free_searches', 15, 1, no_of_pages=1, no_of_items=1)

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    @patch('server.views.my_account.SearchFreeSearchesForm')
    def test_free_searches_post_nowt(self, mock_form, mock_paginate, mock_sllc):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.search_term.data = " thingy "
        mock_form.return_value.search_term.errors = []
        mock_sllc.return_value.get_free_search_for_user_by_search_id.return_value = None
        mock_sllc.return_value.get_free_search_items.return_value = {
            "pages": 1, "total": 1, "items": [{"search-date": "2020-02-01"}]
        }
        mock_paginate.return_value = [], {}, 0
        result = self.client.post(url_for('my_account.free_searches'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Free searches", result.text)
        mock_sllc.return_value.get_free_search_for_user_by_search_id.assert_called_with('mock_user', "thingy")
        self.assertEqual(['You have entered an invalid Search ID. Check it and try again'],
                         mock_form.return_value.search_term.errors)
        mock_paginate.assert_called_with(None, 'my_account.free_searches', 15, 1, no_of_pages=1, no_of_items=1)

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.calculate_pagination_info')
    @patch('server.views.my_account.SearchFreeSearchesForm')
    def test_free_searches_post_found(self, mock_form, mock_paginate, mock_sllc):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.search_term.data = " thingy "
        mock_sllc.return_value.get_free_search_for_user_by_search_id.return_value = [{"search-date": "2022-01-10"}]
        result = self.client.post(url_for('my_account.free_searches'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Free searches", result.text)
        mock_sllc.return_value.get_free_search_for_user_by_search_id.assert_called_with('mock_user', "thingy")

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.AuditAPIService')
    @patch('server.views.my_account.search_by_area')
    def test_free_search_review_not_found(self, mock_area, mock_audit, mock_sllc):
        mock_sllc.return_value.get_free_search_for_user_by_search_id.return_value = None
        result = self.client.get(url_for('my_account.free_search_review', search_id="thingy"))
        self.assertEqual(result.status_code, 404)
        self.assertIn("Page not found", result.text)
        mock_sllc.return_value.get_free_search_for_user_by_search_id.assert_called_with('mock_user', "thingy")
        mock_area.assert_not_called()

    @patch('server.views.my_account.SearchLocalLandChargeService')
    @patch('server.views.my_account.AuditAPIService')
    @patch('server.views.my_account.search_by_area')
    def test_free_search_review_found(self, mock_area, mock_audit, mock_sllc):
        mock_sllc.return_value.get_free_search_for_user_by_search_id.return_value = [
            {"search-extent": {"an": "extent"},
             "address": "anaddress"}
        ]
        mock_area.return_value = redirect("anurl")
        result = self.client.get(url_for('my_account.free_search_review', search_id="thingy"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")
        mock_sllc.return_value.get_free_search_for_user_by_search_id.assert_called_with('mock_user', "thingy")
        mock_area.assert_called_with({'an': 'extent'}, 'anaddress')
