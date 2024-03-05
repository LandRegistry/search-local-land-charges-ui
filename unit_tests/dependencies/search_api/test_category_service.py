from unittest import TestCase
from server import main
from unittest.mock import MagicMock
from flask import g, current_app
from server.dependencies.search_api.category_service import CategoryService
from unit_tests.utilities_tests import super_test_context


class TestCategoryService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_get(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            local_land_charge_service = CategoryService(current_app.config)

            local_land_charge_service.get()

            g.requests.get.assert_called_with(
                "{}/search/categories".format(current_app.config['SEARCH_API_URL']),
                headers={'Content-Type': 'application/json'}
            )
