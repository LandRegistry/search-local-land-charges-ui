import { map } from "./map";
import { GeoJSON } from "ol/format";
import { Vector as SourceVector } from "ol/source";
import { Vector as LayerVector } from "ol/layer";
import { Style, Circle, Fill, Stroke } from "ol/style";

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
    source: DISPLAY_SEARCH_EXTENT.source, style: new Style({
        fill: new Fill({
            color: [6, 88, 229, 0.15]
        }),
        stroke: new Stroke({
            color: '#0658e5',
            width: 2,
            lineDash: [1, 5]
        }),
        image: new Circle({
            radius: 7,
            fill: new Fill({
                color: '#0658e5'
            })
        })
    })
});
