from unittest import TestCase
from flask import g
import json
import time
from unittest.mock import MagicMock, patch
from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server import main
from landregistry.exceptions import ApplicationError
from unit_tests.utilities_tests import super_test_context


class TestAuditAPIService(TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False
        main.app.testing = True

    def test_audit_event_success(self):
        with super_test_context(main.app):
            g.requests = MagicMock()
            g.trace_id = 123

            response = MagicMock()
            response.status_code = 201

            g.requests.post.return_value = response
            AuditAPIService.audit_event("A thing")
            g.requests.post.assert_called()

    def test_audit_event_timestamps(self):
        with super_test_context(main.app):
            g.requests = MagicMock()
            g.trace_id = 123

            response = MagicMock()
            response.status_code = 201

            g.requests.post.return_value = response
            AuditAPIService.audit_event("A thing")
            call1 = g.requests.post.call_args
            args, kwargs = call1
            call1_timestamp = json.loads(kwargs['data'])['activity_timestamp']

            time.sleep(0.1)

            AuditAPIService.audit_event("A thing")
            call2 = g.requests.post.call_args
            args, kwargs = call2
            call2_timestamp = json.loads(kwargs['data'])['activity_timestamp']

            self.assertNotEqual(call1_timestamp, call2_timestamp)

    def test_audit_event_exception(self):
        with super_test_context(main.app):
            g.requests = MagicMock()
            g.trace_id = '123'
            g.requests.post.side_effect = Exception('Test exception')

            try:
                AuditAPIService.audit_event("Test Event")
            except ApplicationError as e:
                self.assertEqual(e.http_code, 500)

    def test_audit_event_fail_raises_application_error(self):
        with super_test_context(main.app):
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 400

            g.requests.post.return_value = response

            try:
                AuditAPIService.audit_event("A thing")
            except ApplicationError as e:
                self.assertEqual(e.http_code, 500)

    @patch('server.dependencies.audit_api.audit_api_service.socket')
    def test_audit_event_machine_ip_with_supporting_info(self, mock_socket):
        with super_test_context(main.app):
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing", supporting_info={"another": "thing"})
            g.requests.post.assert_called()
            message = json.loads(g.requests.post.call_args[1]['data'])
            self.assertIn('machine_ip', message['supporting_info'])
            self.assertEqual("1.1.1.1", message['supporting_info']['machine_ip'])
            self.assertIn('another', message['supporting_info'])
            self.assertEqual("thing", message['supporting_info']['another'])

    @patch('server.dependencies.audit_api.audit_api_service.socket')
    def test_audit_event_machine_ip_without_supporting_info(self, mock_socket):
        with super_test_context(main.app):
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing")
            g.requests.post.assert_called()
            message = json.loads(g.requests.post.call_args[1]['data'])
            self.assertIn('machine_ip', message['supporting_info'])
            self.assertEqual("1.1.1.1", message['supporting_info']['machine_ip'])
            self.assertNotIn('another', message['supporting_info'])

    @staticmethod
    def mock_request():
        g.trace_id = '333'
        g.session = MagicMock()
        g.session.user.id = "USER123"
        g.requests = MagicMock()

    @staticmethod
    def mock_response(status_code=200, text='', json=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        if json:
            response.json.return_value = json
        return response
