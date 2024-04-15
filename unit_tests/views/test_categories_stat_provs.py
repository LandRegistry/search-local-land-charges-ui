from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import url_for

from server.main import app


class TestStatutoryProvisions(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["profile"] = {"user_id": "mock_user"}

    @patch("server.views.categories_stat_provs.StatProvService")
    def test_get_json_stat_prov_history(self, mock_stat_prov):
        mock_stat_prov.return_value.get_history.return_value = {"some": "json"}
        response = self.client.get(url_for("categories_stat_provs.get_json_stat_prov_history"))
        self.assertEqual(response.get_json(), {"some": "json"})

    @patch("server.views.categories_stat_provs.StatProvService")
    def test_get_json_stat_prov(self, mock_stat_prov):
        mock_stat_prov.return_value.get.return_value = {"some": "json"}
        response = self.client.get(url_for("categories_stat_provs.get_json_stat_prov", selectable="RHUBARB"))
        self.assertEqual(response.get_json(), {"some": "json"})
        mock_stat_prov.return_value.get.assert_called_with("RHUBARB")

    @patch("server.views.categories_stat_provs.StatProvService")
    def test_get_json_stat_prov_list(self, mock_stat_prov):
        mock_stat_prov.return_value.get_history.return_value = [
            {
                "title": "A new version",
                "display_title": "A new version",
                "selectable": True,
                "created_timestamp": "2022-07-13T14:43:31.557072",
            },
            {
                "title": "An old version",
                "display_title": "A new version",
                "selectable": False,
            },
        ]
        response = self.client.get(url_for("categories_stat_provs.get_page_stat_prov", sort_by="last_updated"))
        self.assertIn("A new version", response.text)
        self.assertIn("An old version", response.text)
        self.assertIn("13 July 2022", response.text)

    @patch("server.views.categories_stat_provs.StatProvService")
    def test_get_json_stat_prov_removed_list(self, mock_stat_prov):
        mock_stat_prov.return_value.get_history.return_value = [
            {
                "title": "A new version",
                "display_title": "A new version",
                "selectable": False,
                "unselectable_timestamp": "2022-07-13T14:43:31.557072",
            },
            {
                "title": "An old version",
                "display_title": "A new version",
                "selectable": False,
            },
        ]
        response = self.client.get(
            url_for(
                "categories_stat_provs.get_page_stat_prov_removed",
                sort_by="date_removed",
            )
        )
        self.assertIn("A new version", response.text)
        self.assertIn("An old version", response.text)
        self.assertIn("13 July 2022", response.text)

    @patch("server.views.categories_stat_provs.CategoryService")
    def test_get_page_categories(self, mock_cat):
        mock_cat.return_value.get_all_and_sub.return_value = {"some": "stuff"}

        response = self.client.get(url_for("categories_stat_provs.get_page_categories"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("List of categories", response.text)

    @patch("server.views.categories_stat_provs.CategoryService")
    def test_get_categories_and_sub(self, mock_cat):
        mock_cat.return_value.get_all_and_sub.return_value = {"some": "stuff"}

        response = self.client.get(url_for("categories_stat_provs.get_categories_and_sub"))
        self.assertEqual(response.json, {"some": "stuff"})

    @patch("server.views.categories_stat_provs.CategoryService")
    def test_get_all_categories(self, mock_cat):
        mock_cat.return_value.get.return_value = {"some": "stuff"}

        response = self.client.get(url_for("categories_stat_provs.get_all_categories"))
        self.assertEqual(response.json, {"some": "stuff"})

    @patch("server.views.categories_stat_provs.CategoryService")
    def test_get_category(self, mock_cat):
        mock_response = MagicMock()
        mock_response.json.return_value = {"some": "stuff"}
        mock_response.status_code = 207
        mock_cat.return_value.get_category.return_value = mock_response

        response = self.client.get(url_for("categories_stat_provs.get_category", category="acat"))
        self.assertEqual(response.json, {"some": "stuff"})
        self.assertEqual(response.status_code, 207)
        mock_cat.return_value.get_category.assert_called_with("acat")

    @patch("server.views.categories_stat_provs.CategoryService")
    def test_get_sub_category(self, mock_cat):
        mock_response = MagicMock()
        mock_response.json.return_value = {"some": "stuff"}
        mock_response.status_code = 207
        mock_cat.return_value.get_sub_category.return_value = mock_response

        response = self.client.get(
            url_for(
                "categories_stat_provs.get_sub_category",
                category="acat",
                sub_category="asubcat",
            )
        )
        self.assertEqual(response.json, {"some": "stuff"})
        self.assertEqual(response.status_code, 207)
        mock_cat.return_value.get_sub_category.assert_called_with("acat", "asubcat")
