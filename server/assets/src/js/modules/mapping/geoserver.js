import { Tile } from 'ol/layer';
import { TileWMS } from 'ol/source';
import { MAP_CONFIG } from './map_config';
import { geoserver_url, geoserver_token } from './set_map_variables'

var GEOSERVER_CONFIG = {}

function configureGeoserverLayerForUser(geoserverUrl, geoserverToken) {
    
    GEOSERVER_CONFIG.boundariesLayer = getBoundaryLayer(geoserverUrl, geoserverToken,
    		'authority_boundary_search', MAP_CONFIG.boundaryLayerZindex);
}

function getBoundaryLayer(geoserverUrl, geoserverToken, style, layerZindex) {
    var params = {
        'LAYERS': 'llc:boundaries_organisation_combined',
        'VERSION': '1.1.1',
        'FORMAT': 'image/png',
        'TILED': true,
        'STYLES': style
    };

    var layer = new Tile({
        source: new TileWMS({
            url: geoserverUrl + '/geoserver/llc/' + geoserverToken + '/wms?',
            params: params
        }),
        zIndex: layerZindex
    });

    return layer;
}

configureGeoserverLayerForUser(geoserver_url, geoserver_token);

export {GEOSERVER_CONFIG}
