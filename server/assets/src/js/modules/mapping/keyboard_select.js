import { MAP_CONTROLS } from "./map_controls";
import { MAP_CONFIG } from "./map_config";
import { COPY_VECTOR_LAYER } from "./copy_vector_layer";
import { Interaction } from "ol/interaction";
import EventType from 'ol/events/EventType';
import { MultiPolygon } from 'ol/geom';
import { MAP_UNDO } from "./map_undo";

class KeyboardSelect extends Interaction {

    constructor() {
        super();
    }

    setActive(active) {
        super.setActive(active);
        if (this.getMap() != null) {
            if (active) {
                this.addCrosshair(this.getMap());
            } else {
                this.removeCrosshair();
            }
        }
    }

    addCrosshair(map) {
        if (this.crosshairDiv_ == null) {
            var crosshairDiv = document.createElement("div");
            crosshairDiv.className = "crosshair";
            crosshairDiv.id = "crosshair"
            map.getViewport().appendChild(crosshairDiv);
            this.crosshairDiv_ = crosshairDiv
        }
    }

    removeCrosshair() {
        if (this.crosshairDiv_ == null) {
            return;
        }
        this.crosshairDiv_.parentElement.removeChild(this.crosshairDiv_);
        this.crosshairDiv_ = null;
    }

    setMap(map) {
        if (this.getMap() != null) {
            this.removeCrosshair();
        }
        super.setMap(map);
        if (map != null) {
            this.addCrosshair(map);
        }
    }

}

class KeyboardSelectDelete extends KeyboardSelect {
    handleEvent(mapBrowserEvent) {
        let stopEvent = false;
        if (mapBrowserEvent.type == EventType.KEYDOWN) {
            const keyEvent = /** @type {KeyboardEvent} */ (
                mapBrowserEvent.originalEvent
            );
            const key = keyEvent.key;
            if (key == "Enter" || key == " ") {
                const map = mapBrowserEvent.map;
                const view = map.getView();
                MAP_CONFIG.drawLayer.getSource().getFeaturesAtCoordinate(view.getCenter()).forEach(function(feature) {
                    if (feature) {
                        MAP_UNDO.storeState();
                        MAP_CONFIG.drawLayer.getSource().removeFeature(feature);
                        if (MAP_CONFIG.drawSource.getFeatures().length === 0){
                            MAP_CONTROLS.disableReviewButtons();
                        }
                    }
                });
                keyEvent.preventDefault();
                stopEvent = true;
            }
        }
        return !stopEvent;
    }
}

class KeyboardSelectCopy extends KeyboardSelect {
    handleEvent(mapBrowserEvent) {
        let stopEvent = false;
        if (mapBrowserEvent.type == EventType.KEYDOWN) {
            const keyEvent = /** @type {KeyboardEvent} */ (
                mapBrowserEvent.originalEvent
            );
            const key = keyEvent.key;
            if (key == "Enter" || key == " ") {
                const map = mapBrowserEvent.map;
                const view = map.getView();
                if (COPY_VECTOR_LAYER.enabled) {
                    COPY_VECTOR_LAYER.layer.getSource().getFeaturesAtCoordinate(view.getCenter()).forEach(function(feature) {
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
                    });
                }
                keyEvent.preventDefault();
                stopEvent = true;
            }
        }
        return !stopEvent;
    }
}

export { KeyboardSelectDelete, KeyboardSelectCopy };
