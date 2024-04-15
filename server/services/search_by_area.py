import json

from server.dependencies.search_api.local_land_charge_service import (
    LocalLandChargeService,
)


class SearchByArea(object):
    def __init__(self, logger, config):
        self.logger = logger
        self.local_land_charge_service = LocalLandChargeService(config)

    def process(self, bounding_box, results_filter=None):
        response = dict()
        if bounding_box:
            self.logger.info("Searching area by bounding box")
            bounding_box_json = self.build_bounding_box_json(bounding_box)
            search_response = self.local_land_charge_service.get(bounding_box_json, results_filter)

            response["status"] = search_response.status_code
            if search_response.status_code == 200:
                response["data"] = search_response.json()
        else:
            response["status"] = 500
        return response

    @staticmethod
    def build_bounding_box_json(bounding_box):
        collection = {
            "type": "geometrycollection",
            "geometries": [feature["geometry"] for feature in bounding_box["features"]],
        }

        return json.dumps(collection)
