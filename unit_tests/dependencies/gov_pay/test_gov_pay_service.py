from unittest import TestCase
from server.main import app
from unittest.mock import MagicMock
from flask import g, current_app, url_for
from server.dependencies.gov_pay.gov_pay_service import GovPayService
from landregistry.exceptions import ApplicationError
from unit_tests.utilities_tests import super_test_context


class TestGovPayService(TestCase):

    def setUp(self):
        app.config['Testing'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True

    def test_request_payment_contents(self):
        with super_test_context(app):
            g.requests = MagicMock()
            g.locale = 'en'
            response = MagicMock()
            response.status_code = 201

            g.requests.post.return_value = response

            gov_pay_service = GovPayService(current_app.config)

            test_payment_amount = 1
            test_reference = "test reference"
            test_description = "test description"

            expected_request_body = {
                'amount': test_payment_amount,
                'reference': test_reference,
                'description': test_description,
                'return_url': url_for('paid_search.process_pay', enc_search_id='anencid', _external=True),
                'language': 'en'
            }

            expected_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': "Bearer {}".format(current_app.config['GOV_PAY_API_KEY'])
            }

            gov_pay_service.request_payment(test_payment_amount, test_reference, test_description, "anencid")
            g.requests.post.assert_called_with(current_app.config['GOV_PAY_URL'],
                                               json=expected_request_body, headers=expected_headers)

    def test_get_payment_contents(self):
        with super_test_context(app):
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200

            g.requests.get.return_value = response

            gov_pay_service = GovPayService(current_app.config)

            payment_id = "test_id"

            expected_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': "Bearer {}".format(current_app.config['GOV_PAY_API_KEY'])
            }

            gov_pay_service.get_payment(payment_id)
            g.requests.get.assert_called_with("{}/{}".format(current_app.config['GOV_PAY_URL'], payment_id),
                                              headers=expected_headers)

    def test_get_payment_raises_error(self):
        with super_test_context(app):
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 404

            g.requests.get.return_value = response
            gov_pay_service = GovPayService(current_app.config)

            with self.assertRaises(ApplicationError) as context:
                gov_pay_service.get_payment("invalid_id")

            self.assertEqual(context.exception.http_code, 404)

    def test_payment_failure_raises_error(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.locale = 'en'
            response = MagicMock()
            response.status_code = 400

            g.requests.post.return_value = response
            gov_pay_service = GovPayService(current_app.config)

            with self.assertRaises(ApplicationError) as context:
                gov_pay_service.request_payment(1, "test", "test", "anencid")

            self.assertEqual(context.exception.http_code, 400)
