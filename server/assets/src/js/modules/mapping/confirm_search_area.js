import $ from "jquery";
import { map } from "./map";
import { GeoJSON } from "ol/format";
import { Vector as SourceVector } from "ol/source";
import { Vector as LayerVector } from "ol/layer";
import { draw_layer_styles } from "./map_styles";

var DISPLAY_SEARCH_EXTENT = {}

$(function () {
    // Remove map controls (draw tools) and interactions (zooming, panning, etc.)
    map.getControls().clear();
    map.getInteractions().clear();

    // Add New Layer to Open Layers for LLC
    map.addLayer(DISPLAY_SEARCH_EXTENT.layer);

    if (search_extent != '') {
        map.getView().fit(DISPLAY_SEARCH_EXTENT.source.getExtent(), {maxZoom: '15'});
    }
});

// Open Layers Local Land Charge Display Layer
var search_extent = $('#saved-features').val();

DISPLAY_SEARCH_EXTENT.features = new GeoJSON().readFeatures(search_extent);
DISPLAY_SEARCH_EXTENT.source = new SourceVector({features: DISPLAY_SEARCH_EXTENT.features});
DISPLAY_SEARCH_EXTENT.layer = new LayerVector({
    source: DISPLAY_SEARCH_EXTENT.source, style: draw_layer_styles.style[draw_layer_styles.DRAW]
});
