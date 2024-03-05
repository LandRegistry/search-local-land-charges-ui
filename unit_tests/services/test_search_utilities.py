from unittest import TestCase
from unittest.mock import patch

from server.services.search_utilities import (
    calculate_pagination_info,
    decode_validate_search_id,
    get_charge_items,
    start_new_search,
)
from server.main import app
from flask import session, url_for
from unit_tests.utilities import Utilities
from unit_tests.utilities_tests import super_test_context


class TestSearchUtilities(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()

    @patch("server.services.search_utilities.reset_history")
    def test_start_new_search(self, mock_reset):
        session["search_state"] = "a"
        session["payment_state"] = "b"
        session["unmerged_extent"] = "c"
        session["address_search_term"] = "d"
        session["address_search_results"] = "e"
        session["zoom_to_location"] = "f"
        session["coordinate_search"] = "g"
        start_new_search()
        self.assertNotEqual(session["search_state"], "a")
        self.assertNotIn("payment_state", session)
        self.assertNotIn("unmerged_extent", session)
        self.assertNotIn("address_search_term", session)
        self.assertNotIn("address_search_results", session)
        self.assertNotIn("zoom_to_location", session)
        self.assertNotIn("coordinate_search", session)

        mock_reset.assert_called()

    @patch("server.services.search_utilities.SearchLocalLandChargeService")
    def test_decode_validate_search_id_ok(self, mock_sllc_service):
        with super_test_context(app):
            enc_search_id = Utilities.create_enc_search_id(1)
            mock_sllc_service.return_value.get_free_search.return_value = {
                "user-id": "anuserid",
                "address": "anaddress",
                "id": "anid",
                "search-extent": {"an": "extent"},
            }
            session["profile"] = {"user_id": "anuserid"}
            result = decode_validate_search_id(enc_search_id)
            mock_sllc_service.return_value.get_free_search.assert_called_with("1")
            self.assertEqual(
                result.to_json(),
                {
                    "address": "anaddress",
                    "charges": None,
                    "free-search-id": "anid",
                    "parent-search": None,
                    "previously-completed": None,
                    "search-extent": {"an": "extent"},
                    "search-reference": None,
                },
            )

    @patch("server.services.search_utilities.SearchLocalLandChargeService")
    def test_decode_validate_search_id_bad_userid(self, mock_sllc_service):
        with super_test_context(app):
            enc_search_id = Utilities.create_enc_search_id(1)
            mock_sllc_service.return_value.get_free_search.return_value = {
                "user-id": "anuserid",
                "address": "anaddress",
                "id": "anid",
                "search-extent": {"an": "extent"},
            }
            session["profile"] = {"user_id": "anuserid2"}
            result = decode_validate_search_id(enc_search_id)
            mock_sllc_service.return_value.get_free_search.assert_called_with("1")
            self.assertIsNone(result)

    def test_get_charge_items(self):
        mock_results = [{"item": {"some": "result"}, "adjoining": True}, {"item": {"some": "result"}}]

        result = get_charge_items(mock_results)
        self.assertEqual([{"some": "result", "adjoining": True}, {"some": "result", "adjoining": False}], result)

    def test_calculate_pagination_info_no_items(self):
        display_items, pagination_info, start_index = calculate_pagination_info(
            None, "search_results.results", 10, 5, {"some": "arg"}, 10, 100
        )
        self.assertIsNone(display_items)
        self.assertEqual(
            pagination_info,
            {
                "items": [
                    {"href": url_for("search_results.results", some="arg"), "number": 1},
                    {"ellipsis": True},
                    {"href": url_for("search_results.results", page=4, some="arg"), "number": 4},
                    {"current": True, "href": url_for("search_results.results", page=5, some="arg"), "number": 5},
                    {"href": url_for("search_results.results", page=6, some="arg"), "number": 6},
                    {"ellipsis": True},
                    {"href": url_for("search_results.results", page=10, some="arg"), "number": 10},
                ],
                "next": {"href": url_for("search_results.results", page=6, some="arg"), "text": "Next"},
                "previous": {"href": url_for("search_results.results", page=4, some="arg"), "text": "Previous"},
            },
        )
        self.assertEqual(start_index, 40)

    def test_calculate_pagination_info_items(self):
        display_items, pagination_info, start_index = calculate_pagination_info(
            range(100), "search_results.results", 10, 5
        )
        self.assertEqual(display_items, range(50)[40:51])
        self.assertEqual(
            pagination_info,
            {
                "items": [
                    {"href": url_for("search_results.results"), "number": 1},
                    {"ellipsis": True},
                    {"href": url_for("search_results.results", page=4), "number": 4},
                    {"current": True, "href": url_for("search_results.results", page=5), "number": 5},
                    {"href": url_for("search_results.results", page=6), "number": 6},
                    {"ellipsis": True},
                    {"href": url_for("search_results.results", page=10), "number": 10},
                ],
                "next": {"href": url_for("search_results.results", page=6), "text": "Next"},
                "previous": {"href": url_for("search_results.results", page=4), "text": "Previous"},
            },
        )
        self.assertEqual(start_index, 40)


# def calculate_pagination_info(items, paginate_url, items_per_page, current_page, paginate_args=None,
#                               no_of_pages=None, no_of_items=None):
#     if paginate_args is None:
#         paginate_args = {}
#     if no_of_items is None:
#         no_of_items = len(items)
#     if no_of_pages is None:
#         no_of_pages = int(math.ceil(no_of_items / items_per_page))

#     # This works out the index of the first address on this page
#     start_index = items_per_page * (current_page - 1)

#     # This works out the index of the last address on this page
#     end_index = (
#         no_of_items - 1 if current_page == no_of_pages
#         else (items_per_page * current_page) - 1)

#     pagination_info = {'items': []}

#     if current_page > 1:
#         pagination_info['previous'] = {
#             "href": url_for(paginate_url, page=current_page - 1, **paginate_args),
#             "text": _("Previous"),
#         }
#         if current_page > 2:
#             pagination_info['items'].append({
#                 "number": 1,
#                 "href": url_for(paginate_url, **paginate_args)
#             })
#         if current_page > 3:
#             pagination_info['items'].append({
#                 "ellipsis": True
#             })
#         pagination_info['items'].append({
#             "number": current_page - 1,
#             "href": url_for(paginate_url, page=current_page - 1, **paginate_args)
#         })
#     pagination_info['items'].append({
#         "number": current_page,
#         "href": url_for(paginate_url, page=current_page, **paginate_args),
#         "current": True
#     })
#     if current_page < no_of_pages:
#         pagination_info["items"].append({
#             "number": current_page + 1,
#             "href": url_for(paginate_url, page=current_page + 1, **paginate_args)
#         })
#         if current_page < no_of_pages - 2:
#             pagination_info['items'].append({
#                 "ellipsis": True
#             })
#         if current_page < no_of_pages - 1:
#             pagination_info["items"].append({
#                 "number": no_of_pages,
#                 "href": url_for(paginate_url, page=no_of_pages, **paginate_args)
#             })
#         pagination_info['next'] = {
#             "href": url_for(paginate_url, page=current_page + 1, **paginate_args),
#             "text": _('Next'),
#         }

#     display_items = None
#     if items is not None:
#         # slice the items list to only have the content required on the page
#         display_items = items[start_index:end_index + 1]

#     return display_items, pagination_info, start_index
