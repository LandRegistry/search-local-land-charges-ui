import unittest
from unittest.mock import patch

from flask import session

from server.main import app
from server.utils.repeat_searches import (
    has_free_searches_to_repeat,
    has_paid_searches_to_repeat,
)
from unit_tests.utilities_tests import super_test_context


class TestRepeatSearches(unittest.TestCase):

    @patch("server.utils.repeat_searches.SearchLocalLandChargeService")
    def test_show_searches_to_repeat_false(self, mock_sllc):
        with super_test_context(app):
            session["profile"] = {"user_id": "auserid"}
            mock_sllc.return_value.get_free_search_items_to_repeat.return_value = {
                "items": [],
                "total": 0,
            }
            mock_sllc.return_value.get_paid_search_items_to_repeat.return_value = {
                "items": [],
                "total": 0,
            }
            result1 = has_paid_searches_to_repeat()
            result2 = has_free_searches_to_repeat()
            self.assertFalse(result1)
            self.assertFalse(result2)

    @patch("server.utils.repeat_searches.SearchLocalLandChargeService")
    def test_show_searches_to_repeat_some_free(self, mock_sllc):
        with super_test_context(app):
            session["profile"] = {"user_id": "auserid"}
            mock_sllc.return_value.get_free_search_items_to_repeat.return_value = {
                "items": ["some", "things"],
                "total": 2,
            }
            mock_sllc.return_value.get_paid_search_items_to_repeat.return_value = {
                "items": [],
                "total": 0,
            }
            result1 = has_paid_searches_to_repeat()
            result2 = has_free_searches_to_repeat()
            self.assertTrue(result2)
            self.assertFalse(result1)

    @patch("server.utils.repeat_searches.SearchLocalLandChargeService")
    def test_show_searches_to_repeat_some_paid(self, mock_sllc):
        with super_test_context(app):
            session["profile"] = {"user_id": "auserid"}
            mock_sllc.return_value.get_free_search_items_to_repeat.return_value = {
                "items": [],
                "total": 0,
            }
            mock_sllc.return_value.get_paid_search_items_to_repeat.return_value = {
                "items": ["some", "things"],
                "total": 2,
            }
            result1 = has_paid_searches_to_repeat()
            result2 = has_free_searches_to_repeat()
            self.assertTrue(result1)
            self.assertFalse(result2)

    @patch("server.utils.repeat_searches.SearchLocalLandChargeService")
    def test_show_searches_to_repeat_some_paid_and_free(self, mock_sllc):
        with super_test_context(app):
            session["profile"] = {"user_id": "auserid"}
            mock_sllc.return_value.get_free_search_items_to_repeat.return_value = {
                "items": ["some", "things"],
                "total": 2,
            }
            mock_sllc.return_value.get_paid_search_items_to_repeat.return_value = {
                "items": ["some", "things"],
                "total": 2,
            }
            result1 = has_paid_searches_to_repeat()
            result2 = has_free_searches_to_repeat()
            self.assertTrue(result1)
            self.assertTrue(result2)
