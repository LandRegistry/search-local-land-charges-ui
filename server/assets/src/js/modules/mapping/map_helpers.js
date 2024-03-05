import { linear } from 'ol/easing';
import { GeoJSON } from 'ol/format';
import { boundingExtent as olBoundingExtent } from 'ol/extent';
import { MAP_CONFIG } from './map_config';
import { map, addressMarker } from './map';

var MAP_HELPERS = {};

(function(MAP_HELPERS) {
    MAP_HELPERS.getZoomLevel = function(map) {
        return Math.round(map.getView().getZoom());
    };

    MAP_HELPERS.mapIsPastZoomThreshold = function(map) {
        return MAP_HELPERS.getZoomLevel(map) >= MAP_CONFIG.drawControlsZoomThreshold;
    };

    MAP_HELPERS.zoomToBoundary = function() {
        var extent = new olBoundingExtent([[137738.0354,383.7986],[633717.1256,669903.6353]]);
        map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: linear});
    };

    MAP_HELPERS.zoom_to_authority_boundary = function(local_authority_boundary_url) {
        $.getJSON(local_authority_boundary_url)
            .done(function(json){
                var geojson = new GeoJSON();
                var feature = geojson.readFeature(json);
                var extent = feature.getGeometry().getExtent();
                map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: linear});
            })
            .fail(function(json) {
                var extent = new olBoundingExtent([[137738.0354,383.7986],[633717.1256,669903.6353]]);
                map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: linear});
            });
    };

    MAP_HELPERS.zoomToPreviousExtent = function(searchExtent) {
        if (searchExtent) {
            try {
                var options = {
                    dataProjection: 'EPSG:27700',
                    featureProjection: 'EPSG:27700'
                };

                var features = new GeoJSON().readFeatures(searchExtent, options);
                var zoomExtent = features[0].getGeometry().getExtent();
                map.getView().fit(zoomExtent);
            } catch (e) {
                windowLocationReplace('/error');
            }
        }
    };

    MAP_HELPERS.zoomToLocation = function (coordinates, coordinateSearch) {
        if (coordinates) {
            if (coordinateSearch) {
                addressMarker.markCoordinates(coordinates);
                var coordinates = [coordinates]
            }

            var boundingExtent = new olBoundingExtent(coordinates)
            map.getView().fit(boundingExtent, {duration: 1000, maxZoom: 15})
        }
    };

})(MAP_HELPERS);

export {MAP_HELPERS};
