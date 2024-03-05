import {register} from 'ol/proj/proj4';
import {get} from 'ol/proj'
import {default as proj4} from 'proj4';
import {Collection} from 'ol';
import {Vector as SourceVector, TileImage} from 'ol/source';
import {Vector as LayerVector, Tile} from 'ol/layer';
import {draw_layer_styles} from './map_styles';
import TileGrid from 'ol/tilegrid/TileGrid';
import {mastermap_api_key, map_base_layer_view_name, wmts_server_url} from './set_map_variables'

// Define British National Grid Projection - we'll use this to convert points to/from OpenLayers ESPG:3857 Format
proj4.defs('EPSG:27700', '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 ' +
    '+x_0=400000 +y_0=-100000 +ellps=airy ' +
    '+towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 ' +
    '+units=m +no_defs');
register(proj4);

var MAP_CONFIG = {};

(function (MAP_CONFIG) {
    // Map Default Position
    MAP_CONFIG.defaultCenter = [385727.58, 335143.72];
    MAP_CONFIG.defaultZoom = 0;
    MAP_CONFIG.drawControlsZoomThreshold = 13;
    MAP_CONFIG.maxZoomLevel = 15;

    MAP_CONFIG.baseLayerZindex = 0;
    MAP_CONFIG.boundaryLayerZindex = 1;
    MAP_CONFIG.nonMigratedLayerZindex = 2;
    MAP_CONFIG.drawLayerZindex = 3;

    // Draw Source
    MAP_CONFIG.drawFeatures = new Collection();
    MAP_CONFIG.drawSource = new SourceVector({
        features: MAP_CONFIG.drawFeatures
    });
    MAP_CONFIG.drawLayer = new LayerVector({
        source: MAP_CONFIG.drawSource,
        style: draw_layer_styles.style[draw_layer_styles.NONE],
        zIndex: MAP_CONFIG.drawLayerZindex
    });
    MAP_CONFIG.projection = get('EPSG:27700');
    // Fixed resolutions to display the map at (pixels per ground unit (meters when
    // the projection is British National Grid))
    MAP_CONFIG.resolutions = [
        //res level scale
        2800.0000, // 0 10000000.0
        1400.0000, // 1 5000000.0
        700.0000, // 2 2500000.0
        280.0000, // 3 1000000.0
        140.0000, // 4 500000.0
        70.0000, // 5 250000.0
        28.0000, // 6 100000.0
        21.0000, // 7 75000.0
        14.0000, // 8 50000.0
        7.0000, // 9 25000.0
        2.8000, // 10 10000.0
        1.4000, // 11 5000.0
        0.7000, // 12 2500.0
        0.3500, // 13 1250.0
        0.1750, // 14 625.0
        0.0875 // 15 312.5
    ];

    MAP_CONFIG.baseLayer = undefined;

    MAP_CONFIG.setBaseLayer = function (zIndex, res, proj) {
        // Extent of the map in units of the projection (these match our base map)
        var extent = [0, 0, 700000, 1300000];
        proj = get('EPSG:27700');
        proj.setExtent(extent);

        MAP_CONFIG.baseLayer = new Tile({
            extent: extent,
            opacity: 1.0,
            source: new TileImage({
                attributions: null,
                crossOrigin: null,
                projection: proj,
                tileGrid: new TileGrid({
                    origin: [extent[0], extent[1]],
                    resolutions: res
                }),
                tileUrlFunction: function (tileCoord, pixelRatio, projection) {
                    if (!tileCoord) {
                        return "";
                    }

                    var x = tileCoord[1];
                    var y = -1 - tileCoord[2];
                    var z = tileCoord[0];

                    if (x < 0 || y < 0) {
                        return "";
                    }

                    var url = wmts_server_url + '/' + mastermap_api_key + '/' + map_base_layer_view_name + '/' + z + '/' + x + '/' + y + '.png';
                    return url;
                }
            }),
            zIndex: zIndex
        });
    };
})(MAP_CONFIG);

MAP_CONFIG.setBaseLayer(MAP_CONFIG.baseLayerZindex, MAP_CONFIG.resolutions, MAP_CONFIG.projection);

export {MAP_CONFIG}
