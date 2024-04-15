from datetime import datetime, timezone

from flask import current_app, g
from landregistry.exceptions import ApplicationError

from server.config import REPORT_API_BASE_URL


class ReportAPIService(object):
    """Service class for making requests to report-api"""

    @staticmethod
    def send_event(event_name, event_details):
        current_app.logger.info(
            "Calling the report event endpoint of the Report API " "with the following data: {}".format(event_details)
        )
        payload = {
            "event_name": event_name,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "event_details": event_details,
        }

        response = g.requests.post(
            "{}/v2.0/report_events".format(REPORT_API_BASE_URL),
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 201:
            raise ApplicationError(
                "Failed to send event to report-api, status was {}".format(response.status_code),
                "REPORT01",
                500,
            )
