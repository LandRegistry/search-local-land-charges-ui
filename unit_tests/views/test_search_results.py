from collections import OrderedDict
from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import url_for
from flask_babel import lazy_gettext as _

from server.app import app
from server.models.charges import (
    FinancialItem,
    LandCompensationItem,
    LightObstructionNoticeItem,
    LocalLandChargeItem,
)
from server.models.searches import SearchState
from server.views.search_results import (
    format_for_display,
    group_charges_format_for_display,
    sort_charges,
)
from unit_tests.test_data.mock_land_charge import (
    mock_financial_charge,
    mock_land_charge,
    mock_land_compensation_charge,
)
from unit_tests.test_data.mock_lon import mock_light_obstruction_notice


class TestSearchResults(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()

    def test_results_no_search_state(self):
        with self.client.session_transaction() as session:
            session["profile"] = {"user_id": "anuserid"}
        result = self.client.get(url_for("search_results.results"))
        self.assertEqual(result.location, url_for("index.index_page"))

    @patch("server.views.search_results.SearchResultsForm")
    @patch("server.views.search_results.decode_validate_search_id")
    def test_results_post_invalid_enc_search(self, mock_decode, mock_form):
        with self.client.session_transaction() as session:
            session["profile"] = {"user_id": "anuserid"}
            session["search_state"] = "somestate"
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.enc_search_id.data = "custard"
        mock_decode.return_value = False

        result = self.client.post(url_for("search_results.results"))
        self.assertEqual(result.status_code, 500)
        mock_decode.assert_called_with("custard")
        self.assertIn("Sorry, there is a problem with the service", result.text)

    @patch("server.views.search_results.SearchResultsForm")
    @patch("server.views.search_results.decode_validate_search_id")
    def test_results_post_valid_enc_search(self, mock_decode, mock_form):
        with self.client.session_transaction() as session:
            session["profile"] = {"user_id": "anuserid"}
            session["search_state"] = "somestate"
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.enc_search_id.data = "custard"
        mock_decode.return_value = True

        result = self.client.post(url_for("search_results.results"))
        self.assertEqual(result.status_code, 302)
        mock_decode.assert_called_with("custard")
        self.assertEqual(
            result.location,
            url_for("paid_search.search_area_description", enc_search_id="custard"),
        )

    @patch("server.views.search_results.SearchResultsForm")
    @patch("server.views.search_results.sort_charges")
    @patch("server.views.search_results.calculate_pagination_info")
    @patch("server.views.search_results.Fernet")
    @patch("server.views.search_results.group_charges_format_for_display")
    def test_results_get(self, mock_group, mock_fernet, mock_paginate, mock_sort, mock_form):
        with self.client.session_transaction() as session:
            session["profile"] = {"user_id": "anuserid"}
            test_search_state = SearchState()
            test_search_state.search_extent = "anextent"
            test_search_state.charges = [
                mock_financial_charge(),
                mock_land_charge(),
                mock_land_compensation_charge(),
                mock_light_obstruction_notice(),
            ]
            test_search_state.free_search_id = "anid"
            session["search_state"] = test_search_state
            session["repeated_search"] = True
        mock_form.return_value.validate_on_submit.return_value = False
        mock_form.return_value.enc_search_id.data = "custard"
        mock_form.return_value.errors = []
        mock_sort.return_value = "Somecharges"
        mock_fernet.return_value.encrypt.return_value = b"someencryptedthing"
        mock_paginate.return_value = [], {"items": []}, 0
        mock_group.return_value = {}

        result = self.client.get(url_for("search_results.results"))
        mock_fernet.return_value.encrypt.assert_called_with(b"anid")
        mock_group.assert_called_with([])
        mock_paginate.assert_called_with("Somecharges", "search_results.results", 25, 1)
        mock_sort.assert_called()
        self.assertIn("Local land charge search results", result.text)

    @patch("server.views.search_results.CategoryService")
    def test_charge_sorting(self, mock_cat_service):
        mock_cat_service.return_value.get.return_value = [
            {"display-name": "Planning"},
            {"display-name": "Financial"},
            {"display-name": "Listed building"},
            {"display-name": "Land compensation"},
            {"display-name": "Housing / buildings"},
            {"display-name": "Light obstruction notice"},
            {"display-name": "Other"},
        ]
        listed_building_charge = MagicMock()
        listed_building_charge.charge_type = "Listed building"

        financial_charge = MagicMock()
        financial_charge.charge_type = "Financial"

        planning_charge = MagicMock()
        planning_charge.charge_type = "Planning"

        charges = [listed_building_charge, financial_charge, planning_charge] * 15

        ordered_charges = sort_charges(charges)
        self.assertEqual(ordered_charges[0]["group-type"], "Planning")
        self.assertEqual(ordered_charges[14]["group-type"], "Planning")
        self.assertEqual(ordered_charges[15]["group-type"], "Financial")
        self.assertEqual(ordered_charges[29]["group-type"], "Financial")
        self.assertEqual(ordered_charges[30]["group-type"], "Listed building")
        self.assertEqual(ordered_charges[44]["group-type"], "Listed building")

    @patch("server.views.search_results.CategoryService")
    def test_charge_sorting_no_charges(self, mock_cat_service):
        mock_cat_service.return_value.get.return_value = [
            {"display-name": "Planning"},
            {"display-name": "Financial"},
            {"display-name": "Listed building"},
            {"display-name": "Land compensation"},
            {"display-name": "Housing / buildings"},
            {"display-name": "Light obstruction notice"},
            {"display-name": "Other"},
        ]
        ordered_charges = sort_charges([])
        self.assertEqual(len(ordered_charges), 0)

    @patch("server.views.search_results.format_for_display")
    def test_group_charges_format_for_display(self, mock_format):
        charges = [
            {"group-type": "Aardvark", "charge": "ancharge"},
            {"group-type": "Rhubarb", "charge": "anothercharge"},
            {"group-type": "Rhubarb", "charge": "yetanothercharge"},
        ]
        mock_format.return_value = "formattedcharge"
        result = group_charges_format_for_display(charges)
        self.assertEqual(
            result,
            OrderedDict(
                {
                    "Aardvark": ["formattedcharge"],
                    "Rhubarb": ["formattedcharge", "formattedcharge"],
                }
            ),
        )

    def test_format_for_display_land_charge(self):
        result = format_for_display(LocalLandChargeItem.from_json(mock_land_charge()))
        self.assertEqual(
            result,
            {
                "content": {
                    "Authority reference": "a reference",
                    "HM Land Registry reference": "LLC-3Z",
                    "Law": "a provision",
                    "Legal document": "An instrument",
                    "Location": ["a description"],
                    "Originating authority": "an authority",
                    "Registration date": "01 January 2011",
                },
                "heading": {
                    "creation_date": "01 January 2011",
                    "header": "a charge type",
                    "sub_header": "",
                },
            },
        )

    def test_format_for_display_lon(self):
        result = format_for_display(LightObstructionNoticeItem.from_json(mock_light_obstruction_notice()))
        self.assertEqual(
            result,
            {
                "content": {
                    "Applicant 1 details": [
                        "Human Name",
                        "123 Fake Street",
                        "Test Town",
                        "Up",
                        "12H 2ND",
                        "United Kingdom",
                    ],
                    "Covers all or part of extent": "Over yonder",
                    "Expiry date\n(definitive certificate)": "01 January 2011",
                    "HM Land Registry reference": "LLC-3Z",
                    "Height of servient land development": "28 Metres",
                    "Interest in land": "land interest description",
                    "Law": "a provision",
                    "Legal document": "An instrument",
                    "Location\n(dominant building)": ["a description"],
                    "Start date\n(definitive certificate)": "01 January 2012",
                },
                "heading": {
                    "header": "Light obstruction notice",
                    "registration_date": "01 January 2011",
                    "sub_header": "",
                },
            },
        )

    def test_format_for_display_land_comp(self):
        result = format_for_display(LandCompensationItem.from_json(mock_land_compensation_charge()))
        self.assertEqual(
            result,
            {
                "content": {
                    "Authority reference": "a reference",
                    "HM Land Registry reference": "LLC-3Z",
                    "Land sold": "10",
                    "Law": "a provision",
                    "Legal document": "An instrument",
                    "Location": ["a description"],
                    "Originating authority": "an authority",
                    "Registration date": "01 January 2011",
                    "Work done": "21",
                },
                "heading": {
                    "creation_date": "01 January 2011",
                    "header": "Land compensation",
                    "sub_header": "",
                },
            },
        )

    def test_format_for_display_land_comp_paid(self):
        charge = LandCompensationItem.from_json(mock_land_compensation_charge())
        charge.land_compensation_paid = "1"
        result = format_for_display(charge)
        self.assertEqual(
            result,
            {
                "content": {
                    "Advance payment": "£1.00",
                    "Agreed or estimated": _("Not provided"),
                    "Authority reference": "a reference",
                    "HM Land Registry reference": "LLC-3Z",
                    "Interest in land": _("Not provided"),
                    "Land sold": "10",
                    "Law": "a provision",
                    "Legal document": "An instrument",
                    "Location": ["a description"],
                    "Originating authority": "an authority",
                    "Registration date": "01 January 2011",
                    "Total compensation": _("Not provided"),
                    "Work done": "21",
                },
                "heading": {
                    "creation_date": "01 January 2011",
                    "header": "Land compensation",
                    "sub_header": "",
                },
            },
        )

    def test_format_for_display_financial(self):
        result = format_for_display(FinancialItem.from_json(mock_financial_charge()))
        self.assertEqual(
            result,
            {
                "content": {
                    "Amount": "£12.00",
                    "Authority reference": "a reference",
                    "HM Land Registry reference": "LLC-3Z",
                    "Interest rate": "5&#37;",
                    "Law": "a provision",
                    "Legal document": "An instrument",
                    "Location": ["a description"],
                    "Originating authority": "an authority",
                    "Registration date": "01 January 2011",
                },
                "heading": {
                    "creation_date": "01 January 2011",
                    "header": "Financial",
                    "sub_header": "",
                },
            },
        )
