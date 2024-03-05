import { MAP_CONTROLS } from "./map_controls";
import { MAP_CONFIG } from "./map_config";
import { GEOSERVER_CONFIG } from "./geoserver";
import { SNAP_TO_VECTOR_LAYER } from "./snap_to_vector_layer";
import { COPY_VECTOR_LAYER } from "./copy_vector_layer";
import { MAP_HELPERS } from "./map_helpers";
import { Map } from "ol";
import { Zoom, ScaleLine, Attribution} from 'ol/control';
import { View } from 'ol';
import { Draw } from "ol/interaction";
import { staticContentUrl } from './set_map_variables'
import { AddressMarker } from "./address_marker";
import { draw_layer_styles } from "./map_styles";
import { hasArea } from 'ol/size';
import { equals } from 'ol/array';
import { warn } from 'ol/console';

var map_controls = new MAP_CONTROLS.Controls([
    MAP_CONTROLS.polygonButton(),
    MAP_CONTROLS.editButton(),
    MAP_CONTROLS.copyButton(),
    MAP_CONTROLS.snapTo(),
    MAP_CONTROLS.remove_button(),
    MAP_CONTROLS.removeAllButton(),
    MAP_CONTROLS.undoButton()
]);

Map.prototype.updateSize = function() {
    const targetElement = this.getTargetElement().getElementsByClassName("ol-viewport")[0];
    
    let size = undefined;
    let heightOffset = 0;
    if (targetElement) {
      const computedStyle = getComputedStyle(targetElement);
      if (getComputedStyle(targetElement)['position'] == "static") {
        // hack to change the height calc, means the point is 4px out at the bottom but best I can do
        heightOffset = 4;
        let elements = targetElement.childNodes
        // if static we need to move anything that's not layers out of the viewport
        for (let i = elements.length - 1; i >= 0; i--) {
          if (!elements[i].classList.contains("ol-layers")) {
            targetElement.parentNode.appendChild(elements[i]);
          }
        }
      } else {
        // else move everything back if it's not where it's supposed to be
        let elements = targetElement.parentNode.childNodes
        for (let i = elements.length - 1; i >= 0; i--) {
          if (!elements[i].classList.contains("ol-viewport")) {
            targetElement.appendChild(elements[i]);
          }
        }
      }
      const width =
        targetElement.offsetWidth -
        parseFloat(computedStyle['borderLeftWidth']) -
        parseFloat(computedStyle['paddingLeft']) -
        parseFloat(computedStyle['paddingRight']) -
        parseFloat(computedStyle['borderRightWidth']);
      const height =
        targetElement.offsetHeight -
        parseFloat(computedStyle['borderTopWidth']) -
        parseFloat(computedStyle['paddingTop']) -
        parseFloat(computedStyle['paddingBottom']) -
        parseFloat(computedStyle['borderBottomWidth']) - heightOffset;
      if (!isNaN(width) && !isNaN(height)) {
        size = [width, height];
        if (
          !hasArea(size) &&
          !!(
            targetElement.offsetWidth ||
            targetElement.offsetHeight ||
            targetElement.getClientRects().length
          )
        ) {
          warn(
            "No map visible because the map container's width or height are 0."
          );
        }
      }
    }

    const oldSize = this.getSize();
    if (size && (!oldSize || !equals(size, oldSize))) {
      this.setSize(size);
      this.updateViewportSize_();
    }
  }

var map = new Map({
    layers: [
        MAP_CONFIG.baseLayer,
        GEOSERVER_CONFIG.boundariesLayer,
        MAP_CONFIG.drawLayer
    ],
    logo: false,
    target: 'map',
    controls: [
        map_controls,
        new Zoom(),
        new ScaleLine(),
        new Attribution({ collapsed: false, collapsible: false })
    ],
    view: new View({
        projection: MAP_CONFIG.projection,
        resolutions: MAP_CONFIG.resolutions,
        center: MAP_CONFIG.defaultCenter,
        zoom: MAP_CONFIG.defaultZoom
    })
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

    map.forEachFeatureAtPixel(pixel, function(feature, layer) {
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
        $('#snap-to-checkbox').removeClass('snap-to-disabled');
    } else {
        if ($('#checkbox').prop('selected')){
            $('#checkbox').trigger('click');
            $('#checkbox').removeAttr('selected');
        }
        SNAP_TO_VECTOR_LAYER.disable();
        COPY_VECTOR_LAYER.disable();
        MAP_CONTROLS.toggleButtons([
            MAP_CONTROLS.copyButtonId,
            MAP_CONTROLS.snapToButtonId
        ], false);
        $('#snap-to-checkbox').addClass('snap-to-disabled');
    }

    if (extentOnMap) {
        MAP_CONTROLS.enableReviewButtons();
    } else {
        MAP_CONTROLS.disableReviewButtons();
    }
});

var addressMarker = new AddressMarker(staticContentUrl)
map.addLayer(addressMarker.addressMarkerLayer);

export { map, addressMarker };
