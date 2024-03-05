import {Style, Stroke} from 'ol/style';
import {Vector as SourceVector} from 'ol/source';
import {Vector as LayerVector} from 'ol/layer';
import {GeoJSON} from 'ol/format';
import {bbox} from 'ol/loadingstrategy';
import {Snap} from 'ol/interaction';
import {wfs_server_url, mastermap_api_key} from './set_map_variables'
import {map} from './map'

var SNAP_TO_VECTOR_LAYER = {};

var vectorSourceLines = new SourceVector({
    format: new GeoJSON(),
    url: function(extent) {
        return wfs_server_url + '/' + mastermap_api_key  + '/wfs?service=WFS&' +
            'version=1.1.0&request=GetFeature&typename=PSMA:os.mm.topo.topographicline,PSMA:os.mm.topo.boundaryline&' +
            'outputFormat=application/json&srsname=EPSG:27700&' +
            'bbox=' + extent.join(',')
    },
    strategy: bbox
});

SNAP_TO_VECTOR_LAYER.layer = new LayerVector({
    source: vectorSourceLines,
    style: new Style({
        stroke: new Stroke({
            color: 'rgba(0, 0, 255, 0)',
            width: 1
        })
    })
});

SNAP_TO_VECTOR_LAYER.enabled = false

SNAP_TO_VECTOR_LAYER.enable = function() {
    if (!SNAP_TO_VECTOR_LAYER.enabled) {
        map.addLayer(SNAP_TO_VECTOR_LAYER.layer);
        SNAP_TO_VECTOR_LAYER.enabled = true;
    }
};

SNAP_TO_VECTOR_LAYER.disable = function() {
    if(SNAP_TO_VECTOR_LAYER.enabled){
        map.removeLayer(SNAP_TO_VECTOR_LAYER.layer);
        SNAP_TO_VECTOR_LAYER.enabled = false
    }
};

SNAP_TO_VECTOR_LAYER.interaction = new Snap({
    source: SNAP_TO_VECTOR_LAYER.layer.getSource(),
    edge: true,
    vertex: true,
    pixelTolerance: 7.5
});

export {SNAP_TO_VECTOR_LAYER}