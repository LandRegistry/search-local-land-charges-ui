from flask import url_for
from unittest.mock import patch
from server.main import app
from unittest import TestCase


class TestAccountAdmin(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    def test_register_get(self):
        result = self.client.get(url_for('account_admin.register'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Create an account", result.text)

    @patch('server.views.account_admin.RegisterForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_register_post_409(self, mock_account, mock_register):
        mock_register.return_value.validate_on_submit.return_value = True
        mock_account.return_value.register.return_value = {
            "status": 409
        }
        mock_register.return_value.email_addresses.email_address.errors = []
        mock_register.return_value.email_addresses.confirm_email_address.errors = []
        mock_register.return_value.email_addresses.email_address.data = "some@email.com"

        result = self.client.post(url_for('account_admin.register'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Create an account", result.text)
        self.assertEqual(mock_register.return_value.email_addresses.errors,
                         {'email_addresses': ['There is an existing account for some@email.com, try again']})

    @patch('server.views.account_admin.RegisterForm')
    @patch('server.views.account_admin.AccountApiService')
    @patch('server.views.account_admin.AuditAPIService')
    def test_register_post_ok(self, mock_audit, mock_account, mock_register):
        mock_register.return_value.validate_on_submit.return_value = True
        mock_account.return_value.register.return_value = {
            "status": 200,
            "data": {"id": "anuserid"}
        }
        mock_register.return_value.email_address.errors = []
        mock_register.return_value.confirm_email_address.errors = []
        mock_register.return_value.email_address.data = "some@email.com"

        result = self.client.post(url_for('account_admin.register'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.check_your_email"))

    def test_check_your_email_ok(self):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        result = self.client.get(url_for('account_admin.check_your_email'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("anemail@email.com", result.text)
        self.assertIn("Check your email", result.text)

    def test_check_your_email_no_email(self):
        result = self.client.get(url_for('account_admin.check_your_email'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.register"))

    def test_resend_activation_email_no_email(self):
        result = self.client.get(url_for('account_admin.resend_activation_email'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("sign_in.handle_sign_in"))

    @patch('server.views.account_admin.AccountApiService')
    def test_resend_activation_email_ok(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.resend_email.return_value.status_code = 200
        result = self.client.get(url_for('account_admin.resend_activation_email'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.check_your_email"))
        mock_account.return_value.resend_email.assert_called_with("anemail@email.com")

    @patch('server.views.account_admin.AccountApiService')
    def test_resend_activation_email_error(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.resend_email.return_value.status_code = 500
        result = self.client.get(url_for('account_admin.resend_activation_email'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.resend_email.assert_called_with("anemail@email.com")

    @patch('server.views.account_admin.AccountApiService')
    def test_activate_account_ok(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.validate_token.return_value = {
            "status": "Valid",
            "action": "activation",
            "user_id": "anuserid"
        }
        mock_account.return_value.activate_user.return_value.status_code = 200
        result = self.client.get(url_for('account_admin.activate_account', activate_token="antoken"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("You have activated your account", result.text)
        mock_account.return_value.validate_token.assert_called_with("antoken")
        mock_account.return_value.activate_user.assert_called_with("antoken", "anuserid")

    @patch('server.views.account_admin.AccountApiService')
    def test_activate_account_fail(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.validate_token.return_value = {
            "status": "Valid",
            "action": "activation",
            "user_id": "anuserid"
        }
        mock_account.return_value.activate_user.return_value.status_code = 500
        result = self.client.get(url_for('account_admin.activate_account', activate_token="antoken"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.validate_token.assert_called_with("antoken")
        mock_account.return_value.activate_user.assert_called_with("antoken", "anuserid")

    @patch('server.views.account_admin.AccountApiService')
    def test_activate_account_expired(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.validate_token.return_value = {
            "status": "Expired"
        }
        result = self.client.get(url_for('account_admin.activate_account', activate_token="antoken"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.expired_activation", page_type="expired-activation"))
        mock_account.return_value.validate_token.assert_called_with("antoken")
        mock_account.return_value.activate_user.assert_not_called()

    @patch('server.views.account_admin.AccountApiService')
    def test_activate_account_error(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        mock_account.return_value.validate_token.return_value = {
            "status": "Rudyard Kipling"
        }
        result = self.client.get(url_for('account_admin.activate_account', activate_token="antoken"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.expired_activation", page_type="invalid-activation"))
        mock_account.return_value.validate_token.assert_called_with("antoken")
        mock_account.return_value.activate_user.assert_not_called()

    def test_password_check_your_email_ok(self):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        result = self.client.get(url_for('account_admin.password_check_your_email'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("anemail@email.com", result.text)
        self.assertIn("Check your email", result.text)

    def test_password_check_your_email_no_email(self):
        result = self.client.get(url_for('account_admin.password_check_your_email'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("sign_in.handle_sign_in"))

    @patch('server.views.account_admin.AccountApiService')
    def test_resend_reset_password_ok(self, mock_account):
        with self.client.session_transaction() as sess:
            sess["registered_email"] = "anemail@email.com"
        result = self.client.get(url_for('account_admin.resend_reset_password'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.password_check_your_email"))
        mock_account.return_value.request_reset_password_email.assert_called_with("anemail@email.com")

    def test_resend_reset_password_no_email(self):
        result = self.client.get(url_for('account_admin.resend_reset_password'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("sign_in.handle_sign_in"))

    def test_expired_activation_get(self):
        result = self.client.get(url_for('account_admin.expired_activation', page_type="expired-activation"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Your activation link has expired", result.text)

    @patch('server.views.account_admin.ExpiredActivationForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_expired_activation_post_fail(self, mock_account, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.email_address.data = "an@email.com"
        mock_account.return_value.resend_email.return_value.status_code = 500

        result = self.client.post(url_for('account_admin.expired_activation', page_type="expired-activation"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.resend_email.assert_called_with("an@email.com")

    @patch('server.views.account_admin.ExpiredActivationForm')
    @patch('server.views.account_admin.AccountApiService')
    @patch('server.views.account_admin.AuditAPIService')
    def test_expired_activation_post_ok(self, mock_audit, mock_account, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.email_address.data = "an@email.com"
        mock_account.return_value.resend_email.return_value.status_code = 200

        result = self.client.post(url_for('account_admin.expired_activation', page_type="expired-activation"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.check_your_email"))
        mock_account.return_value.resend_email.assert_called_with("an@email.com")

    @patch('server.views.account_admin.AccountApiService')
    def test_change_password_with_token_get_invalid(self, mock_account):
        mock_account.return_value.validate_token.return_value = None

        result = self.client.get(url_for('account_admin.change_password_with_token', password_token="anpwtoken"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.reset_password", page_type="invalid-password-link"))
        mock_account.return_value.validate_token.assert_called_with("anpwtoken")

    @patch('server.views.account_admin.AccountApiService')
    def test_expired_activation_with_token_get_expired(self, mock_account):
        mock_account.return_value.validate_token.return_value = {"status": "Expired"}

        result = self.client.get(url_for('account_admin.change_password_with_token', password_token="anpwtoken"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.reset_password", page_type="expired-password-link"))
        mock_account.return_value.validate_token.assert_called_with("anpwtoken")

    @patch('server.views.account_admin.ChangePasswordWithTokenForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_expired_activation_with_token_post_blacklisted(self, mock_account, mock_form):
        mock_account.return_value.validate_token.return_value = {
            "status": "Valid", "action": "password", "user_id": "anuserid"
        }
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.passwords.password.data = "anpassword"
        mock_form.return_value.passwords.password.errors = []
        mock_form.return_value.passwords.confirm_password.errors = []
        mock_account.return_value.set_password.return_value.status_code = 400
        mock_account.return_value.set_password.return_value.text = "Password is blacklisted"

        result = self.client.get(url_for('account_admin.change_password_with_token', password_token="anpwtoken"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Change your password", result.text)
        mock_account.return_value.validate_token.assert_called_with("anpwtoken")
        mock_account.return_value.set_password.assert_called_with("anpwtoken", "anuserid", "anpassword")
        self.assertEqual(mock_form.return_value.passwords.errors, {"passwords": ['This password is not secure enough']})

    @patch('server.views.account_admin.ChangePasswordWithTokenForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_expired_activation_with_token_post_fail(self, mock_account, mock_form):
        mock_account.return_value.validate_token.return_value = {
            "status": "Valid", "action": "password", "user_id": "anuserid"
        }
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.passwords.password.data = "anpassword"
        mock_form.return_value.passwords.password.errors = []
        mock_form.return_value.passwords.confirm_password.errors = []
        mock_account.return_value.set_password.return_value.status_code = 500

        result = self.client.get(url_for('account_admin.change_password_with_token', password_token="anpwtoken"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.validate_token.assert_called_with("anpwtoken")
        mock_account.return_value.set_password.assert_called_with("anpwtoken", "anuserid", "anpassword")

    @patch('server.views.account_admin.flash')
    @patch('server.views.account_admin.AuditAPIService')
    @patch('server.views.account_admin.ChangePasswordWithTokenForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_expired_activation_with_token_post_ok(self, mock_account, mock_form, mock_audit, mock_flash):
        mock_account.return_value.validate_token.return_value = {
            "status": "Valid", "action": "password", "user_id": "anuserid"
        }
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.passwords.password.data = "anpassword"
        mock_account.return_value.set_password.return_value.status_code = 200

        result = self.client.get(url_for('account_admin.change_password_with_token', password_token="anpwtoken"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("sign_in.handle_sign_in"))
        mock_account.return_value.validate_token.assert_called_with("anpwtoken")
        mock_account.return_value.set_password.assert_called_with("anpwtoken", "anuserid", "anpassword")
        mock_flash.assert_called_with('Your password has been changed', category='success')

    @patch('server.views.account_admin.ResetPasswordForm')
    def test_reset_password_get_expired(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False

        result = self.client.get(url_for('account_admin.reset_password',
                                         page_type="expired-password-link"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Your link has expired", result.text)

    @patch('server.views.account_admin.ResetPasswordForm')
    def test_reset_password_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False

        result = self.client.get(url_for('account_admin.reset_password',
                                         page_type="reset-password"))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Enter your email address", result.text)

    @patch('server.views.account_admin.AuditAPIService')
    @patch('server.views.account_admin.ResetPasswordForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_reset_password_post_ok(self, mock_account, mock_form, mock_audit):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.email_address.data = "an@email.com"
        mock_account.return_value.request_reset_password_email.return_value.status_code = 201

        result = self.client.get(url_for('account_admin.reset_password', page_type="reset-password"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for("account_admin.password_check_your_email"))
        mock_account.return_value.request_reset_password_email.assert_called_with("an@email.com")

    @patch('server.views.account_admin.ResetPasswordForm')
    @patch('server.views.account_admin.AccountApiService')
    def test_reset_password_post_fail(self, mock_account, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.email_address.data = "an@email.com"
        mock_account.return_value.request_reset_password_email.return_value.status_code = 500

        result = self.client.get(url_for('account_admin.reset_password', page_type="reset-password"))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_account.return_value.request_reset_password_email.assert_called_with("an@email.com")
