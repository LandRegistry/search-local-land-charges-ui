from unittest import TestCase

from server.views.forms.search_free_searches_form import SearchFreeSearchesForm


class TestSearchFreeSearchesForm(TestCase):
    def test_search_free_searches_form(self):
        form = SearchFreeSearchesForm()
        form.search_term.data = "notanumber"
        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {"search_term": ["You have entered an invalid Search ID. Check it and try again"]}
        )
