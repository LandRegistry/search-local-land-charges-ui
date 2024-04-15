import $ from "jquery";
import { MAP_CONTROLS } from "./map_controls";
import { MAP_CONFIG } from "./map_config";
import { GEOSERVER_CONFIG } from "./geoserver";
import { SNAP_TO_VECTOR_LAYER } from "./snap_to_vector_layer";
import { COPY_VECTOR_LAYER } from "./copy_vector_layer";
import { MAP_HELPERS } from "./map_helpers";
import { Map } from "ol";
import { Zoom, ScaleLine } from 'ol/control';
import { View } from 'ol';
import { Draw, KeyboardPan } from "ol/interaction";
import { defaults as defaultInteractions } from 'ol/interaction/defaults';
import { shiftKeyOnly } from "ol/events/condition";
import { staticContentUrl } from './set_map_variables'
import { AddressMarker } from "./address_marker";
import { draw_layer_styles } from "./map_styles";

var map_controls = [
    MAP_CONTROLS.polygonButton(),
    MAP_CONTROLS.editButton(),
    MAP_CONTROLS.copyButton(),
    MAP_CONTROLS.snapTo(),
    MAP_CONTROLS.remove_button(),
    MAP_CONTROLS.removeAllButton(),
    MAP_CONTROLS.undoButton()
];

var map = new Map({
    layers: [
        MAP_CONFIG.baseLayer,
        GEOSERVER_CONFIG.boundariesLayer,
        MAP_CONFIG.drawLayer
    ],
    logo: false,
    target: 'map',
    controls: [
        new Zoom({zoomInLabel: "", zoomOutLabel: "", zoomInTipLabel: _("Zoom in"), zoomOutTipLabel: _("Zoom out")}),
        new ScaleLine()
    ],
    view: new View({
        projection: MAP_CONFIG.projection,
        resolutions: MAP_CONFIG.resolutions,
        center: MAP_CONFIG.defaultCenter,
        zoom: MAP_CONFIG.defaultZoom
    }),
    interactions: defaultInteractions().extend([
        new KeyboardPan({ condition: shiftKeyOnly, pixelDelta: 10 }),
    ])
});

//Prevent zooming in when finishing drawing polygon
map.on("dblclick", function (e) {
    if (MAP_CONTROLS.currentInteraction instanceof Draw) {
        return false;
    }
});

map.on('pointermove', function(browserEvent) {
    var pixel = browserEvent.pixel;
    document.body.style.cursor = '';

    map.forEachFeatureAtPixel(pixel, function(pixelFeature, layer) {
        if (layer == MAP_CONFIG.drawLayer && MAP_CONTROLS.currentStyle == draw_layer_styles.REMOVE) {
            document.body.style.cursor = 'pointer';
        }
    })
});

map.on('moveend', function () {
    var extentOnMap = MAP_CONFIG.drawSource.getFeatures().length;

    if (MAP_HELPERS.mapIsPastZoomThreshold(map)) {
        MAP_CONTROLS.toggleButtons([
            MAP_CONTROLS.copyButtonId,
            MAP_CONTROLS.snapToButtonId
        ], true);
    } else {
        SNAP_TO_VECTOR_LAYER.disable();
        COPY_VECTOR_LAYER.disable();
        MAP_CONTROLS.toggleButtons([
            MAP_CONTROLS.copyButtonId,
            MAP_CONTROLS.snapToButtonId
        ], false);
    }

    if (extentOnMap) {
        MAP_CONTROLS.enableReviewButtons();
    } else {
        MAP_CONTROLS.disableReviewButtons();
    }

    var zoomLevel = map.getView().getZoom();
    var zoomIn = $('.ol-zoom-in')
    var zoomOut = $('.ol-zoom-out')
    if (zoomLevel === MAP_CONFIG.maxZoomLevel) {
        zoomIn.prop('disabled', true);
        zoomOut.prop('disabled', false);
    }
    else if (zoomLevel === 0) {
        zoomIn.prop('disabled', false);
        zoomOut.prop('disabled', true);
    }
    else {
        zoomIn.prop('disabled', false);
        zoomOut.prop('disabled', false);
    }
});

var addressMarker = new AddressMarker(staticContentUrl)
map.addLayer(addressMarker.addressMarkerLayer);

//Catch mousewheel events if tabbable
if (map.getTargetElement().getAttribute("tabindex") != null) {
   map.getTargetElement().addEventListener("wheel", function(event) {
       event.preventDefault();
       this.focus();
});
}

export { map, addressMarker };
