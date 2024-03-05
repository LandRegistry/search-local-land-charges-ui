from datetime import datetime
from unittest import TestCase
from server import main
from unittest.mock import patch, MagicMock
from flask import g
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service \
    import SearchLocalLandChargeService
from landregistry.exceptions import ApplicationError
from unit_tests.utilities_tests import super_test_context
from server.main import app


class TestSearchLocalLandChargeApiService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.datetime')
    def test_post_free_search_ok(self, mock_datetime):
        with super_test_context(app):
            g.requests.post.return_value.status_code = 201
            g.trace_id = "Help me"

            test_datetime = datetime(1969, 12, 25)
            mock_datetime.now.return_value = test_datetime

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}

            search_llc_service = SearchLocalLandChargeService(config)

            response = search_llc_service.save_free_search("a userid", [1, 2, 3, 4], {"an": "extent"}, "anaddress")

            post_json = {"user-id": "a userid",
                         "charge-ids": [1, 2, 3, 4],
                         "search-extent": {"an": "extent"},
                         "search-date": test_datetime.isoformat(),
                         "address": "anaddress"}

            g.requests.post.assert_called_with(
                "a URL/free-searches",
                json=post_json,
                headers={'Content-Type': 'application/json'}
            )

            self.assertEqual(g.requests.post.return_value.json.return_value, response)

    def test_post_free_search_error(self):
        with super_test_context(app):
            g.requests.post.return_value.status_code = 400
            g.trace_id = "Help me"

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)

            with self.assertRaises(ApplicationError):
                search_llc_service.save_free_search(None, [1, 2, 3, 4], {"an": "extent"}, "anaddress")

    def test_get_service_messages_good(self):
        message_json = {"messages": [{"id": 1, "message-name": "test message",
                                      "message-en": "This is a test",
                                      "message-cy": "This is a test in welsh",
                                      "hyperlink-message-en": "This is a hyperlink",
                                      "hyperlink-message-cy": "This is a hyperlink in welsh",
                                      "hyperlink-link-en": "http://alink.com",
                                      "hyperlink-link-cy": "http://alinkinwelsh.com"},
                                     {"id": 2, "message-name": "downtime",
                                      "message-en": "Going down 10pm - 1am",
                                      "message-cy": "Going down 10pm - 1am in welsh",
                                      "hyperlink-message-en": "This is another hyperlink",
                                      "hyperlink-message-cy": "This is another hyperlink in welsh",
                                      "hyperlink-link-en": "http://anotherlink.com",
                                      "hyperlink-link-cy": "http://anotherlinkinwelsh.com"}]
                        }
        expected_response = [{'link': 'http://alink.com',
                              'link_text': 'This is a hyperlink',
                              'message': 'This is a test'},
                             {'link': 'http://anotherlink.com',
                              'link_text': 'This is another hyperlink',
                              'message': 'Going down 10pm - 1am'}]

        with super_test_context(app):
            g.requests.get.return_value.status_code = 200
            g.requests.get.return_value.json.return_value = message_json
            g.trace_id = "Help me"
            g.locale = "en"

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}

            search_llc_service = SearchLocalLandChargeService(config)

            response = search_llc_service.get_service_messages()

            self.assertEqual(response, expected_response)

    def test_get_service_messages_good_cy(self):
        message_json = {"messages": [{"id": 1, "message-name": "test message",
                                      "message-en": "This is a test",
                                      "message-cy": "This is a test in welsh",
                                      "hyperlink-message-en": "This is a hyperlink",
                                      "hyperlink-message-cy": "This is a hyperlink in welsh",
                                      "hyperlink-link-en": "http://alink.com",
                                      "hyperlink-link-cy": "http://alinkinwelsh.com"},
                                     {"id": 2, "message-name": "downtime",
                                      "message-en": "Going down 10pm - 1am",
                                      "message-cy": "Going down 10pm - 1am in welsh",
                                      "hyperlink-message-en": "This is another hyperlink",
                                      "hyperlink-message-cy": "This is another hyperlink in welsh",
                                      "hyperlink-link-en": "http://anotherlink.com",
                                      "hyperlink-link-cy": "http://anotherlinkinwelsh.com"}]
                        }
        expected_response = [{'link': 'http://alinkinwelsh.com',
                              'link_text': 'This is a hyperlink in welsh',
                              'message': 'This is a test in welsh'},
                             {'link': 'http://anotherlinkinwelsh.com',
                              'link_text': 'This is another hyperlink in welsh',
                              'message': 'Going down 10pm - 1am in welsh'}]

        with super_test_context(app):
            g.requests.get.return_value.status_code = 200
            g.requests.get.return_value.json.return_value = message_json
            g.trace_id = "Help me"
            g.locale = "cy"

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}

            search_llc_service = SearchLocalLandChargeService(config)

            response = search_llc_service.get_service_messages()

            self.assertEqual(response, expected_response)

    def test_get_service_messages_no_messages(self):
        expected_response = []

        with super_test_context(app):
            g.requests.get.return_value.status_code = 404
            g.trace_id = "Help me"

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}

            search_llc_service = SearchLocalLandChargeService(config)

            response = search_llc_service.get_service_messages()

            self.assertEqual(response, expected_response)

    def test_get_service_messages_error(self):
        with super_test_context(app):
            g.requests.get.return_value.status_code = 500
            g.trace_id = "Help me"

            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}

            search_llc_service = SearchLocalLandChargeService(config)

            with self.assertRaises(ApplicationError):
                search_llc_service.get_service_messages()

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.LLC1DocumentAPIService')
    def test_check_for_completed_doc_url_ok(self, mock_llc1_api):
        with super_test_context(app):
            mock_llc1_api.return_value.poll.return_value = {"document_url": "someurl"}
            g.trace_id = "Help me"
            mock_post = MagicMock()
            mock_post.status_code = 201
            g.requests.post.return_value = mock_post
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            mock_search = MagicMock()
            mock_search.search_id = 1
            mock_search.document_url = None
            self.assertEqual(search_llc_service.check_for_completed_doc_url(mock_search).document_url, "someurl")
            g.requests.post.assert_called()

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.LLC1DocumentAPIService')
    def test_check_for_completed_doc_url_not_yet(self, mock_llc1_api):
        with super_test_context(app):
            mock_llc1_api.return_value.poll.return_value = None
            g.trace_id = "Help me"
            mock_post = MagicMock()
            mock_post.status_code = 201
            g.requests.post.return_value = mock_post
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            mock_search = MagicMock()
            mock_search.search_id = 1
            mock_search.document_url = None
            self.assertIsNone(search_llc_service.check_for_completed_doc_url(mock_search).document_url)
            g.requests.post.assert_not_called()

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.LLC1DocumentAPIService')
    def test_check_for_completed_doc_url_error(self, mock_llc1_api):
        with super_test_context(app):
            mock_llc1_api.return_value.poll.side_effect = ApplicationError("Some error", "ERR01", 300)
            g.trace_id = "Help me"
            mock_post = MagicMock()
            mock_post.status_code = 201
            g.requests.post.return_value = mock_post
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            mock_search = MagicMock()
            mock_search.search_id = 1
            mock_search.document_url = None
            self.assertEqual(search_llc_service.check_for_completed_doc_url(mock_search).document_url, "ERROR")
            g.requests.post.assert_not_called()

    def test_get_paid_search_items_404(self):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_paid_search_items("userid"), [])

    def test_get_paid_search_items_500(self):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            with self.assertRaises(ApplicationError):
                search_llc_service = SearchLocalLandChargeService(config)
                search_llc_service.get_paid_search_items("userid")

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.PaidSearchItem')
    def test_get_paid_search_items_ok(self, mock_paid_item):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp2 = MagicMock()
            mock_resp2.status_code = 201
            mock_search_item = MagicMock()
            mock_search_item.document_url = None
            mock_search_item2 = MagicMock()
            mock_search_item2.document_url = "ERROR"
            mock_search_item3 = MagicMock()
            mock_search_item3.document_url = "AURL"
            mock_paid_item.from_json_list.return_value = [mock_search_item, mock_search_item2, mock_search_item3]
            g.requests = MagicMock()
            g.requests.get.return_value = mock_resp
            g.requests.post.return_value = mock_resp2
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_paid_search_items("userid"),
                             [mock_search_item, mock_search_item2, mock_search_item3])

    def test_get_free_search_items_200(self):
        with super_test_context(app):
            respone_json = {'respone': 'this is json'}
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            g.requests.get.return_value = mock_resp
            g.requests.get.return_value.json.return_value = respone_json
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_free_search_items("userid", 20, 1), respone_json)

    def test_get_free_search_items_404(self):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_free_search_items("userid", 20, 1), {})

    def test_get_free_search_item_200(self):
        with super_test_context(app):
            respone_json = {'respone': 'this is json'}
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            g.requests.get.return_value = mock_resp
            g.requests.get.return_value.json.return_value = respone_json
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_free_search_for_user_by_search_id("userid", 'searchid'),
                             [respone_json])

    def test_get_free_search_item_404(self):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_free_search_for_user_by_search_id("userid", 'searchid'), [])

    def test_get_free_search_500(self):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            with self.assertRaises(ApplicationError):
                search_llc_service = SearchLocalLandChargeService(config)
                search_llc_service.get_free_search("anid")
            g.requests.get.assert_called()

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.PaidSearchItem')
    def test_get_free_search_ok(self, mock_paid_item):
        with super_test_context(app):
            g.trace_id = "Help me"
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"some": "json"}
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_free_search("userid"), {"some": "json"})

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.PaidSearchItem')
    def test_get_paid_search_item(self, mock_paid_item):
        with super_test_context(app):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"some": "json"}
            mock_paid_item.from_json.return_value = {"paid": "item"}
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            self.assertEqual(search_llc_service.get_paid_search_item("userid", "1"), {"paid": "item"})
            g.requests.get.assert_called_with("a URL/users/userid/paid-searches/1")
            mock_paid_item.from_json.assert_called_with({"some": "json"})

    @patch('server.dependencies.search_local_land_charge_api.'
           'search_local_land_charge_service.PaidSearchItem')
    def test_get_paid_search_item_error(self, mock_paid_item):
        with super_test_context(app):
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.json.return_value = {"some": "json"}
            mock_paid_item.from_json.return_value = {"paid": "item"}
            g.requests.get.return_value = mock_resp
            config = {'SEARCH_LOCAL_LAND_CHARGE_API_URL': "a URL"}
            search_llc_service = SearchLocalLandChargeService(config)
            with self.assertRaises(ApplicationError) as raises_context:
                search_llc_service.get_paid_search_item("userid", "1")
            self.assertEqual(raises_context.exception.code, "SLLC03")
            g.requests.get.assert_called_with("a URL/users/userid/paid-searches/1")
