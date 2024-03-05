import {Vector as SourceVector} from 'ol/source';
import {Vector as LayerVector} from 'ol/layer';
import {Select} from 'ol/interaction';
import {draw_layer_styles} from './map_styles';
import {GeoJSON} from 'ol/format';
import {bbox} from 'ol/loadingstrategy';
import {wfs_server_url, mastermap_api_key} from './set_map_variables'
import {map} from './map'

var COPY_VECTOR_LAYER = {};

var vectorSource = new SourceVector({
    format: new GeoJSON(),
    url: function(extent) {
        return wfs_server_url + '/' + mastermap_api_key + '/wfs?service=WFS&' +
               'version=1.1.0&request=GetFeature&typename=os.mm.topo.topographicarea&' +
               'outputFormat=application/json&srsname=EPSG:27700&' +
               'bbox=' + extent.join(',')
    },
    strategy: bbox
});

COPY_VECTOR_LAYER.layer = new LayerVector({
    source: vectorSource,
    style: draw_layer_styles.style[draw_layer_styles.HIDDEN]
});

COPY_VECTOR_LAYER.enabled = false;

COPY_VECTOR_LAYER.enable = function() {
    if (!COPY_VECTOR_LAYER.enabled) {
        map.addLayer(COPY_VECTOR_LAYER.layer);
        COPY_VECTOR_LAYER.enabled = true
    }
};

COPY_VECTOR_LAYER.disable = function() {
    map.removeLayer(COPY_VECTOR_LAYER.layer);
    COPY_VECTOR_LAYER.enabled = false;
    map.removeInteraction(COPY_VECTOR_LAYER.interaction);
};

COPY_VECTOR_LAYER.interaction = new Select({
    layers: [COPY_VECTOR_LAYER.layer],
    style: draw_layer_styles.style[draw_layer_styles.HIDDEN]
});

export {COPY_VECTOR_LAYER}
