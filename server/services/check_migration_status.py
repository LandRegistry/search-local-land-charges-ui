from server.dependencies.local_authority_api.local_authority_api_service \
    import LocalAuthorityAPIService

from flask import current_app


class CheckMigrationStatus(object):

    @staticmethod
    def process(bounding_box):
        if bounding_box:
            current_app.logger.info("Searching area by bounding box")
            bounding_box_json = CheckMigrationStatus.build_bounding_box_json(bounding_box)

            plus_minus_buffer = LocalAuthorityAPIService.plus_minus_buffer(bounding_box_json)

            # Test response in descending order of severity in search service
            if len(plus_minus_buffer['minus_buffer']['maintenance_list']) > 0:
                plus_minus_buffer['flag'] = "fail_maintenance"
            elif len(plus_minus_buffer['plus_buffer']['maintenance_list']) > 0:
                plus_minus_buffer['flag'] = "fail_maintenance_contact"
            elif plus_minus_buffer['minus_buffer']['includes_scotland']:
                plus_minus_buffer['flag'] = "fail_scotland"
            elif len(plus_minus_buffer['minus_buffer']['non_migrated_list']) > 0:
                plus_minus_buffer['flag'] = "fail"
            elif len(plus_minus_buffer['migrated_list']) == 0:
                plus_minus_buffer['flag'] = "fail_no_authority"
            elif plus_minus_buffer['plus_buffer']['includes_scotland']:
                plus_minus_buffer['flag'] = "warning"
            elif len(plus_minus_buffer['plus_buffer']['non_migrated_list']) > 0:
                plus_minus_buffer['flag'] = "warning"
            else:
                plus_minus_buffer['flag'] = "pass"

            plus_minus_buffer['includes_migrated'] = len(plus_minus_buffer['migrated_list']) > 0

            return plus_minus_buffer
        else:
            return None

    @staticmethod
    def build_bounding_box_json(bounding_box):
        collection = {
            "type": "GeometryCollection",
            "geometries": [feature['geometry'] for feature in bounding_box['features']]
        }

        return collection
