from unittest import TestCase
from server.views.forms.search_by_coordinates_form import SearchByCoordinatesForm


class TestSearchByCoordinatesForm(TestCase):
    def test_search_by_coordinates_form_invalid(self):
        form = SearchByCoordinatesForm()
        form.eastings.data = "notanumber"
        form.eastings.raw_data = "notanumber"
        form.northings.data = "1232132132132132132132131232132131"
        form.northings.raw_data = "1232132132132132132132131232132131"
        self.assertFalse(form.validate())
        self.assertEqual(
            form.errors, {'eastings': ['Enter coordinates in the correct format'],
                          'northings': ['Enter coordinates in the correct format']}
        )

    def test_search_by_coordinates_form_valid(self):
        form = SearchByCoordinatesForm()
        form.eastings.data = "5678"
        form.eastings.raw_data = "5678"
        form.northings.data = "12345"
        form.northings.raw_data = "12345"
        self.assertTrue(form.validate())
