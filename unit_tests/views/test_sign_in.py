from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import current_app, redirect, url_for

from server.app import app
from server.views.sign_in import check_user
from unit_tests.utilities_tests import super_test_context


class TestSignIn(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()

    @patch("server.views.sign_in.check_user")
    @patch("server.views.sign_in.SignInForm")
    def test_login_valid(self, mock_form, mock_check_user):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_check_user.return_value = redirect("Aardvark")
        result = self.client.post(url_for("sign_in.handle_sign_in"))
        self.assertEqual(result.location, "Aardvark")

    @patch("server.views.sign_in.SignInForm")
    def test_login_already_in(self, mock_form):
        with super_test_context(app):
            mock_form.return_value.validate_on_submit.return_value = False
            with self.client.session_transaction() as session:
                session["profile"] = {"user_id": "anuserid"}
            result = self.client.get(url_for("sign_in.handle_sign_in"))
            self.assertEqual(result.location, url_for("search.search_by_post_code_address"))

    @patch("server.views.sign_in.SignInForm")
    def test_login_no_redirect(self, mock_form):
        with super_test_context(app):
            mock_form.return_value.validate_on_submit.return_value = False
            mock_form.return_value.redirect_uri.data = None
            result = self.client.get(url_for("sign_in.handle_sign_in"))
            self.assertEqual(result.location, url_for("auth.login"))

    @patch("server.views.sign_in.SignInForm")
    @patch("server.views.sign_in.SearchLocalLandChargeService")
    @patch("server.views.sign_in.flash")
    @patch("server.views.sign_in.force_locale")
    def test_login_from_welsh(self, mock_force_locale, mock_flash, mock_sllc, mock_form):
        with super_test_context(app):
            mock_form.return_value.validate_on_submit.return_value = False
            mock_form.return_value.redirect_uri.data = current_app.config["HOME_PAGE_CY_URL"]
            mock_sllc.return_value.get_service_messages.return_value = "Some messages"
            result = self.client.get(
                url_for("sign_in.handle_sign_in"),
                headers={"Referer": current_app.config["HOME_PAGE_CY_URL"]},
            )
            mock_flash.assert_called_with("Some messages", "service_message")
            mock_force_locale.assert_called_with("cy")
            self.assertIn("Sign in", result.text)

    @patch("server.views.sign_in.SignInForm")
    @patch("server.views.sign_in.SearchLocalLandChargeService")
    @patch("server.views.sign_in.flash")
    @patch("server.views.sign_in.force_locale")
    def test_login_from_english(self, mock_force_locale, mock_flash, mock_sllc, mock_form):
        with super_test_context(app):
            mock_form.return_value.validate_on_submit.return_value = False
            mock_form.return_value.redirect_uri.data = "an URI"
            mock_sllc.return_value.get_service_messages.return_value = "Some messages"
            result = self.client.get(
                url_for("sign_in.handle_sign_in"),
                headers={"Referer": current_app.config["HOME_PAGE_EN_URL"]},
            )
            mock_flash.assert_called_with("Some messages", "service_message")
            mock_force_locale.assert_called_with("en")
            self.assertIn("Sign in", result.text)

    @patch("server.views.sign_in.SignInForm")
    @patch("server.views.sign_in.SearchLocalLandChargeService")
    @patch("server.views.sign_in.flash")
    @patch("server.views.sign_in.force_locale")
    def test_login_get(self, mock_force_locale, mock_flash, mock_sllc, mock_form):
        with super_test_context(app):
            mock_form.return_value.validate_on_submit.return_value = False
            mock_form.return_value.redirect_uri.data = "an URI"
            mock_sllc.return_value.get_service_messages.return_value = "Some messages"
            result = self.client.get(url_for("sign_in.handle_sign_in"))
            mock_flash.assert_called_with("Some messages", "service_message")
            self.assertIn("Sign in", result.text)

    @patch("server.views.sign_in.validate")
    @patch("server.views.sign_in.AuthenticationApi")
    def test_check_user_inactive(self, mock_auth, mock_validate):
        with super_test_context(app):
            mock_auth.return_value.authenticate.return_value = (True, "a result")
            mock_userinfo = MagicMock()
            mock_userinfo.principle.status = "Invited"
            mock_validate.return_value = mock_userinfo
            result = check_user(MagicMock())
            self.assertEqual(result.location, url_for("account_admin.resend_activation_email"))

    @patch("server.views.sign_in.validate")
    @patch("server.views.sign_in.AuthenticationApi")
    def test_check_user_active(self, mock_auth, mock_validate):
        with super_test_context(app):
            mock_auth.return_value.authenticate.return_value = (True, "a result")
            mock_userinfo = MagicMock()
            mock_userinfo.principle.status = "Active"
            mock_validate.return_value = mock_userinfo
            mock_form = MagicMock()
            mock_form.redirect_uri.data = "Anurl"
            result = check_user(mock_form)
            self.assertEqual(result.location, "Anurl")

    @patch("server.views.sign_in.AuditAPIService")
    @patch("server.views.sign_in.validate")
    @patch("server.views.sign_in.AuthenticationApi")
    def test_check_user_locked(self, mock_auth, mock_validate, mock_audit):
        with super_test_context(app):
            mock_auth.return_value.authenticate.return_value = (False, {"locked": True})
            mock_userinfo = MagicMock()
            mock_userinfo.principle.status = "Active"
            mock_validate.return_value = mock_userinfo
            mock_form = MagicMock()
            mock_form.redirect_uri.data = "Anurl"
            result = check_user(mock_form)
            self.assertEqual(
                mock_form.username_password.errors,
                {
                    "username_password": [
                        "You tried to log in using an invalid username or password. For security "
                        "reasons, your account status has been changed to inactive"
                    ]
                },
            )
            self.assertIsNone(result)

    @patch("server.views.sign_in.validate")
    @patch("server.views.sign_in.AuthenticationApi")
    def test_check_user_fail(
        self,
        mock_auth,
        mock_validate,
    ):
        with super_test_context(app):
            mock_auth.return_value.authenticate.return_value = (
                False,
                {"locked": False},
            )
            mock_userinfo = MagicMock()
            mock_userinfo.principle.status = "Active"
            mock_validate.return_value = mock_userinfo
            mock_form = MagicMock()
            mock_form.redirect_uri.data = "Anurl"
            result = check_user(mock_form)
            self.assertEqual(
                mock_form.username_password.errors,
                {"username_password": ["Email address and password do not match, try again or reset your password"]},
            )
            self.assertIsNone(result)
