from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid


def merge_polygons(extent):
    # Convert the FeatureCollection to GeometryCollection because Shapely doesn't like FCs
    geometry_collection = {
        "type": "GeometryCollection",
        "geometries": [feature["geometry"] for feature in extent["features"]],
    }

    # Convert to Shapely format
    extent_shape = make_valid(shape(geometry_collection))

    # Merge all the polygons together
    geo_extent_shape = unary_union(extent_shape)

    # Convert from Shapely format (mapping function)
    json_union = mapping(geo_extent_shape)

    # And finally convert back into a FeatureCollection. Phew.
    union_geojson = {
        "type": "FeatureCollection",
        "features": [{"geometry": json_union, "type": "Feature", "properties": None}],
    }

    return union_geojson
