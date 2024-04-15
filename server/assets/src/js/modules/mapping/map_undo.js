import { GeoJSON } from "ol/format";
import { MAP_CONTROLS } from "./map_controls";
import { MAP_CONFIG } from "./map_config";

var MAP_UNDO = {};

MAP_UNDO.currentState = null;
MAP_UNDO.undoStack = [];
MAP_UNDO.drawing = false

MAP_UNDO.storeState = function() {
    MAP_UNDO.undoStack.push(MAP_UNDO.getGeometries());
    // Limit growth of undo stack [AC3]
    if(MAP_UNDO.undoStack.length > 10) {
        MAP_UNDO.undoStack = MAP_UNDO.undoStack.slice(MAP_UNDO.undoStack.length - 10)
    }
    MAP_UNDO.enableUndoButton(true);
};

MAP_UNDO.enableUndoButton = function(enable) {
    if(document.getElementById(MAP_CONTROLS.undoButtonId)){
        document.getElementById(MAP_CONTROLS.undoButtonId).disabled = !enable;
    }
};

MAP_UNDO.undo = function () {
    if (MAP_UNDO.drawing) {
        MAP_UNDO.openlayersUndo();
    } else {
        MAP_UNDO.removeUndo();
    }
};

MAP_UNDO.openlayersUndo = function() {
    MAP_CONTROLS.currentInteraction.removeLastPoint();
};

MAP_UNDO.removeUndo = function() {
    if(MAP_UNDO.undoStack.length > 0){
        MAP_UNDO.putGeometries(MAP_UNDO.undoStack.pop());
    }

    if (MAP_CONFIG.drawSource.getFeatures().length === 0){
        MAP_CONTROLS.disableReviewButtons();
    } else {
        MAP_CONTROLS.enableReviewButtons();
    }
};

MAP_UNDO.getGeometries = function() {
    var geojson = new GeoJSON();
    var features = MAP_CONFIG.drawSource.getFeatures();

    var options = {
        dataProjection: 'EPSG:27700',
        featureProjection: 'EPSG:27700'
    };

    var featuresJson = geojson.writeFeatures(features, options);
    return featuresJson;
};

MAP_UNDO.putGeometries = function(geometry) {
    var options = {
        dataProjection: 'EPSG:27700',
        featureProjection: 'EPSG:27700'
    };

    MAP_CONFIG.drawSource.clear();
    var features = new GeoJSON().readFeatures(geometry, options);

    MAP_CONFIG.drawSource.addFeatures(features);
};

export {MAP_UNDO};
