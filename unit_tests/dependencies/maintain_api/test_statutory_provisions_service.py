from unittest import TestCase
from unittest.mock import MagicMock

from flask import current_app, g

from server import main
from server.dependencies.maintain_api.statutory_provisions_service import (
    StatProvService,
)
from unit_tests.utilities_tests import super_test_context


class TestStatProvService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_get(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            stat_prov_service = StatProvService(current_app.config)

            result = stat_prov_service.get(True)

            g.requests.get.assert_called_with(
                "{}/statutory-provisions".format(current_app.config["MAINTAIN_API_URL"]),
                headers={"Content-Type": "application/json"},
                params={"selectable": True},
            )
            self.assertEqual(result, g.requests.get.return_value.json.return_value)

    def test_get_history(self):
        with super_test_context(main.app):
            g.requests = MagicMock()

            stat_prov_service = StatProvService(current_app.config)

            result = stat_prov_service.get_history()

            g.requests.get.assert_called_with(
                "{}/statutory-provisions/history".format(current_app.config["MAINTAIN_API_URL"]),
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(result, g.requests.get.return_value.json.return_value)
