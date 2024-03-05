import { GeoJSON } from "ol/format";
import { MAP_CONFIG } from "./map_config";
import { MAP_CONTROLS } from "./map_controls";
import { map } from "./map";
import { draw_layer_styles } from "./map_styles";

function populateGeometries() {
    var geojson = new GeoJSON();
    var features = MAP_CONFIG.drawSource.getFeatures();

    if (features) {
        var options = {
            dataProjection: 'EPSG:27700',
            featureProjection: 'EPSG:27700'
        };

        var featuresJson = geojson.writeFeatures(features, options);
        var hiddenField = document.getElementById('saved-features');

        hiddenField.setAttribute("value", featuresJson);
    }
}

function loadPreviousData(information) {
    if (information) {
        try {
            var options = {
                dataProjection: 'EPSG:27700',
                featureProjection: 'EPSG:27700'
            }

            var feature = new GeoJSON().readFeatures(information, options);
            MAP_CONTROLS.enableReviewButtons();

            MAP_CONFIG.drawSource.addFeatures(feature);
            MAP_CONFIG.drawLayer.setStyle(draw_layer_styles.style[draw_layer_styles.DRAW])

            var extent = feature[0].getGeometry().getExtent().slice(0);

            map.getView().fit(extent, {
                duration: 1000,
                maxZoom: 15
            })

        } catch (e) {
            throw e;
        }
    }
}

export { loadPreviousData, populateGeometries }
