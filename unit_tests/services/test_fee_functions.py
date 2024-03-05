from server.app import app
from server.services.fee_functions import format_fee_for_display, format_fee_for_gov_pay
from unittest import TestCase


class TestFeeFunctions(TestCase):

    def setUp(self):
        app.config['Testing'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True

    def test_format_fee_for_display_no_decimal(self):
        fee_in = "1500"
        expected_output = "15"
        actual_output = format_fee_for_display(fee_in)
        self.assertEqual(actual_output, expected_output)

    def test_format_fee_for_display_decimal(self):
        fee_in = "1250"
        expected_output = "12.50"
        actual_output = format_fee_for_display(fee_in)
        self.assertEqual(actual_output, expected_output)

    def test_format_fee_for_gov_pay_valid(self):
        fee_in = "1500"
        expected_output = 1500
        actual_output = format_fee_for_gov_pay(fee_in)
        self.assertEqual(actual_output, expected_output)

    def test_format_fee_for_gov_pay_invalid(self):
        fee_in = "NaN"
        expected_output = 1500
        actual_output = format_fee_for_gov_pay(fee_in)
        self.assertEqual(actual_output, expected_output)
