import {Style, Icon} from 'ol/style';
import {Vector as SourceVector} from 'ol/source';
import {Vector as LayerVector} from 'ol/layer';
import {GeoJSON} from 'ol/format';

class AddressMarker {

    constructor(staticContentPath) {

        var self = this;

        self.staticContentPath = staticContentPath;

        self.addressMarkerSource = new SourceVector({});

        self.addressMarkerLayer = new LayerVector({
            source: this.addressMarkerSource
        });

        self.addressMarkerStyle = new Style({
            image: new Icon(({
                src: self.staticContentPath + '/images/mapping/icon-locator.png',
                anchor: [0.5, 1]
            }))
        });

        self.markCoordinates = function (coordinates) {
            var geometry = {
                'type': 'Point',
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:27700'
                    }
                },
                'coordinates': coordinates
            };
            self.markGeometry(geometry);
        };

        self.markGeometry = function (geometry) {
            self.addressMarkerSource.clear();

            var geoJson = {
                'type': 'Feature',
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:27700'
                    }
                },
                'geometry': geometry
            };

            var options = {
                'dataProjection': 'EPSG:27700',
                'featureProjection': 'EPSG:27700'
            };

            var pin = (new GeoJSON()).readFeature(geoJson, options);
            pin.setStyle(self.addressMarkerStyle);

            self.addressMarkerSource.addFeature(pin);
        };
    }
}
    
export {AddressMarker}
