from unittest import TestCase
from server.views.forms.change_password_with_token_form import ChangePasswordWithTokenForm


class TestChangePasswordWithTokenForm(TestCase):
    def test_change_password_with_token_form_invalid_short(self):
        form = ChangePasswordWithTokenForm()
        form.passwords.password.data = "Blah"
        form.passwords.password.raw_data = "Blah"
        form.passwords.confirm_password.data = "Blah"
        form.passwords.confirm_password.raw_data = "Blah"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_change_password_with_token_form_invalid_all_lower(self):
        form = ChangePasswordWithTokenForm()
        form.passwords.password.data = "qwertyuiop"
        form.passwords.password.raw_data = "qwertyuiop"
        form.passwords.confirm_password.data = "qwertyuiop"
        form.passwords.confirm_password.raw_data = "qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_change_password_with_token_form_invalid_no_num(self):
        form = ChangePasswordWithTokenForm()
        form.passwords.password.data = "Qwertyuiop"
        form.passwords.password.raw_data = "Qwertyuiop"
        form.passwords.confirm_password.data = "Qwertyuiop"
        form.passwords.confirm_password.raw_data = "Qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_change_password_with_token_form_invalid_no_punc(self):
        form = ChangePasswordWithTokenForm()
        form.passwords.password.data = "Qwertyuiop123"
        form.passwords.password.raw_data = "Qwertyuiop123"
        form.passwords.confirm_password.data = "Qwertyuiop123"
        form.passwords.confirm_password.raw_data = "Qwertyuiop123"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_change_password_with_token_form_valid(self):
        form = ChangePasswordWithTokenForm()
        form.passwords.password.data = "Qwertyuiop123!"
        form.passwords.password.raw_data = "Qwertyuiop123!"
        form.passwords.confirm_password.data = "Qwertyuiop123!"
        form.passwords.confirm_password.raw_data = "Qwertyuiop123!"

        self.assertTrue(form.validate())
