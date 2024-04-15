from unittest import TestCase

from flask import session, url_for

from server.main import app
from server.services import back_link_history
from unit_tests.utilities_tests import super_test_context


class TestBackLinkHistory(TestCase):
    def test_add_history_slice(self):
        with super_test_context(app):
            session["history"] = ["alink", "backtracklink", "anotherlink"]
            back_link_history.add_history("backtracklink")
            self.assertEqual(session["history"], ["alink", "backtracklink"])

    def test_add_history_add(self):
        with super_test_context(app):
            session["history"] = ["alink", "anotherlink"]
            back_link_history.add_history("yetanotherlink")
            self.assertEqual(session["history"], ["alink", "anotherlink", "yetanotherlink"])

    def test_add_history_create(self):
        with super_test_context(app):
            session["history"] = []
            back_link_history.add_history("alink")
            self.assertEqual(session["history"], ["alink"])

    def test_add_history_backlink(self):
        with super_test_context(app):
            session["history"] = []
            session["back_link"] = True
            back_link_history.add_history("alink")
            self.assertEqual(session["back_link"], False)

    def test_get_back_url_history(self):
        with super_test_context(app):
            session["history"] = ["alink"]
            result = back_link_history.get_back_url()
            self.assertEqual(result, "alink")
            self.assertEqual(session["history"], [])

    def test_get_back_url_no_history(self):
        with super_test_context(app):
            session["history"] = []
            result = back_link_history.get_back_url()
            self.assertEqual(result, url_for("index.index_page"))
            self.assertEqual(session["history"], [])

    def test_reset_history(self):
        with super_test_context(app):
            session["history"] = ["aardvark"]
            back_link_history.reset_history()
            self.assertEqual(session["history"], [url_for("index.index_page")])
