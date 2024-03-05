from unittest import TestCase
from server.views.forms.register_form import RegisterForm


class TestRegisterForm(TestCase):
    def test_register_form_invalid_short(self):
        form = RegisterForm()
        form.first_name.data = "Blah"
        form.first_name.raw_data = "Blah"
        form.last_name.data = "Blah"
        form.last_name.raw_data = "Blah"
        form.email_addresses.email_address.data = "Blah@rhubarb.com"
        form.email_addresses.email_address.raw_data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.raw_data = "Blah@rhubarb.com"
        form.passwords.password.data = "Blah"
        form.passwords.password.raw_data = "Blah"
        form.passwords.confirm_password.data = "Blah"
        form.passwords.confirm_password.raw_data = "Blah"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_register_form_invalid_all_lower(self):
        form = RegisterForm()
        form.first_name.data = "Blah"
        form.first_name.raw_data = "Blah"
        form.last_name.data = "Blah"
        form.last_name.raw_data = "Blah"
        form.email_addresses.email_address.data = "Blah@rhubarb.com"
        form.email_addresses.email_address.raw_data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.raw_data = "Blah@rhubarb.com"
        form.passwords.password.data = "qwertyuiop"
        form.passwords.password.raw_data = "qwertyuiop"
        form.passwords.confirm_password.data = "qwertyuiop"
        form.passwords.confirm_password.raw_data = "qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_register_form_invalid_no_num(self):
        form = RegisterForm()
        form.first_name.data = "Blah"
        form.first_name.raw_data = "Blah"
        form.last_name.data = "Blah"
        form.last_name.raw_data = "Blah"
        form.email_addresses.email_address.data = "Blah@rhubarb.com"
        form.email_addresses.email_address.raw_data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.raw_data = "Blah@rhubarb.com"
        form.passwords.password.data = "Qwertyuiop"
        form.passwords.password.raw_data = "Qwertyuiop"
        form.passwords.confirm_password.data = "Qwertyuiop"
        form.passwords.confirm_password.raw_data = "Qwertyuiop"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_register_form_invalid_no_punc(self):
        form = RegisterForm()
        form.first_name.data = "Blah"
        form.first_name.raw_data = "Blah"
        form.last_name.data = "Blah"
        form.last_name.raw_data = "Blah"
        form.email_addresses.email_address.data = "Blah@rhubarb.com"
        form.email_addresses.email_address.raw_data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.raw_data = "Blah@rhubarb.com"
        form.passwords.password.data = "Qwertyuiop123"
        form.passwords.password.raw_data = "Qwertyuiop123"
        form.passwords.confirm_password.data = "Qwertyuiop123"
        form.passwords.confirm_password.raw_data = "Qwertyuiop123"

        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'passwords': {'confirm_password': ['Enter a password in the correct format'],
                          'password': ['Enter a password in the correct format']}}
        )

    def test_register_form_valid(self):
        form = RegisterForm()
        form.first_name.data = "Blah"
        form.first_name.raw_data = "Blah"
        form.last_name.data = "Blah"
        form.last_name.raw_data = "Blah"
        form.email_addresses.email_address.data = "Blah@rhubarb.com"
        form.email_addresses.email_address.raw_data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.data = "Blah@rhubarb.com"
        form.email_addresses.confirm_email_address.raw_data = "Blah@rhubarb.com"
        form.passwords.password.data = "Qwertyuiop123!"
        form.passwords.password.raw_data = "Qwertyuiop123!"
        form.passwords.confirm_password.data = "Qwertyuiop123!"
        form.passwords.confirm_password.raw_data = "Qwertyuiop123!"

        self.assertTrue(form.validate())
