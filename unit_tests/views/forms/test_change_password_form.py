from unittest import TestCase
from server.views.forms.change_password_form import ChangePasswordForm


class TestChangePasswordForm(TestCase):
    def test_change_password_form_invalid_short(self):
        form = ChangePasswordForm()
        form.current_password.data = "Blah"
        form.current_password.raw_data = "Blah"
        form.new_passwords.new_password.data = "Blah"
        form.new_passwords.new_password.raw_data = "Blah"
        form.new_passwords.confirm_new_password.data = "Blah"
        form.new_passwords.confirm_new_password.raw_data = "Blah"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'new_passwords': {'confirm_new_password': ['Enter a password in the correct format'],
                          'new_password': ['Enter a password in the correct format']}}
        )

    def test_change_password_form_invalid_all_lower(self):
        form = ChangePasswordForm()
        form.current_password.data = "Blah"
        form.current_password.raw_data = "Blah"
        form.new_passwords.new_password.data = "qwertyuiop"
        form.new_passwords.new_password.raw_data = "qwertyuiop"
        form.new_passwords.confirm_new_password.data = "qwertyuiop"
        form.new_passwords.confirm_new_password.raw_data = "qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'new_passwords': {'confirm_new_password': ['Enter a password in the correct format'],
                          'new_password': ['Enter a password in the correct format']}}
        )

    def test_change_password_form_invalid_no_num(self):
        form = ChangePasswordForm()
        form.current_password.data = "Blah"
        form.current_password.raw_data = "Blah"
        form.new_passwords.new_password.data = "Qwertyuiop"
        form.new_passwords.new_password.raw_data = "Qwertyuiop"
        form.new_passwords.confirm_new_password.data = "Qwertyuiop"
        form.new_passwords.confirm_new_password.raw_data = "Qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'new_passwords': {'confirm_new_password': ['Enter a password in the correct format'],
                          'new_password': ['Enter a password in the correct format']}}
        )

    def test_change_password_form_invalid_no_punc(self):
        form = ChangePasswordForm()
        form.current_password.data = "Blah"
        form.current_password.raw_data = "Blah"
        form.new_passwords.new_password.data = "Qwertyuiop123"
        form.new_passwords.new_password.raw_data = "Qwertyuiop123"
        form.new_passwords.confirm_new_password.data = "Qwertyuiop123"
        form.new_passwords.confirm_new_password.raw_data = "Qwertyuiop123"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'new_passwords': {'confirm_new_password': ['Enter a password in the correct format'],
                          'new_password': ['Enter a password in the correct format']}}
        )

    def test_change_password_form_valid(self):
        form = ChangePasswordForm()
        form.current_password.data = "Blah"
        form.current_password.raw_data = "Blah"
        form.new_passwords.new_password.data = "Qwertyuiop123!"
        form.new_passwords.new_password.raw_data = "Qwertyuiop123!"
        form.new_passwords.confirm_new_password.data = "Qwertyuiop123!"
        form.new_passwords.confirm_new_password.raw_data = "Qwertyuiop123!"

        self.assertTrue(form.validate())
