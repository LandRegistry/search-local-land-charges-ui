from unittest import TestCase
from server import main
from unittest.mock import MagicMock
from flask import g, current_app
from server.dependencies.maintain_api.category_service import CategoryService
from unit_tests.utilities_tests import super_test_context


class TestCategoryService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_get_all_and_sub(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            local_land_charge_service = CategoryService(current_app.config)

            result = local_land_charge_service.get_all_and_sub()

            g.requests.get.assert_called_with(
                "{}/categories/all".format(current_app.config['MAINTAIN_API_URL']),
                headers={'Content-Type': 'application/json'}
            )
            self.assertEqual(result, g.requests.get.return_value.json.return_value)

    def test_get_sub_category(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            local_land_charge_service = CategoryService(current_app.config)

            result = local_land_charge_service.get_sub_category("acategory", "asubcategory")

            g.requests.get.assert_called_with(
                "{}/categories/acategory/sub-categories/asubcategory".format(current_app.config['MAINTAIN_API_URL']),
                headers={'Content-Type': 'application/json'}
            )
            self.assertEqual(result, g.requests.get.return_value)

    def test_get_category(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            local_land_charge_service = CategoryService(current_app.config)

            result = local_land_charge_service.get_category("acategory")

            g.requests.get.assert_called_with(
                "{}/categories/acategory".format(current_app.config['MAINTAIN_API_URL']),
                headers={'Content-Type': 'application/json'}
            )
            self.assertEqual(result, g.requests.get.return_value)

    def test_get(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            local_land_charge_service = CategoryService(current_app.config)

            result = local_land_charge_service.get()

            g.requests.get.assert_called_with(
                "{}/categories".format(current_app.config['MAINTAIN_API_URL']),
                headers={'Content-Type': 'application/json'}
            )
            self.assertEqual(result, g.requests.get.return_value.json.return_value)
