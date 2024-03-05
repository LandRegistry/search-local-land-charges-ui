from unittest import TestCase, mock

from server.services.check_maintenance_status import CheckMaintenanceStatus
from server.main import app
from flask import g


class TestCheckMaintenance(TestCase):

    @mock.patch("server.services.check_maintenance_status.LocalAuthorityAPIService")
    def test_no_maintenance(self, mock_local_authority_api_service):

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                mock_local_authority_api_service.get_organisations.return_value = [
                    {"maintenance": False}
                ]
                self.assertFalse(CheckMaintenanceStatus.under_maintenance())

    @mock.patch("server.services.check_maintenance_status.LocalAuthorityAPIService")
    def test_maintenance(self, mock_local_authority_api_service):

        with app.app_context():
            with app.test_request_context():
                g.trace_id = "test"
                mock_local_authority_api_service.get_organisations.return_value = [
                    {"maintenance": True}
                ]
                self.assertTrue(CheckMaintenanceStatus.under_maintenance())
