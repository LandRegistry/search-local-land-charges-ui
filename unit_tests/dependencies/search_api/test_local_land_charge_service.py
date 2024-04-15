from unittest import TestCase
from unittest.mock import MagicMock

from flask import current_app, g

from server import main
from server.dependencies.search_api.local_land_charge_service import (
    LocalLandChargeService,
)
from unit_tests.utilities_tests import super_test_context


class TestLocalLandChargeApiService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_get_with_bounding_box(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            bounding_box = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"

            local_land_charge_service = LocalLandChargeService(current_app.config)

            local_land_charge_service.get(bounding_box)

            g.requests.post.assert_called_with(
                "{}/search/local_land_charges".format(current_app.config["SEARCH_API_URL"]),
                data=bounding_box,
                params={
                    "maxResults": current_app.config["SEARCH_API_MAX_RESULTS"],
                    "filter_sensitive_geometry": "true",
                },
                headers={"Content-Type": "application/json"},
            )

    def test_get_with_bounding_box_and_filter_cancelled(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            bounding_box = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"

            results_filter = "cancelled"
            local_land_charge_service = LocalLandChargeService(current_app.config)

            local_land_charge_service.get(bounding_box, results_filter=results_filter)

            g.requests.post.assert_called_with(
                "{}/search/local_land_charges".format(current_app.config["SEARCH_API_URL"]),
                data=bounding_box,
                params={
                    "maxResults": current_app.config["SEARCH_API_MAX_RESULTS"],
                    "filter": results_filter,
                    "filter_sensitive_geometry": "true",
                },
                headers={"Content-Type": "application/json"},
            )

    def test_get_by_charge_number(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            charge_number = "LLC-1"

            local_land_charge_service = LocalLandChargeService(current_app.config)

            local_land_charge_service.get_by_charge_number(charge_number)

            g.requests.get.assert_called_with(
                "{}/search/local_land_charges/{}".format(current_app.config["SEARCH_API_URL"], charge_number),
                params=None,
            )

    def test_get_history_for_charge(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            charge_number = "LLC-1"

            local_land_charge_service = LocalLandChargeService(current_app.config)

            local_land_charge_service.get_history_for_charge(charge_number)

            g.requests.get.assert_called_with(
                "{}/search/local_land_charges/{}/history".format(current_app.config["SEARCH_API_URL"], charge_number),
                params=None,
            )
