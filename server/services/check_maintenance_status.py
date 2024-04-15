from flask import current_app

from server.dependencies.local_authority_api.local_authority_api_service import (
    LocalAuthorityAPIService,
)


class CheckMaintenanceStatus(object):
    @staticmethod
    def under_maintenance():
        current_app.logger.info("Checking for any organisations under maintenance")
        organisations = LocalAuthorityAPIService.get_organisations()
        for organisation in organisations:
            if organisation["maintenance"]:
                current_app.logger.info("Found organisation '{}' under maintenance".format(organisation))
                return True
        current_app.logger.info("No organisations found under maintenance")
        return False
