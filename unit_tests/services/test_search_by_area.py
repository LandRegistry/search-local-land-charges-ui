import json
from unittest import TestCase, mock
from unittest.mock import Mock

from server.services.search_by_area import SearchByArea


class TestSearchByArea(TestCase):
    SEARCH_BY_AREA_PATH = "server.services.search_by_area"

    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_AREA_PATH))
    def test_search_by_area_with_bbox_no_paging(self, mock_local_land_charge_service):
        expected_response = "some response"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response

        mock_local_land_charge_service.return_value.get.return_value = mock_response

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000],
                            ]
                        ],
                    },
                    "properties": {"id": 1519313947379},
                }
            ],
        }

        extents = []
        for feature in bounding_box["features"]:
            geo_dict = {
                "type": "Polygon",
                "coordinates": feature["geometry"]["coordinates"],
            }
            extents.append(geo_dict)

        collection = {"type": "geometrycollection", "geometries": extents}

        expected = json.dumps(collection)

        config = {"SEARCH_API_URL": "TEST"}
        search_by_area = SearchByArea(Mock(), config)
        response = search_by_area.process(bounding_box)

        self.assertEqual(response["data"], expected_response)
        mock_local_land_charge_service.return_value.get.assert_called_with(expected, None)

    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_AREA_PATH))
    def test_search_by_area_with_bbox_multiple_extents(self, mock_local_land_charge_service):
        expected_response = "some response"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response

        mock_local_land_charge_service.return_value.get.return_value = mock_response

        bounding_box = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290000, 910000],
                                [290100, 910000],
                                [290100, 910100],
                                [290000, 910100],
                                [290000, 910000],
                            ]
                        ],
                    },
                    "properties": {"id": 1519313947379},
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [290001, 910001],
                                [290101, 910001],
                                [290101, 910101],
                                [290001, 910101],
                                [290001, 910001],
                            ]
                        ],
                    },
                    "properties": {"id": 1519313947380},
                },
            ],
        }

        extents = []
        for feature in bounding_box["features"]:
            geo_dict = {
                "type": "Polygon",
                "coordinates": feature["geometry"]["coordinates"],
            }
            extents.append(geo_dict)

        collection = {"type": "geometrycollection", "geometries": extents}

        expected = json.dumps(collection)

        config = {"SEARCH_API_URL": "TEST"}
        search_by_area = SearchByArea(Mock(), config)
        response = search_by_area.process(bounding_box)

        self.assertEqual(response["data"], expected_response)
        mock_local_land_charge_service.return_value.get.assert_called_with(expected, None)
