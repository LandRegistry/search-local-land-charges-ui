import unittest
from flask import url_for
from unittest.mock import patch
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.routing import RequestRedirect

from server.main import app
from server.utils.view_function import get_view_function
from server.views.main import terms_and_conditions
from unit_tests.utilities_tests import super_test_context


class TestRepeatSearches(unittest.TestCase):

    def test_get_view_function(self):
        with super_test_context(app):
            self.assertEqual(get_view_function(url_for("main.terms_and_conditions")),
                             (terms_and_conditions, {}))

    @patch('server.utils.view_function.app')
    def test_get_view_function_noallowedpost(self, mock_app):
        mock_app.url_map.bind.return_value.match.side_effect = MethodNotAllowed()
        with super_test_context(app):
            self.assertIsNone(get_view_function(url_for("main.terms_and_conditions"), "POST"))
        mock_app.url_map.bind.return_value.match.assert_called_with(
            url_for("main.terms_and_conditions"), method='POST'
        )

    @patch('server.utils.view_function.app')
    def test_get_view_function_redirect(self, mock_app):
        mock_app.url_map.bind.return_value.match.side_effect = [
            RequestRedirect(url_for("main.map_help")), ("aard", "vark")
        ]
        mock_app.view_functions = {"aard": "rhubarb"}
        with super_test_context(app):
            self.assertEqual(get_view_function(url_for("main.terms_and_conditions")),
                             ('rhubarb', 'vark'))
        mock_app.url_map.bind.return_value.match.assert_called_with(
            url_for("main.map_help"), method='GET'
        )

    @patch('server.utils.view_function.app')
    def test_get_view_function_noviewassociated(self, mock_app):
        mock_app.url_map.bind.return_value.match.return_value = ("aard", "vark")
        mock_app.view_functions = {"vark": "rhubarb"}
        with super_test_context(app):
            self.assertIsNone(get_view_function(url_for("main.terms_and_conditions"), "POST"))
        mock_app.url_map.bind.return_value.match.assert_called_with(
            url_for("main.terms_and_conditions"), method='POST'
        )
