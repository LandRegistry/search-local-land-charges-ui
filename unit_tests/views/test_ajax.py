from flask import url_for
from unittest.mock import MagicMock, patch
from server.main import app
from unittest import TestCase

from server.models.searches import SearchState


class TestCheckMigratedAuthorities(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch("server.views.ajax.LocalAuthorityAPIService")
    @patch("server.views.ajax.request")
    def test_local_authority_service_boundingbox_ok(self, mock_request, mock_local_auth):
        mock_request.is_xhr = True
        mock_response = MagicMock()
        mock_response.json.return_value = {"aard": "vark"}
        mock_response.status_code = 211
        mock_local_auth.get_bounding_box.return_value = mock_response
        response = self.client.get(url_for("ajax.local_authority_service_boundingbox", authority="Anauthority"))
        self.assertEqual(response.json, {'aard': 'vark'})
        self.assertEqual(response.status_code, 211)
        mock_local_auth.get_bounding_box.assert_called_with("Anauthority")

    @patch("server.views.ajax.request")
    def test_local_authority_service_boundingbox_notxhr(self, mock_request):
        mock_request.is_xhr = False
        response = self.client.get(url_for("ajax.local_authority_service_boundingbox", authority="Anauthority"))
        self.assertEqual(response.status_code, 500)

    @patch("server.views.ajax.request")
    def test_ajax_llc1_pdf_poll_notxhr(self, mock_request):
        mock_request.is_xhr = False
        response = self.client.get(url_for("ajax.ajax_llc1_pdf_poll", enc_search_id="someid"))
        self.assertEqual(response.status_code, 500)

    @patch("server.views.ajax.request")
    def test_ajax_llc1_pdf_poll_not_found(self, mock_request):
        mock_request.is_xhr = True
        search_state = SearchState()
        search_state.search_reference = None
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"ansearchid": {"search_state": search_state}}
        response = self.client.get(url_for("ajax.ajax_llc1_pdf_poll", enc_search_id="ansearchid"))
        self.assertEqual(response.json, {"status": "search reference not set"})
        self.assertEqual(response.status_code, 404)

    @patch("server.views.ajax.LLC1DocumentAPIService")
    @patch("server.views.ajax.request")
    def test_ajax_llc1_pdf_poll_generating(self, mock_request, mock_llc1):
        mock_request.is_xhr = True
        mock_llc1.return_value.poll.return_value = None
        search_state = SearchState()
        search_state.search_reference = 1234
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"ansearchid": {"search_state": search_state}}
        response = self.client.get(url_for("ajax.ajax_llc1_pdf_poll", enc_search_id="ansearchid"))
        self.assertEqual(response.json, {"status": "generating"})
        self.assertEqual(response.status_code, 202)

    @patch("server.views.ajax.LLC1DocumentAPIService")
    @patch("server.views.ajax.request")
    def test_ajax_llc1_pdf_poll_success(self, mock_request, mock_llc1):
        mock_request.is_xhr = True
        mock_llc1.return_value.poll.return_value = "A thing"
        search_state = SearchState()
        search_state.search_reference = 1234
        with self.client.session_transaction() as sess:
            sess["paid_searches"] = {"ansearchid": {"search_state": search_state}}
        response = self.client.get(url_for("ajax.ajax_llc1_pdf_poll", enc_search_id="ansearchid"))
        self.assertEqual(response.json, {"status": "success"})
        self.assertEqual(response.status_code, 201)
