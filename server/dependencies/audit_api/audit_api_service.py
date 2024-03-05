from server.config import AUDIT_API_URL
from landregistry.exceptions import ApplicationError
from flask import current_app, g, session
from datetime import datetime, timezone
import json
import socket
import copy


class AuditAPIService(object):
    @staticmethod
    def audit_event(activity, origin_id=None, component_name="search-for-local-land-charges",
                    business_service="Search Local Land Charge UI", trace_id=None, supporting_info=None):
        """Sends audit event to Audit API"""

        if not origin_id:
            if 'profile' in session and 'user_id' in session['profile']:
                origin_id = session['profile']['user_id']
            else:
                origin_id = "search-local-land-charge-ui"
        if not trace_id:
            trace_id = g.trace_id

        event = {'activity': activity,
                 'activity_timestamp': datetime.now(timezone.utc).isoformat(),
                 'origin_id': origin_id,
                 'component_name': component_name,
                 'business_service': business_service,
                 'trace_id': trace_id}

        host_ip = socket.gethostbyname(socket.gethostname())

        if supporting_info:
            extra_info = copy.copy(supporting_info)
            extra_info['machine_ip'] = host_ip
            event['supporting_info'] = extra_info
        else:
            supporting_info = {'machine_ip': host_ip}
            event['supporting_info'] = supporting_info

        try:
            current_app.logger.info("Sending event to audit api")
            response = g.requests.post('{}/records'.format(AUDIT_API_URL),
                                       data=json.dumps(event),
                                       headers={'Content-Type': 'application/json'})
        except Exception:
            raise ApplicationError("Error sending audit information", "AUDIT01", 500)

        if response.status_code != 201:
            raise ApplicationError("Error sending audit information", "AUDIT02", 500)
