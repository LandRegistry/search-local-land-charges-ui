from unittest import TestCase
from unittest.mock import patch

from flask import url_for

from server.main import app


class TestCheckMigratedAuthorities(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    def test_redirect(self):
        resp = self.client.get(url_for("check_migrated_authorities.old_check_authorities"))
        assert resp.status_code == 302
        assert resp.location == url_for("check_migrated_authorities.check_authorities")

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_post(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.organisation_search.data = "Anorganisation"
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"},
        ]
        response = self.client.post(url_for("check_migrated_authorities.check_authorities"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            url_for("check_migrated_authorities.show_authority_migrated_details"),
        )

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_post_not_found(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = True
        mock_form.return_value.organisation_search.data = "Anorganisationthatdoesntmatch"
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"},
        ]
        response = self.client.post(url_for("check_migrated_authorities.check_authorities"))
        self.assertIn("Sorry, there is a problem with the service", response.text)
        self.assertEqual(response.status_code, 500)
        mock_local_auth.get_organisations.assert_called()

    @patch("server.views.check_migrated_authorities.CheckMigratedAuthoritiesForm")
    @patch("server.views.check_migrated_authorities.LocalAuthorityAPIService")
    def test_check_authorities_get(self, mock_local_auth, mock_form):
        mock_form.return_value.validate_on_submit.return_value = False
        mock_form.return_value.errors = None
        mock_local_auth.get_organisations.return_value = [
            {"title": "Anorganisation", "migrated": True, "maintenance": True},
            {"title": "Another organisation"},
        ]
        response = self.client.get(url_for("check_migrated_authorities.check_authorities"))
        self.assertIn("Check if a local authority is available on this service", response.text)

    def test_get_show_authority_migrated_details_migrated(self):
        with self.client.session_transaction() as sess:
            sess["organisation_details"] = {
                "title": "Test Authority",
                "migrated": True,
                "maintenance": False,
            }
        response = self.client.get(url_for("check_migrated_authorities.show_authority_migrated_details"))
        self.assertIn("Test Authority is available on this service", response.text)

    def test_get_show_authority_migrated_details_not_migrated(self):
        with self.client.session_transaction() as sess:
            sess["organisation_details"] = {
                "title": "Test Authority",
                "migrated": False,
                "maintenance": False,
            }
        response = self.client.get(url_for("check_migrated_authorities.show_authority_migrated_details"))
        self.assertIn("Test Authority is not yet available on this service", response.text)

    def test_get_show_authority_migrated_details_migrated_maintenance(self):
        with self.client.session_transaction() as sess:
            sess["organisation_details"] = {
                "title": "Test Authority",
                "migrated": True,
                "maintenance": True,
            }
        response = self.client.get(url_for("check_migrated_authorities.show_authority_migrated_details"))
        self.assertIn(
            "Test Authority is on the register but information for this area is temporarily not available",
            response.text,
        )

    def test_get_show_authority_migrated_details_not_migrated_maintenance(self):
        with self.client.session_transaction() as sess:
            sess["organisation_details"] = {
                "title": "Test Authority",
                "migrated": False,
                "maintenance": True,
            }
        response = self.client.get(url_for("check_migrated_authorities.show_authority_migrated_details"))
        self.assertIn(
            "Test Authority is on the register but information for this area is temporarily not available",
            response.text,
        )
