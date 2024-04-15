import $ from "jquery";
import { draw_layer_styles } from './map_styles';
import Control from 'ol/control/Control';
import { Draw, Modify, Select }  from 'ol/interaction';
import { Polygon, MultiPolygon } from 'ol/geom';
import { GeoJSON } from 'ol/format';
import Feature from 'ol/Feature';
import union from '@turf/union';
import { MAP_HELPERS } from "./map_helpers";
import { SNAP_TO_VECTOR_LAYER } from './snap_to_vector_layer';
import { COPY_VECTOR_LAYER } from './copy_vector_layer';
import { MAP_UNDO } from './map_undo';
import { MAP_CONFIG } from './map_config';
import { map } from "./map"
import { KeyboardSelectDelete, KeyboardSelectCopy } from "./keyboard_select";

var MAP_CONTROLS = {};

MAP_CONTROLS.controlContainer = "map-options_container";
MAP_CONTROLS.polygonButtonId = "map-options_draw-area";
MAP_CONTROLS.editButtonId = "map-options_edit-area";
MAP_CONTROLS.copyButtonId = "map-options_select-area";
MAP_CONTROLS.undoButtonId = "map-options_undo";
MAP_CONTROLS.removeAllButtonId = "map-options_clear-all";
MAP_CONTROLS.snapToButtonId = "map-options_snap-to";
MAP_CONTROLS.searchButtonId = "searchButton";
MAP_CONTROLS.deleteButtonId = "map-options_delete-area";

MAP_CONTROLS.currentInteraction = null;
MAP_CONTROLS.hoverInteraction = null;
MAP_CONTROLS.keyboardInteraction = null;

MAP_CONTROLS.currentStyle = draw_layer_styles.NONE;

function bindButtonEvent(id, clickEvent) {
    var button = document.getElementById(id);
    if (button != null) {
        button.addEventListener('click', clickEvent);
    }
    return button
}

// Draw Polygon Button
MAP_CONTROLS.polygonButton = function () {
    return bindButtonEvent(MAP_CONTROLS.polygonButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Draw polygon button clicked'});

        // Remove the previous interaction
        MAP_CONTROLS.removeActiveControl();
        // Toggle the draw control as needed
        var checked = $('#' + MAP_CONTROLS.polygonButtonId).attr('checked');

        if (!checked) {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.DRAW);

            MAP_CONTROLS.currentInteraction = new Draw({
                features: MAP_CONFIG.drawFeatures,
                type: "Polygon",
                style: draw_layer_styles.style[draw_layer_styles.DRAW],
                geometryFunction: function (coords, geometry) {
                    if (!geometry) {
                        geometry = new Polygon([]);
                    }
                    geometry.setCoordinates([coords[0].concat([coords[0][0]])]);
                    MAP_CONTROLS.toggleButton(MAP_CONTROLS.undoButtonId, coords[0].length > 1);
                    MAP_UNDO.drawing = coords[0].length > 1;
                    return geometry;
                }
            });

            MAP_CONTROLS.currentInteraction.on('drawstart', function(event) {
                MAP_UNDO.storeState();
            });

            MAP_CONTROLS.currentInteraction.on('drawend', function (event) {
                event.feature.setProperties({
                    'id': Date.now()
                });
                MAP_UNDO.drawing = false;
                MAP_CONTROLS.enableReviewButtons();
            });

            map.addInteraction(MAP_CONTROLS.currentInteraction);

            if(SNAP_TO_VECTOR_LAYER.enabled){
                map.addInteraction(SNAP_TO_VECTOR_LAYER.interaction);
            }
        }
    });
};

// Edit Features Button
MAP_CONTROLS.editButton = function () {
    return bindButtonEvent(MAP_CONTROLS.editButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Edit button clicked'});

        MAP_CONTROLS.removeActiveControl();
        var checked = $('#' + MAP_CONTROLS.editButtonId).attr('checked');

        if (!checked) {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.EDIT);

            MAP_CONTROLS.currentInteraction = new Modify({
                features: MAP_CONFIG.drawFeatures,
                style: draw_layer_styles.style[draw_layer_styles.EDIT]
            });

            map.addInteraction(MAP_CONTROLS.currentInteraction);

            MAP_CONTROLS.currentInteraction.on('modifystart', function (event) {
                MAP_UNDO.storeState();
            });

            if(SNAP_TO_VECTOR_LAYER.enabled){
                map.addInteraction(SNAP_TO_VECTOR_LAYER.interaction);
            }
        } else {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.NONE);
        }
    });
};

// Remove all button
MAP_CONTROLS.removeAllButton = function () {
    return bindButtonEvent(MAP_CONTROLS.removeAllButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Remove all button clicked'});
        MAP_UNDO.storeState();
        MAP_CONFIG.drawSource.clear();
        MAP_CONTROLS.disableReviewButtons();
    });
};

MAP_CONTROLS.undoButton = function () {
    return bindButtonEvent(MAP_CONTROLS.undoButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Undo button clicked'});
        MAP_UNDO.undo()
    });
};

MAP_CONTROLS.snapTo = function () {
    return bindButtonEvent(MAP_CONTROLS.snapToButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Snap to button clicked'});
        if (!MAP_HELPERS.mapIsPastZoomThreshold(map)) { 
            return
        }
        if (!SNAP_TO_VECTOR_LAYER.enabled) {
            SNAP_TO_VECTOR_LAYER.enable();
        } else {
            SNAP_TO_VECTOR_LAYER.disable();
        }
    });
};

MAP_CONTROLS.copyButton = function () {
    var copyListenerAdded = false
    return bindButtonEvent(MAP_CONTROLS.copyButtonId, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Copy button clicked'});
        //prevent css manipulation to enable buttons
        if (!MAP_HELPERS.mapIsPastZoomThreshold(map)) {
            return
        }

        MAP_CONTROLS.removeActiveControl();

        var checked = $('#' + MAP_CONTROLS.copyButtonId).attr('checked');

        if (!checked) {
            COPY_VECTOR_LAYER.enable();
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.DRAW);

            MAP_CONTROLS.currentInteraction = COPY_VECTOR_LAYER.interaction;
            MAP_CONTROLS.hoverInteraction = COPY_VECTOR_LAYER.hoverInteraction;
            MAP_CONTROLS.keyboardInteraction = new KeyboardSelectCopy(map);

            // Only add the Copy Button event listener once.
            if (!copyListenerAdded) {
                copyListenerAdded = true
                MAP_CONTROLS.currentInteraction.getFeatures().on('add', function (event) {
                    var feature = event.target.item(0).clone();
                    if (feature) {
                        MAP_UNDO.storeState();
                        var geometry = feature.getGeometry();
                        //Convert multi polygons to features
                        if (geometry instanceof MultiPolygon) {
                            geometry.getPolygons().forEach(function(geometry) {
                                MAP_CONTROLS.addGeometryToMap(geometry)
                            });
                        } else {
                            MAP_CONTROLS.addGeometryToMap(geometry);
                        }
                        MAP_CONTROLS.enableReviewButtons();
                    }
                    COPY_VECTOR_LAYER.interaction.getFeatures().clear();
                });
            }
            map.addInteraction(MAP_CONTROLS.currentInteraction);
            map.addInteraction(MAP_CONTROLS.hoverInteraction);
            map.addInteraction(MAP_CONTROLS.keyboardInteraction);
        } else {
            COPY_VECTOR_LAYER.disable()
        }
    });
};

MAP_CONTROLS.addGeometryToMap = function(geometry) {
    // Convert geometry into geojson as union function requires geojson
    let geoJsontoAdd = JSON.parse(new GeoJSON().writeGeometry(geometry));

    let featuresToRemove = [];

    MAP_CONFIG.drawSource.getFeatures().forEach(function(feature) {
        let currentGeoJson = JSON.parse(new GeoJSON().writeGeometry(feature.getGeometry()));
  
        let mergedGeoJSON = union(currentGeoJson, geoJsontoAdd);
        /* If adjecent returns a feature with a polygon
           Else returns a feature with a multi polygon */
  
        if (mergedGeoJSON.geometry.type === 'Polygon') {
            geoJsontoAdd = mergedGeoJSON.geometry;
            featuresToRemove.push(feature);
        }
    })
  
    featuresToRemove.forEach(function(feature) {
        MAP_CONFIG.drawSource.removeFeature(feature)
    })

    let newFeature = new Feature({
        geometry: new GeoJSON().readGeometry(geoJsontoAdd)
    });
    newFeature.setProperties({
        'id': Date.now()
    });
  
    MAP_CONFIG.drawSource.addFeature(newFeature);
}

// Remove Features Button
MAP_CONTROLS.remove_button = function() {
    return bindButtonEvent(MAP_CONTROLS.deleteButtonId, function(){
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Delete single polygon button clicked'});
        MAP_CONTROLS.removeActiveControl();
        var checked = $('#' + MAP_CONTROLS.deleteButtonId).attr('checked');

        if (!checked) {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.REMOVE);

            MAP_CONTROLS.currentInteraction = new Select({
                layers: [MAP_CONFIG.drawLayer]
            });
            MAP_CONTROLS.keyboardInteraction = new KeyboardSelectDelete(map);

            MAP_CONTROLS.currentInteraction.getFeatures().on('add', function (event) {
                MAP_UNDO.storeState();
                var feature_id = event.element.getProperties().id;

                MAP_CONTROLS.remove_selected_feature(feature_id);
                MAP_CONTROLS.currentInteraction.getFeatures().clear();

                if (MAP_CONFIG.drawSource.getFeatures().length === 0){
                    MAP_CONTROLS.disableReviewButtons();
                }
            });

            map.addInteraction(MAP_CONTROLS.currentInteraction)
            map.addInteraction(MAP_CONTROLS.keyboardInteraction)
        } else {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.NONE)
        }
    })
};

// When no extent has been drawn and the only controls that should be available are polygon/copy/snap-to
MAP_CONTROLS.disableReviewButtons = function () {
    MAP_CONTROLS.toggleButtons([
        MAP_CONTROLS.editButtonId,
        MAP_CONTROLS.removeAllButtonId,
        MAP_CONTROLS.searchButtonId,
        MAP_CONTROLS.deleteButtonId
    ], false);
    MAP_UNDO.enableUndoButton(MAP_UNDO.undoStack.length > 0);
};

// When an extent has been drawn enable the edit/remove/search controls, and submit button
MAP_CONTROLS.enableReviewButtons = function () {
    MAP_CONTROLS.toggleButtons([
        MAP_CONTROLS.editButtonId,
        MAP_CONTROLS.removeAllButtonId,
        MAP_CONTROLS.searchButtonId,
        MAP_CONTROLS.deleteButtonId
    ], true);
    MAP_UNDO.enableUndoButton(MAP_UNDO.undoStack.length > 0);
};

// Toggle Feature Styles on draw layer for current style
MAP_CONTROLS.toggleDrawLayerStyle = function (style) {
    MAP_CONTROLS.currentStyle = style;
    MAP_CONFIG.drawLayer.setStyle(draw_layer_styles.style[style]);
};

// Toggle an array of buttons as enabled/disabled
MAP_CONTROLS.toggleButtons = function (buttonIds, enable) {
    for (var i = 0; i < buttonIds.length; i++) {
        MAP_CONTROLS.toggleButton(buttonIds[i], enable);
    }
};

// Toggle a button as enabled/disabled
MAP_CONTROLS.toggleButton = function (buttonId, enable) {
    var jbutton = $("#" + buttonId)
    jbutton.prop('disabled', !enable);
    // Also unset checked if set and we're disabling the button
    if (!enable) {
        // if disabling the active mode then remove active control
        if (jbutton.prop('checked') && jbutton.is(':radio')) {
            MAP_CONTROLS.removeActiveControl();
        }
        jbutton.prop('checked', false);
    }
};

MAP_CONTROLS.remove_selected_feature = function(id) {
    var features = MAP_CONFIG.drawSource.getFeatures();
    var feature = $.grep(features, function(feature) { return feature.getProperties().id == id });
    MAP_CONFIG.drawSource.removeFeature(feature[0])
};

MAP_CONTROLS.removeActiveControl = function(){
    if (MAP_CONTROLS.currentInteraction != null) {
        map.removeInteraction(MAP_CONTROLS.currentInteraction);
        MAP_CONTROLS.currentInteraction = null;
    }
    if (MAP_CONTROLS.hoverInteraction != null) {
        map.removeInteraction(MAP_CONTROLS.hoverInteraction);
        MAP_CONTROLS.hoverInteraction = null;
    }
    if (MAP_CONTROLS.keyboardInteraction != null) {
        map.removeInteraction(MAP_CONTROLS.keyboardInteraction);
        MAP_CONTROLS.keyboardInteraction = null;
    }
    MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.NONE);
}

export { MAP_CONTROLS }
