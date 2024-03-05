from flask import url_for
from unittest.mock import patch
from server.main import app
from unittest import TestCase


class TestCheckMigratedAuthorities(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_post(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.organisation_search.data = "Anorganisation"
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"}
        ]
        response = self.client.post(url_for("check_migrated_authorities.check_authorities"))
        self.assertIn("Anorganisation is on the register but information for this area is temporarily not available",
                      response.text)

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_post_not_found(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.organisation_search.data = "Anorganisationthatdoesntmatch"
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"}
        ]
        response = self.client.post(url_for("check_migrated_authorities.check_authorities"))
        self.assertIn("Sorry, we are experiencing technical difficulties",
                      response.text)
        self.assertEqual(response.status_code, 500)
        mock_local_auth.get_organisations.assert_called()

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_get(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        mock_form.return_value.errors = None
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"}
        ]
        response = self.client.get(url_for("check_migrated_authorities.check_authorities"))
        self.assertIn("Check if your authority has moved to this register",
                      response.text)
