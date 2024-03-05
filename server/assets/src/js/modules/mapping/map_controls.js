import { draw_layer_styles } from './map_styles';
import Control from 'ol/control/Control';
import { Draw, Modify, Select }  from 'ol/interaction';
import { Polygon, MultiPolygon } from 'ol/geom';
import { GeoJSON } from 'ol/format';
import Feature from 'ol/Feature';
import union from '@turf/union';
import { staticContentUrl, addAreaText, editAreaText, copyFromMapText,
    deleteAreaText, clearAllText, undoText, snapToMapText, language, undoArrowText } from './set_map_variables'
import { MAP_HELPERS } from "./map_helpers";
import { SNAP_TO_VECTOR_LAYER } from './snap_to_vector_layer';
import { COPY_VECTOR_LAYER } from './copy_vector_layer';
import { MAP_UNDO } from './map_undo';
import { MAP_CONFIG } from './map_config';
import { map } from "./map"

var MAP_CONTROLS = {};

MAP_CONTROLS.polygonButtonId = "map-button-add-area";
MAP_CONTROLS.editButtonId = "map-button-edit";
MAP_CONTROLS.copyButtonId = "map-button-copy";
MAP_CONTROLS.undoButtonId = "map-button-undo";
MAP_CONTROLS.removeAllButtonId = "map-button-clear-all";
MAP_CONTROLS.snapToButtonId = "checkbox";
MAP_CONTROLS.searchButtonId = "searchButton";
MAP_CONTROLS.deleteButtonId = "map-button-delete";

MAP_CONTROLS.currentInteraction = null;
MAP_CONTROLS.currentStyle = draw_layer_styles.NONE;

// Toolbar Of Available Map Controls
MAP_CONTROLS.Controls = function (controls) {
    var container = document.createElement('div');
    var noOfControls = controls.length;

    container.id = "draw-controls";
    container.className = "ol-control";

    for (var i = 0; i < noOfControls; i++) {
        container.appendChild(controls[i]);
    }

    return new Control({
        element: container
    });
};

var ol_ext_inherits = function(child,parent) {
    child.prototype = Object.create(parent.prototype);
    child.prototype.constructor = child;
};

ol_ext_inherits(MAP_CONTROLS.Controls, Control);

function createButton(id, description, isUndo, clickEvent) {
    var button = document.createElement('button');
    button.setAttribute('id', id);
    button.setAttribute('class', id);
    button.setAttribute('aria-label', description);
    button.value = 'button'

    if (isUndo){
        var undoImg = document.createElement('img');
        undoImg.setAttribute('src', staticContentUrl + '/images/mapping/undo.png');
        undoImg.setAttribute('class', 'undo-img');
        undoImg.setAttribute('alt', undoArrowText);
        undoImg.setAttribute('height', '15');
        button.appendChild(undoImg);
        if (language === 'cy'){
            button.setAttribute('class', id + '-welsh')
        }
    }

    var span = document.createElement("span");
    span.textContent = description;
    span.setAttribute('class', 'control-title')
    button.appendChild(span);

    button.addEventListener('click', clickEvent);
    return button
}

// Draw Polygon Button
MAP_CONTROLS.polygonButton = function () {
    return createButton(MAP_CONTROLS.polygonButtonId, addAreaText, false, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Draw polygon button clicked'});

        // Remove the previous interaction
        map.removeInteraction(MAP_CONTROLS.currentInteraction);
        // Toggle the draw control as needed
        var activated = MAP_CONTROLS.toggleActiveControl(MAP_CONTROLS.polygonButtonId);

        if (activated) {
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
    return createButton(MAP_CONTROLS.editButtonId, editAreaText, false, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Edit button clicked'});

        map.removeInteraction(MAP_CONTROLS.currentInteraction);
        var activated = MAP_CONTROLS.toggleActiveControl(MAP_CONTROLS.editButtonId);

        if (activated) {
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
    return createButton(MAP_CONTROLS.removeAllButtonId, clearAllText, false, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Remove all button clicked'});
        MAP_UNDO.storeState();

        MAP_CONFIG.drawSource.clear();
        MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.NONE);
        map.removeInteraction(MAP_CONTROLS.currentInteraction);

        MAP_CONTROLS.currentInteraction = null;

        $('.active-control').removeClass('active-control');

        MAP_CONTROLS.disableReviewButtons();
    });
};

MAP_CONTROLS.undoButton = function () {
    return createButton(MAP_CONTROLS.undoButtonId, undoText, true, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Undo button clicked'});
        MAP_UNDO.undo()
    });
};

MAP_CONTROLS.snapTo = function () {
        var snapDiv = document.createElement('div')
        var snapText = document.createElement('label');
        var checkBox = document.createElement('input');
        snapDiv.setAttribute('class', 'checkbox');
        snapDiv.setAttribute('id', 'snap-to-checkbox');
        //setsup the checkbox
        checkBox.setAttribute('type', 'checkbox');
        checkBox.setAttribute('class', 'snap-checkbox');
        checkBox.setAttribute('id', 'checkbox');
        snapDiv.appendChild(checkBox);
        //sets up the 'snap to text' then adds it to the div
        snapText.setAttribute('class', 'snap-text');
        snapText.setAttribute('for', 'checkbox');
        snapText.innerHTML = snapToMapText;
        snapDiv.appendChild(snapText);

        checkBox.addEventListener('click', function () {
            gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Snap to button clicked'});
            if (!MAP_HELPERS.mapIsPastZoomThreshold(map)) { 
                return
            }
            if (!SNAP_TO_VECTOR_LAYER.enabled) {
                $('#checkbox').attr('selected', 'selected');
                SNAP_TO_VECTOR_LAYER.enable();
                map.addInteraction(SNAP_TO_VECTOR_LAYER.interaction);
            } else {
                $('#checkbox').removeAttr('selected');
                SNAP_TO_VECTOR_LAYER.disable();
                map.removeInteraction(SNAP_TO_VECTOR_LAYER.interaction);
            }
        })

        return snapDiv;
    };

MAP_CONTROLS.copyButton = function () {
    var copyListenerAdded = false
    return createButton(MAP_CONTROLS.copyButtonId, copyFromMapText, false, function () {
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Copy button clicked'});
        //prevent css manipulation to enable buttons
        if (!MAP_HELPERS.mapIsPastZoomThreshold(map)) {
            return
        }

        map.removeInteraction(MAP_CONTROLS.currentInteraction);

        var activated = MAP_CONTROLS.toggleActiveControl(MAP_CONTROLS.copyButtonId);

        if (activated) {
            COPY_VECTOR_LAYER.enable();
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.DRAW);

            MAP_CONTROLS.currentInteraction = COPY_VECTOR_LAYER.interaction;

            // Only add the Copy Button event listener once.
            if (!copyListenerAdded) {
                copyListenerAdded = true
                MAP_CONTROLS.currentInteraction.getFeatures().on('add', function (event) {
                    MAP_UNDO.storeState();
                    var feature = event.target.item(0).clone();
                    if (feature) {
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

            map.addInteraction(MAP_CONTROLS.currentInteraction)
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
    return createButton(MAP_CONTROLS.deleteButtonId, deleteAreaText, false, function(){
        gtag('event', 'Button click', {'eventCategory': 'Map tools', 'eventLabel': 'Delete single polygon button clicked'});
        map.removeInteraction(MAP_CONTROLS.currentInteraction);
        var toggled_on = MAP_CONTROLS.toggleActiveControl(MAP_CONTROLS.deleteButtonId);

        if (toggled_on) {
            MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.REMOVE);

            MAP_CONTROLS.currentInteraction = new Select({
                layers: [MAP_CONFIG.drawLayer]
            });

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

    if(document.getElementById('map-submit')) {
        document.getElementById('map-submit').disabled = true;
    }
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

    if(document.getElementById('map-submit')) {
        document.getElementById('map-submit').disabled = false;
    }
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
    // Also unset active if set and we're disabling the button
    if (!enable && jbutton.hasClass('active-control')) {
        jbutton.removeClass('active-control');
    }
};

// Activate/Deactivate Control
MAP_CONTROLS.toggleActiveControl = function (buttonId) {
    var jbutton = $("#" + buttonId);
    var isActiveControl = jbutton.hasClass('active-control');

    if (isActiveControl) {
        jbutton.removeClass('active-control');
        return false
    } else {
        $('.active-control').removeClass('active-control');
        jbutton.addClass('active-control');
        return true
    }
};

MAP_CONTROLS.remove_selected_feature = function(id) {
    var features = MAP_CONFIG.drawSource.getFeatures();
    var feature = $.grep(features, function(feature) { return feature.getProperties().id == id });
    MAP_CONFIG.drawSource.removeFeature(feature[0])
};

MAP_CONTROLS.removeActiveControl = function(){
    map.removeInteraction(MAP_CONTROLS.currentInteraction);
    $('.active-control').removeClass('active-control');
    COPY_VECTOR_LAYER.disable()
    MAP_CONTROLS.toggleDrawLayerStyle(draw_layer_styles.NONE)
}

export { MAP_CONTROLS }
