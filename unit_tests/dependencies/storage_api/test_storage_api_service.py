from unittest import TestCase
from flask import g
from unittest.mock import MagicMock
from server import main
from server.dependencies.storage_api.storage_api_service import StorageAPIService
from landregistry.exceptions import ApplicationError

STORAGE_API_SERVICE_PATH = "maintain_frontend.dependencies.storage_api.storage_api_service"


class TestStorageApiService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def setup_response_mock(self, status_code, json_return_value):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_return_value
        return response

    def setup_storage_api_service(self):
        config = {"STORAGE_API_URL": "anurl"}
        storage_api_service = StorageAPIService(config)
        return storage_api_service

    def test_get_external_url_success(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            expected_result = {"external_reference": "mock_report_url"}
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url(mock_file_id, mock_bucket)

            self.assertEqual(result, "mock_report_url")
            g.requests.get.assert_called_with(
                "{}/{}/{}/external-url".format("anurl", mock_bucket, mock_file_id), params={}
            )

    def test_get_external_url_success_with_subdirectories(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            expected_result = {"external_reference": "mock_report_url"}
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url(
                "mock file id", "test_bucket", subdirectories="a subdirectory"
            )

            self.assertEqual(result, "mock_report_url")
            g.requests.get.assert_called_with(
                "{}/{}/{}/external-url".format("anurl", mock_bucket, mock_file_id),
                params={"subdirectories": "a subdirectory"},
            )

    def test_get_external_url_error_404(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            response = self.setup_response_mock(404, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            with self.assertRaises(ApplicationError) as raises_context:
                storage_api_service.get_external_url(mock_file_id, mock_bucket)
            self.assertEqual(raises_context.exception.code, "STORE03")

    def test_get_external_url_error_500(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            response = self.setup_response_mock(500, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            with self.assertRaises(ApplicationError) as raises_context:
                storage_api_service.get_external_url(mock_file_id, mock_bucket)
            self.assertEqual(raises_context.exception.code, "STORE04")

    def test_get_external_url_for_document_url_200(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            expected_result = {"external_reference": "mock_report_url"}
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url_for_document_url("{}/{}".format(mock_bucket, mock_file_id))

            self.assertEqual(result, "mock_report_url")
            g.requests.get.assert_called_with("{}{}/{}/external-url".format("anurl", mock_bucket, mock_file_id))

    def test_get_external_url_for_document_url_404(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            expected_result = {"external_reference": "mock_report_url"}
            response = self.setup_response_mock(404, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            with self.assertRaises(ApplicationError) as raises_context:
                storage_api_service.get_external_url_for_document_url("{}/{}".format(mock_bucket, mock_file_id))
            self.assertEqual(raises_context.exception.code, "STORE01")

            g.requests.get.assert_called_with("{}{}/{}/external-url".format("anurl", mock_bucket, mock_file_id))

    def test_get_external_url_for_document_url_500(self):
        with main.app.test_request_context():
            mock_file_id = "mock file id"
            mock_bucket = "test_bucket"

            response = self.setup_response_mock(500, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            with self.assertRaises(ApplicationError) as raises_context:
                storage_api_service.get_external_url_for_document_url("{}/{}".format(mock_bucket, mock_file_id))
            self.assertEqual(raises_context.exception.code, "STORE02")
