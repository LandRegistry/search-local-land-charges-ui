from unittest import TestCase
from server.services import merge_polygons
from unit_tests.test_data.mock_features import pre_union, post_union
from shapely.geometry import shape


class TestMergePolygons(TestCase):

    def test_merge_polygons(self):
        result = merge_polygons.merge_polygons(pre_union)
        self.assertTrue(shape(result['features'][0]['geometry']).equals(
                        shape(post_union['features'][0]['geometry'])))
