import json
from flask import url_for, redirect, session
from unittest.mock import ANY, MagicMock, patch
from server.main import app
from unittest import TestCase
from server.models.charges import LocalLandChargeItem
from server.models.searches import SearchState
from server.views.search import get_charge_items, property_address_selected, search_by_area, street_address_selected
from unit_tests.utilities_tests import super_test_context
from landregistry.exceptions import ApplicationError


class TestSearch(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch('server.views.search.SearchByText')
    @patch('server.views.search.start_new_search')
    @patch('server.views.search.SearchPostcodeAddressForm')
    def test_search_by_post_code_address_post_results(self, mock_form, mock_start, mock_by_text):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.search_term.data = "ansearchterm"
        mock_by_text.return_value.process.return_value = {
            "data": [{"address_type": "property"}],
            "status": "success"
        }

        result = self.client.post(url_for('search.search_by_post_code_address'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.address_search_results'))
        mock_by_text.return_value.process.assert_called_with('ansearchterm', ANY)
        mock_start.assert_called()
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['address_search_results'], [{'address_type': 'property'}])
            self.assertEqual(sess['address_search_term'], "ansearchterm")

    @patch('server.views.search.flash')
    @patch('server.views.search.SearchByText')
    @patch('server.views.search.start_new_search')
    @patch('server.views.search.SearchPostcodeAddressForm')
    @patch('server.views.search.SearchLocalLandChargeService')
    def test_search_by_post_code_address_post_no_results(self, mock_sllc, mock_form, mock_start,
                                                         mock_by_text, mock_flash):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.search_term.data = "ansearchterm"
        mock_form.return_value.search_term.errors = []
        mock_by_text.return_value.process.return_value = {
            "data": [],
            "status": "success"
        }
        mock_sllc.return_value.get_service_messages.return_value = ["Some", "Messages"]
        result = self.client.post(url_for('search.search_by_post_code_address'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Identify a search area", result.text)
        mock_by_text.return_value.process.assert_called_with('ansearchterm', ANY)
        mock_start.assert_called()
        mock_flash.assert_called_with(["Some", "Messages"], "service_message")
        self.assertEqual(mock_form.return_value.search_term.errors, ['No results found'])

    def test_address_search_results_no_state(self):
        result = self.client.get(url_for('search.address_search_results'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    def test_address_search_results_no_results(self):
        with self.client.session_transaction() as sess:
            sess['search_state'] = "aardvark"
        result = self.client.get(url_for('search.address_search_results'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.search_by_post_code_address'))

    @patch('server.views.search.calculate_pagination_info')
    def test_address_search_results_good(self, mock_paginate):
        with self.client.session_transaction() as sess:
            sess['search_state'] = "aardvark"
            sess['address_search_results'] = ["some", "addresses"]
            sess['address_search_term'] = "ansearchterm"
        mock_paginate.return_value = [], {}, 0
        result = self.client.get(url_for('search.address_search_results'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Search results for ‘ansearchterm’", result.text)

    def test_address_details_no_state(self):
        result = self.client.get(url_for('search.address_details'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    def test_address_details_no_results(self):
        with self.client.session_transaction() as sess:
            sess['search_state'] = "aardvark"
        result = self.client.get(url_for('search.address_details'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.search_by_post_code_address'))

    @patch('server.views.search.property_address_selected')
    def test_address_details_property(self, mock_prop_selected):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['address_search_results'] = [{"address": "anaddress", "address_type": "property"}]
            sess['unmerged_extent'] = "anextent"
            sess['search_state'].search_extent = "anextent"
        mock_prop_selected.return_value = redirect("anurl")
        result = self.client.get(url_for('search.address_details'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")
        mock_prop_selected.assert_called_with({'address': 'anaddress', 'address_type': 'property'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['search_state'].address, "anaddress")
            self.assertNotIn("unmerged_extent", sess)
            self.assertIsNone(sess['search_state'].search_extent)

    @patch('server.views.search.street_address_selected')
    def test_address_details_street(self, mock_street_selected):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['address_search_results'] = [{"address": "anaddress", "address_type": "street"}]
            sess['unmerged_extent'] = "anextent"
            sess['search_state'].search_extent = "anextent"
        mock_street_selected.return_value = redirect("anurl")
        result = self.client.get(url_for('search.address_details'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")
        mock_street_selected.assert_called_with({'address': 'anaddress', 'address_type': 'street'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['search_state'].address, "anaddress")
            self.assertNotIn("unmerged_extent", sess)
            self.assertIsNone(sess['search_state'].search_extent)

    @patch('server.views.search.merge_polygons')
    @patch('server.views.search.SearchByUprn')
    @patch('server.views.search.CheckMigrationStatus')
    def test_property_address_selected_mig_fail(self, mock_check, mock_by_uprn, mock_merge):
        mock_by_uprn.return_value.process.return_value = {
            "data": [{
                "index_map": {
                    "features": [
                        "some", "features"
                    ]
                }
            }]
        }
        mock_merge.return_value = {"some": "geojson"}
        mock_check.process.return_value = None
        with self.assertRaises(ApplicationError) as exc:
            property_address_selected({"uprn": 1234567})
        self.assertEqual(exc.exception.message, "Failed to check authority intersection migration status")
        mock_by_uprn.return_value.process.assert_called_with("1234567", ANY, True)
        mock_merge.assert_called_with({'type': 'FeatureCollection', 'features': ['some', 'features']})
        mock_check.process.assert_called_with({'some': 'geojson'})

    @patch('server.views.search.merge_polygons')
    @patch('server.views.search.SearchByUprn')
    @patch('server.views.search.CheckMigrationStatus')
    @patch('server.views.search.redirect')
    def test_property_address_selected_not_migrated(self, mock_redirect, mock_check, mock_by_uprn, mock_merge):
        with super_test_context(app):
            mock_by_uprn.return_value.process.return_value = {
                "data": [{
                    "index_map": {
                        "features": [
                            "some", "features"
                        ]
                    }
                }]
            }
            mock_merge.return_value = {"some": "geojson"}
            mock_check.process.return_value = {"flag": "something", "includes_migrated": True}
            mock_redirect.return_value = "aardvark"
            result = property_address_selected({"uprn": 1234567, "geometry": {"coordinates": "somecoordinates"}})
            mock_by_uprn.return_value.process.assert_called_with("1234567", ANY, True)
            mock_merge.assert_called_with({'type': 'FeatureCollection', 'features': ['some', 'features']})
            mock_check.process.assert_called_with({'some': 'geojson'})
            self.assertEqual(session['zoom_to_location'], ['somecoordinates'])
            self.assertEqual(result, "aardvark")
            mock_redirect.assert_called_with(url_for('search.define_search_area', page_style="draw"))

    @patch('server.views.search.merge_polygons')
    @patch('server.views.search.SearchByUprn')
    @patch('server.views.search.CheckMigrationStatus')
    @patch('server.views.search.redirect')
    def test_property_address_selected_all_good(self, mock_redirect, mock_check, mock_by_uprn, mock_merge):
        with super_test_context(app):
            mock_by_uprn.return_value.process.return_value = {
                "data": [{
                    "index_map": {
                        "features": [
                            "some", "features"
                        ]
                    }
                }]
            }
            mock_merge.return_value = {"some": "geojson"}
            mock_check.process.return_value = {"flag": "pass", "includes_migrated": True}
            mock_redirect.return_value = "aardvark"
            session['search_state'] = SearchState()
            result = property_address_selected({"uprn": 1234567, "geometry": {"coordinates": "somecoordinates"}})
            mock_by_uprn.return_value.process.assert_called_with("1234567", ANY, True)
            mock_merge.assert_called_with({'type': 'FeatureCollection', 'features': ['some', 'features']})
            mock_check.process.assert_called_with({'some': 'geojson'})
            self.assertEqual(session['unmerged_extent'],
                             {'type': 'FeatureCollection', 'features': ['some', 'features']})
            self.assertEqual(session['search_state'].search_extent, {'some': 'geojson'})
            self.assertEqual(result, "aardvark")
            mock_redirect.assert_called_with(url_for('search.confirm_search_area'))

    @patch('server.views.search.SearchByUsrn')
    @patch('server.views.search.redirect')
    def test_street_address_selected_good(self, mock_redirect, mock_by_usrn):
        with super_test_context(app):
            mock_by_usrn.return_value.process.return_value = {
                "data": [{"address_type": "street"}],
                "status": "success"
            }
            mock_redirect.return_value = "anredirect"
            result = street_address_selected({
                "usrn": "anusrn",
                "postcode": "anpostcode",
                "geometry": {"coordinates": "somecoordinates"},
                "address": "anaddress"
            })
            self.assertEqual(session['zoom_to_location'], "somecoordinates")
            self.assertEqual(session['address_search_results'], [{'address_type': 'street'}])
            self.assertEqual(session['address_search_term'], "anaddress")
            self.assertEqual(result, "anredirect")
            mock_redirect.assert_called_with(url_for('search.address_search_results'))

    @patch('server.views.search.redirect')
    def test_street_address_selected_not_usrn(self, mock_redirect):
        with super_test_context(app):
            mock_redirect.return_value = "anredirect"
            result = street_address_selected({
                "postcode": "anpostcode",
                "geometry": {"coordinates": "somecoordinates"},
                "address": "anaddress"
            })
            self.assertEqual(session['zoom_to_location'], "somecoordinates")
            self.assertEqual(result, "anredirect")
            mock_redirect.assert_called_with(url_for('search.define_search_area', page_style="draw"))

    @patch('server.views.search.SearchByCoordinatesForm')
    def test_search_by_coordinates_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        result = self.client.get(url_for('search.search_by_coordinates'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Search by coordinates", result.text)

    @patch('server.views.search.SearchByCoordinatesForm')
    def test_search_by_coordinates_post(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.eastings.data = "123456"
        mock_form.return_value.northings.data = "78910"
        result = self.client.post(url_for('search.search_by_coordinates'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.define_search_area', page_style="draw"))

    @patch('server.views.search.SearchByTitleNumberForm')
    def test_search_by_title_number_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        result = self.client.get(url_for('search.search_by_title_number'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Search by coordinates", result.text)

    @patch('server.views.search.SearchByTitleNumberForm')
    @patch('server.views.search.AddressesService')
    @patch('server.views.search.merge_polygons')
    def test_search_by_title_number_post_ok(self, mock_merge, mock_addresses, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.title_number.data = "antitlenumber"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"some": "geometry"}
        mock_addresses.return_value.get_by.return_value = mock_response
        mock_merge.return_value = {"some": "mergedgeometry"}
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
        result = self.client.get(url_for('search.search_by_title_number'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.confirm_search_area'))
        mock_addresses.return_value.get_by.assert_called_with('title', 'antitlenumber')
        mock_merge.assert_called_with({'some': 'geometry'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['unmerged_extent'], {'some': 'geometry'})
            self.assertEqual(sess['search_state'].search_extent, {'some': 'mergedgeometry'})

    @patch('server.views.search.SearchByTitleNumberForm')
    @patch('server.views.search.AddressesService')
    def test_search_by_title_number_post_notfound(self, mock_addresses, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.title_number.data = "antitlenumber"
        mock_form.return_value.title_number.errors = []
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_addresses.return_value.get_by.return_value = mock_response
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
        result = self.client.get(url_for('search.search_by_title_number'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Search by coordinates", result.text)
        mock_addresses.return_value.get_by.assert_called_with('title', 'antitlenumber')
        self.assertEqual(mock_form.return_value.title_number.errors,
                         ['We do not recognise that title number. Check title number and try again'])

    @patch('server.views.search.SearchByTitleNumberForm')
    @patch('server.views.search.AddressesService')
    def test_search_by_title_number_post_fail(self, mock_addresses, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.title_number.data = "antitlenumber"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_addresses.return_value.get_by.return_value = mock_response
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
        result = self.client.get(url_for('search.search_by_title_number'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_addresses.return_value.get_by.assert_called_with('title', 'antitlenumber')

    @patch('server.views.search.SearchByInspireIDForm')
    def test_search_by_inspire_id_get(self, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        result = self.client.get(url_for('search.search_by_inspire_id'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Search by INSPIRE ID", result.text)

    @patch('server.views.search.SearchByInspireIDForm')
    @patch('server.views.search.SearchByInspireId')
    @patch('server.views.search.start_new_search')
    @patch('server.views.search.SearchByChargeId')
    def test_search_by_inspire_id_post_ok(self, mock_charge_id, mock_new_search, mock_inspire, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.inspire_id.data = "aninspireid"
        mock_inspire.return_value.process.return_value = {
            "status": 200,
            "data": {
                "llc_id": "1234"
            }
        }
        mock_charge_id.return_value.process.return_value = {
            "status": "success",
            "data": ["some", "charges"],
            "search_message": "Something something dark side, something something complete"
        }
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
        result = self.client.post(url_for('search.search_by_inspire_id'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.inspire_search_results'))
        mock_inspire.return_value.process.assert_called_with('aninspireid')
        mock_charge_id.return_value.process.assert_called_with('1234', ANY)
        mock_new_search.assert_called()
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['search_state'].charges, ["some", "charges"])

    @patch('server.views.search.SearchByInspireIDForm')
    @patch('server.views.search.SearchByInspireId')
    @patch('server.views.search.start_new_search')
    @patch('server.views.search.SearchByChargeId')
    def test_search_by_inspire_id_post_charge_fail(self, mock_charge_id, mock_new_search, mock_inspire, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.inspire_id.data = "aninspireid"
        mock_form.return_value.inspire_id.errors = []
        mock_inspire.return_value.process.return_value = {
            "status": 200,
            "data": {
                "llc_id": "1234"
            }
        }
        mock_charge_id.return_value.process.return_value = {
            "status": "fail",
            "data": ["some", "charges"],
            "search_message": "Something something dark side, something something complete"
        }
        result = self.client.post(url_for('search.search_by_inspire_id'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Search by INSPIRE ID", result.text)
        mock_inspire.return_value.process.assert_called_with('aninspireid')
        mock_charge_id.return_value.process.assert_called_with('1234', ANY)
        mock_new_search.assert_called()
        self.assertEqual(mock_form.return_value.inspire_id.errors,
                         ['Something something dark side, something something complete'])

    @patch('server.views.search.SearchByInspireIDForm')
    @patch('server.views.search.SearchByInspireId')
    @patch('server.views.search.start_new_search')
    def test_search_by_inspire_id_post_inspire_404(self, mock_new_search, mock_inspire, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.inspire_id.data = "aninspireid"
        mock_form.return_value.inspire_id.errors = []
        mock_inspire.return_value.process.return_value = {
            "status": 404,
            "data": {
                "llc_id": "1234"
            }
        }
        result = self.client.post(url_for('search.search_by_inspire_id'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Error: Search by INSPIRE ID", result.text)
        mock_inspire.return_value.process.assert_called_with('aninspireid')
        mock_new_search.assert_called()
        self.assertEqual(mock_form.return_value.inspire_id.errors,
                         ['You have entered an invalid INSPIRE ID'])

    @patch('server.views.search.SearchByInspireIDForm')
    @patch('server.views.search.SearchByInspireId')
    @patch('server.views.search.start_new_search')
    def test_search_by_inspire_id_post_inspire_500(self, mock_new_search, mock_inspire, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.inspire_id.data = "aninspireid"
        mock_inspire.return_value.process.return_value = {
            "status": 500
        }
        result = self.client.post(url_for('search.search_by_inspire_id'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_inspire.return_value.process.assert_called_with('aninspireid')
        mock_new_search.assert_called()

    def test_inspire_search_results_no_state(self):
        result = self.client.get(url_for('search.inspire_search_results'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    @patch("server.views.search.LocalLandChargeItem")
    def test_inspire_search_results_good(self, mock_llc):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].charges = [{
                "geometry": {"some": "geometry"},
                "item": "anchargeitem"
            }]
        mock_llc_item = LocalLandChargeItem()
        mock_llc_item.charge_type = "Aardvark"
        mock_llc.from_json.return_value = mock_llc_item
        result = self.client.get(url_for('search.inspire_search_results'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Aardvark", result.text)
        self.assertIn("Search result", result.text)

    def test_confirm_search_area_no_state(self):
        result = self.client.get(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    @patch("server.views.search.CheckMigrationStatus")
    def test_confirm_search_area_check_fail(self, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
        mock_check.process.return_value = None
        result = self.client.get(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 500)
        self.assertIn("Sorry, we are experiencing technical difficulties", result.text)
        mock_check.process.assert_called_with({"some": "extent"})

    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.ConfirmSearchAreaForm")
    def test_confirm_search_area_check_pass_post(self, mock_form, mock_by_area, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
            sess['search_state'].address = "anaddress"
        mock_check.process.return_value = {"flag": "pass"}
        mock_form.return_value.validate_on_submit.return_value = True
        mock_by_area.return_value = redirect("anredirect")
        result = self.client.post(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anredirect")
        mock_check.process.assert_called_with({"some": "extent"})
        mock_by_area.assert_called_with({'some': 'extent'}, "anaddress")

    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.ConfirmSearchAreaForm")
    def test_confirm_search_area_check_warning_post(self, mock_form, mock_by_area, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
            sess['search_state'].address = "anaddress"
        mock_check.process.return_value = {"flag": "warning"}
        mock_form.return_value.validate_on_submit.return_value = True
        mock_by_area.return_value = redirect("anredirect")
        result = self.client.post(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anredirect")
        mock_check.process.assert_called_with({"some": "extent"})
        mock_by_area.assert_called_with({'some': 'extent'}, "anaddress", warning=True)

    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.ConfirmSearchAreaForm")
    def test_confirm_search_area_check_bad_post(self, mock_form, mock_by_area, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
            sess['search_state'].address = "anaddress"
        mock_check.process.return_value = {"flag": "badstuff"}
        mock_form.return_value.validate_on_submit.return_value = True
        result = self.client.post(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.no_information_available'))
        mock_check.process.assert_called_with({"some": "extent"})
        mock_by_area.assert_not_called()
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['authority_data'], {"flag": "badstuff"})

    @patch("server.views.search.CheckMigrationStatus")
    def test_confirm_search_area_check_pass_get(self, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
        mock_check.process.return_value = {"flag": "pass"}
        result = self.client.get(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Confirm search area", result.text)
        mock_check.process.assert_called_with({"some": "extent"})

    @patch("server.views.search.CheckMigrationStatus")
    def test_confirm_search_area_check_warning_get(self, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
        mock_check.process.return_value = {"flag": "warning"}
        result = self.client.get(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 200)
        self.assertIn("This search area is near a local authority’s boundary", result.text)
        mock_check.process.assert_called_with({"some": "extent"})

    @patch("server.views.search.CheckMigrationStatus")
    def test_confirm_search_area_check_bad_get(self, mock_check):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"some": "extent"}
        mock_check.process.return_value = {"flag": "bad"}
        result = self.client.get(url_for('search.confirm_search_area'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, (url_for('search.no_information_available')))
        mock_check.process.assert_called_with({"some": "extent"})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['authority_data'], {"flag": "bad"})

    @patch("server.views.search.redirect")
    @patch("server.views.search.SearchByArea")
    @patch("server.views.search.get_charge_items")
    @patch("server.views.search.AuditAPIService")
    @patch("server.views.search.LocalAuthorityAPIService")
    @patch("server.views.search.ReportAPIService")
    @patch("server.views.search.SearchLocalLandChargeService")
    def test_search_by_area_200_with_charges(self, mock_sllc, mock_report, mock_local_auth, mock_audit, mock_get_items,
                                             mock_by_area, mock_redirect):
        with super_test_context(app):
            session["profile"] = {"user_id": "mock_user"}
            mock_by_area.return_value.process.return_value = {
                "status": 200,
                "data": [{"an": "charge"}]
            }
            mock_get_items.return_value = [{"local-land-charge": "1234"}]
            mock_local_auth.get_authorities_by_extent.return_value = {"anauthority": True}
            mock_sllc.return_value.save_free_search.return_value = {"id": "anid"}
            mock_redirect.return_value = "anredirect"
            result = search_by_area({
                "features": [
                    {
                        "geometry": {
                            "an": "geometry"
                        }
                    }
                ]
            }, "anaddress", True)
            mock_by_area.return_value.process.assert_called_with({'features': [{'geometry': {'an': 'geometry'}}]},
                                                                 results_filter='cancelled')
            mock_get_items.assert_called_with([{'an': 'charge'}])
            mock_local_auth.get_authorities_by_extent.assert_called_with({'type': 'GeometryCollection',
                                                                          'geometries': [{'an': 'geometry'}]})
            mock_redirect.assert_called_with(url_for('search_results.results'))
            self.assertEqual(result, "anredirect")
            self.assertEqual(session['search_state'].charges, [{'local-land-charge': '1234'}])
            self.assertEqual(session['search_state'].search_extent, {'features': [{'geometry': {'an': 'geometry'}}]})
            self.assertEqual(session['search_state'].address, "anaddress")
            self.assertTrue(session['warning'])
            self.assertEqual(session['search_state'].free_search_id, "anid")

    @patch("server.views.search.redirect")
    @patch("server.views.search.SearchByArea")
    @patch("server.views.search.AuditAPIService")
    @patch("server.views.search.LocalAuthorityAPIService")
    @patch("server.views.search.ReportAPIService")
    @patch("server.views.search.SearchLocalLandChargeService")
    def test_search_by_area_404(self, mock_sllc, mock_report, mock_local_auth, mock_audit,
                                mock_by_area, mock_redirect):
        with super_test_context(app):
            session["profile"] = {"user_id": "mock_user"}
            session["search_state"] = None
            mock_by_area.return_value.process.return_value = {
                "status": 404
            }
            mock_local_auth.get_authorities_by_extent.return_value = {"anauthority": True}
            mock_sllc.return_value.save_free_search.return_value = {"id": "anid"}
            mock_redirect.return_value = "anredirect"
            result = search_by_area({
                "features": [
                    {
                        "geometry": {
                            "an": "geometry"
                        }
                    }
                ]
            }, "anaddress", True)
            mock_by_area.return_value.process.assert_called_with({'features': [{'geometry': {'an': 'geometry'}}]},
                                                                 results_filter='cancelled')
            mock_local_auth.get_authorities_by_extent.assert_called_with({'type': 'GeometryCollection',
                                                                          'geometries': [{'an': 'geometry'}]})
            mock_redirect.assert_called_with(url_for('search_results.results'))
            self.assertEqual(result, "anredirect")
            self.assertEqual(session['search_state'].charges, None)
            self.assertEqual(session['search_state'].search_extent, {'features': [{'geometry': {'an': 'geometry'}}]})
            self.assertEqual(session['search_state'].address, "anaddress")
            self.assertTrue(session['warning'])
            self.assertEqual(session['search_state'].free_search_id, "anid")

    @patch("server.views.search.CheckMaintenanceStatus")
    @patch("server.views.search.render_template")
    @patch("server.views.search.SearchByArea")
    @patch("server.views.search.SearchLocalLandChargeService")
    def test_search_by_area_507(self, mock_sllc, mock_by_area, mock_render, mock_check):
        with super_test_context(app):
            session["profile"] = {"user_id": "mock_user"}
            session["search_state"] = None
            session["unmerged_extent"] = {"unmerged": "extent"}
            mock_by_area.return_value.process.return_value = {
                "status": 507
            }
            mock_sllc.return_value.save_free_search.return_value = {"id": "anid"}
            mock_render.return_value = "anrender"
            mock_check.under_maintenance.return_value = True
            result = search_by_area({
                "features": [
                    {
                        "geometry": {
                            "an": "geometry"
                        }
                    }
                ]
            }, "anaddress", True)
            mock_by_area.return_value.process.assert_called_with({'features': [{'geometry': {'an': 'geometry'}}]},
                                                                 results_filter='cancelled')
            mock_render.assert_called_with('define-search-area.html',
                                           style='edit', form=ANY, too_many_results=True,
                                           information='{"unmerged": "extent"}',
                                           zoom_extent='{"features": [{"geometry": {"an": "geometry"}}]}',
                                           maintenance=True)
            self.assertEqual(result, "anrender")
            self.assertEqual(session['search_state'].charges, None)
            self.assertEqual(session['search_state'].search_extent, {'features': [{'geometry': {'an': 'geometry'}}]})
            self.assertEqual(session['search_state'].address, "anaddress")

    @patch("server.views.search.CheckMaintenanceStatus")
    @patch("server.views.search.render_template")
    @patch("server.views.search.SearchByArea")
    @patch("server.views.search.SearchLocalLandChargeService")
    def test_search_by_area_bad(self, mock_sllc, mock_by_area, mock_render, mock_check):
        with super_test_context(app):
            session["profile"] = {"user_id": "mock_user"}
            session["search_state"] = None
            session["unmerged_extent"] = {"unmerged": "extent"}
            mock_by_area.return_value.process.return_value = {
                "status": 666
            }
            mock_sllc.return_value.save_free_search.return_value = {"id": "anid"}
            mock_render.return_value = "anrender"
            mock_check.under_maintenance.return_value = True
            with self.assertRaises(ApplicationError):
                search_by_area({
                    "features": [
                        {
                            "geometry": {
                                "an": "geometry"
                            }
                        }
                    ]
                }, "anaddress", True)
            mock_by_area.return_value.process.assert_called_with({'features': [{'geometry': {'an': 'geometry'}}]},
                                                                 results_filter='cancelled')
            self.assertEqual(session['search_state'].charges, None)

    def test_get_charge_items(self):
        result = get_charge_items([{"item": {"local-land-charge": "1234"}, "adjoining": True}])
        self.assertEqual(result, [{"local-land-charge": "1234", "adjoining": True}])

    def test_no_information_available_no_state(self):
        result = self.client.get(url_for('search.no_information_available'))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    @patch("server.views.search.render_template")
    def test_no_information_available_fail_maintenance(self, mock_render):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['authority_data'] = {
                'flag': 'fail_maintenance',
                'plus_buffer': {
                    'maintenance_list': [
                        'some', 'authorities'
                    ]
                },
                'migrated_list': []
            }
        result = self.client.get(url_for('search.no_information_available'))
        self.assertEqual(result.status_code, 200)
        mock_render.assert_called_with('no-information-available.html',
                                       show_amend_search=False,
                                       authorities=['authorities', 'some'],
                                       scotland=False,
                                       maintenance=True,
                                       maintenance_contact=False,
                                       no_authority=False)

    @patch("server.views.search.render_template")
    def test_no_information_available_fail_scotland(self, mock_render):
        with self.client.session_transaction() as sess:
            sess['search_state'] = SearchState()
            sess['authority_data'] = {
                'flag': 'fail_scotland',
                'plus_buffer': {
                    'non_migrated_list': [
                        'some', 'authorities'
                    ]
                },
                'migrated_list': []
            }
        result = self.client.get(url_for('search.no_information_available'))
        self.assertEqual(result.status_code, 200)
        mock_render.assert_called_with('no-information-available.html',
                                       show_amend_search=False,
                                       authorities=['Scotland', 'authorities', 'some'],
                                       scotland=True,
                                       maintenance=False,
                                       maintenance_contact=False,
                                       no_authority=False)

    def test_define_search_area_no_state(self):
        result = self.client.get(url_for('search.define_search_area', page_style="find"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('index.index_page'))

    @patch("server.views.search.CheckMaintenanceStatus")
    @patch("server.views.search.render_template")
    @patch("server.views.search.DefineSearchAreaForm")
    def test_define_search_area_get_ok(self, mock_form, mock_render, mock_check):
        mock_form.return_value.validate_on_submit.return_value = False
        with self.client.session_transaction() as sess:
            sess['unmerged_extent'] = {"anunmerged": "extent"}
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"an": "extent"}
            sess['zoom_to_location'] = {"an": "location"}
            sess['zoom_to_authority'] = "anauthority"

        result = self.client.get(url_for('search.define_search_area', page_style="find"))
        self.assertEqual(result.status_code, 200)
        mock_render.assert_called_with('define-search-area.html', form=mock_form.return_value, style='find',
                                       information='{"anunmerged": "extent"}', coordinate_search=None,
                                       zoom_extent='{"an": "extent"}',
                                       local_authority_boundary_url=url_for('ajax.local_authority_service_boundingbox',
                                                                            authority="anauthority"),
                                       zoom_to_location='{"an": "location"}',
                                       maintenance=mock_check.under_maintenance.return_value)

    @patch("server.views.search.merge_polygons")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.DefineSearchAreaForm")
    def test_define_search_area_post_pass(self, mock_form, mock_migration, mock_by_area,
                                          mock_merge):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.saved_features.data = json.dumps({"saved": "features"})
        with self.client.session_transaction() as sess:
            sess['unmerged_extent'] = {"anunmerged": "extent"}
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"an": "extent"}
            sess['search_state'].address = "anaddress"
            sess['zoom_to_location'] = {"an": "location"}
        mock_migration.process.return_value = {
            'flag': 'pass'
        }
        mock_by_area.return_value = redirect("anurl")
        mock_merge.return_value = {"anmerged": "extent"}
        result = self.client.post(url_for('search.define_search_area', page_style="find"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")
        mock_by_area.assert_called_with({'anmerged': 'extent'}, 'anaddress')

    @patch("server.views.search.merge_polygons")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.DefineSearchAreaForm")
    def test_define_search_area_post_warning(self, mock_form, mock_migration, mock_by_area,
                                             mock_merge):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.saved_features.data = json.dumps({"saved": "features"})
        with self.client.session_transaction() as sess:
            sess['unmerged_extent'] = {"anunmerged": "extent"}
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"an": "extent"}
            sess['search_state'].address = "anaddress"
            sess['zoom_to_location'] = {"an": "location"}
        mock_migration.process.return_value = {
            'flag': 'warning'
        }
        mock_by_area.return_value = redirect("anurl")
        mock_merge.return_value = {"anmerged": "extent"}
        result = self.client.post(url_for('search.define_search_area', page_style="find"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, "anurl")
        mock_by_area.assert_called_with({'anmerged': 'extent'}, 'anaddress', warning=True)

    @patch("server.views.search.merge_polygons")
    @patch("server.views.search.search_by_area")
    @patch("server.views.search.CheckMigrationStatus")
    @patch("server.views.search.DefineSearchAreaForm")
    def test_define_search_area_post_bad(self, mock_form, mock_migration, mock_by_area,
                                         mock_merge):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.saved_features.data = json.dumps({"saved": "features"})
        with self.client.session_transaction() as sess:
            sess['unmerged_extent'] = {"anunmerged": "extent"}
            sess['search_state'] = SearchState()
            sess['search_state'].search_extent = {"an": "extent"}
            sess['search_state'].address = "anaddress"
            sess['zoom_to_location'] = {"an": "location"}
        mock_migration.process.return_value = {
            'flag': 'badness'
        }
        mock_by_area.return_value = redirect("anurl")
        mock_merge.return_value = {"anmerged": "extent"}
        result = self.client.post(url_for('search.define_search_area', page_style="find"))
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, url_for('search.no_information_available'))
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['authority_data'], {'flag': 'badness'})
