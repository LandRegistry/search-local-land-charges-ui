var mapVarElement = document.getElementById('mapping-variables')
var mapping_variables = JSON.parse(mapVarElement.innerHTML)

var staticContentUrl = mapping_variables['staticContentUrl'];
var mastermap_api_key = mapping_variables['mastermap_api_key'];
var map_base_layer_view_name = mapping_variables['map_base_layer_view_name'];
var wfs_server_url = mapping_variables['wfs_server_url'];
var wmts_server_url = mapping_variables['wmts_server_url'];
var geoserver_url = mapping_variables['geoserver_url'];
var geoserver_token = mapping_variables['geoserver_token'];

export {staticContentUrl, mastermap_api_key, map_base_layer_view_name, wfs_server_url,
    wmts_server_url, geoserver_url, geoserver_token}
