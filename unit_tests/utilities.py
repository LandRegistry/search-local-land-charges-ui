from unittest.mock import MagicMock

from cryptography.fernet import Fernet
from flask import current_app, g


class Utilities(object):
    """Helper class that mocks out the session for test making app requests.


    Supports both unittest framework and flasktest framework.

    Place in test set up Utilities.mock_session_cookie_unittest(self)

    or

    Utilities.mock_session_cookie_flask_test(self)
    """

    @staticmethod
    def mock_request():
        g.trace_id = "333"
        g.session = MagicMock()
        g.requests = MagicMock()

    @staticmethod
    def mock_response(status_code=200, text="", json=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        if json:
            response.json.return_value = json
        return response

    @staticmethod
    def create_enc_search_id(search_id):
        f = Fernet(current_app.config["GEOSERVER_SECRET_KEY"])
        return f.encrypt(str(search_id).encode()).decode()
