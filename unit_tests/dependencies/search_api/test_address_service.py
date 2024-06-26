from unittest import TestCase
from unittest.mock import MagicMock

from flask import current_app, g

from server.dependencies.search_api.address_service import AddressesService
from server.main import app
from unit_tests.utilities_tests import super_test_context


class TestAddressService(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_search(self):
        with super_test_context(app):
            g.requests.get = MagicMock()

            address_service = AddressesService(current_app.config)

            search_type = "type"
            value = "value"

            address_service.get_by(search_type, value)

            g.requests.get.assert_called_with(
                "{}/search/addresses/{}/{}".format(current_app.config["SEARCH_API_URL"], search_type, "dmFsdWU%3D"),
                params={"base64": "true"},
            )
