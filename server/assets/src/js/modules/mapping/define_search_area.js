import { loadPreviousData, populateGeometries } from "./save_load_geometries";
import { MAP_HELPERS } from "./map_helpers";

var searchAreaVarsElement = document.getElementById('mapping-define-search-area-variables');
var search_area_vars = JSON.parse(searchAreaVarsElement.innerHTML);

var information = search_area_vars['information'];
var zoom_extent = search_area_vars['zoom_extent'];
var zoom_to_location = search_area_vars['zoom_to_location'];
var coordinate_search = search_area_vars['coordinate_search'];
var local_authority_boundary_url = search_area_vars['local_authority_boundary_url'];

if (information != null) {
    loadPreviousData(information);
    MAP_HELPERS.zoomToPreviousExtent(zoom_extent);
} else if (zoom_to_location != null) {
    MAP_HELPERS.zoomToLocation(zoom_to_location, coordinate_search);
} else if (local_authority_boundary_url != null) {
    MAP_HELPERS.zoom_to_authority_boundary(local_authority_boundary_url);
} else {
    MAP_HELPERS.zoomToBoundary();
}

$('#define-search-area-form').submit(function() {
    populateGeometries();
});
