from unittest import TestCase

from server.main import app
from server.views.forms.change_password_with_token_form import (
    ChangePasswordWithTokenForm,
)


class TestChangePasswordWithTokenForm(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True

    def test_change_password_with_token_form_invalid_short(self):
        form = ChangePasswordWithTokenForm()
        form.password.data = "Blah"
        form.password.raw_data = "Blah"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors,
            {
                "password": ["Enter a password in the correct format"],
            },
        )

    def test_change_password_with_token_form_invalid_all_lower(self):
        form = ChangePasswordWithTokenForm()
        form.password.data = "qwertyuiop"
        form.password.raw_data = "qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors,
            {
                "password": ["Enter a password in the correct format"],
            },
        )

    def test_change_password_with_token_form_invalid_no_num(self):
        form = ChangePasswordWithTokenForm()
        form.password.data = "Qwertyuiop"
        form.password.raw_data = "Qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors,
            {
                "password": ["Enter a password in the correct format"],
            },
        )

    def test_change_password_with_token_form_invalid_no_punc(self):
        form = ChangePasswordWithTokenForm()
        form.password.data = "Qwertyuiop123"
        form.password.raw_data = "Qwertyuiop123"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors,
            {
                "password": ["Enter a password in the correct format"],
            },
        )

    def test_change_password_with_token_form_valid(self):
        form = ChangePasswordWithTokenForm()
        form.password.data = "Qwertyuiop123!"
        form.password.raw_data = "Qwertyuiop123!"

        self.assertTrue(form.validate())
