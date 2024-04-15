import contextlib
import logging
import sys
from unittest.mock import MagicMock, patch

from flask import current_app, g

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@contextlib.contextmanager
def super_test_context(app, **kwargs):
    with app.app_context():
        with app.test_request_context(**kwargs):
            g.trace_id = "atraceid"
            current_app.logger = MagicMock()
            current_app.logger.info.side_effect = log_info
            current_app.logger.warn.side_effect = log_warn
            current_app.logger.warning.side_effect = log_warn
            current_app.logger.error.side_effect = log_error
            current_app.logger.exception.side_effect = log_exception
            current_app.logger.critical.side_effect = log_critical
            current_app.logger.debug.side_effect = log_debug
            with patch("server.main.RequestsSessionTimeout") as mock_requests:
                g.requests = mock_requests.return_value
                yield None


def log_info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)


def log_warn(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)


def log_exception(msg, *args, **kwargs):
    logger.exception(msg, *args, **kwargs)


def log_critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


def log_debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)
