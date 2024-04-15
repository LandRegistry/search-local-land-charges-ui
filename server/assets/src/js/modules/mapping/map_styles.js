import { Style, Stroke, Circle, Fill } from 'ol/style';
import { MultiPoint } from 'ol/geom';

var add_colour = '#1d70b8';
var edit_colour = '#00703c';
var delete_colour = '#d4351c';

var add_fill = [29, 112, 184, 0.2];
var edit_fill = [0, 112, 60, 0.2];
var delete_fill = [212, 53, 28, 0.2];

var fill_none = new Fill();
fill_none.setColor([29, 112, 184, 0.1]);

var draw_layer_styles = {
    // Draw Interactions
    DRAW: 0,
    // Edit Interactions
    EDIT: 1,
    // Remove Interactions
    REMOVE: 2,
    // No Interactions Toggled
    NONE: 3,
    // Hidden
    HIDDEN: 4,
    // Hover
    HOVER: 5,
    // Associated Feature Styles for mode
    style: {
        // DRAW | add
        0: new Style({
            fill: new Fill({
                color: add_fill
            }),
            stroke: new Stroke({
                color: add_colour,
                width: 2
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: add_colour
                })
            })
        }),
        // EDIT
        1: [new Style({
            fill: new Fill({
                color: edit_fill
            }),
            stroke: new Stroke({
                color: edit_colour,
                width: 2
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: edit_colour
                })
            })
        }),
        new Style({ // second style for the dots on the edge
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: edit_colour
                })
            }),
            geometry: function (feature) { // creating a custom geometry to draw points on
                var coordinates = feature.getGeometry().getCoordinates()[0];
                if (Array.isArray(coordinates)) {
                    return new MultiPoint(coordinates);
                }
            }
        })],
        // delete | remove
        2: new Style({
            stroke: new Stroke({
                color: delete_colour,
                width: 2
            }),
            fill: new Fill({
                color: delete_fill
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: delete_colour
                })
            }),
            zIndex: 1
        }),
        // NONE
        3: new Style({
            fill: new Fill({
                color: [6, 88, 229, 0.1]
            }),
            stroke: new Stroke({
                color: '#0658e5',
                width: 2
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: '#0658e5'
                })
            })
        }),
        // HIDDEN
        4: new Style({
            stroke: new Stroke({
                color: 'rgba(0, 0, 255, 0)',
                width: 1
            }),
            fill: new Fill({
                color: 'rgba(0, 0, 255, 0)'
            })
        }),
        // HOVER
        5: new Style({
            fill: new Fill({
                color: 'rgba(0,48,120,0.3)'
            }),
            stroke: new Stroke({
                color: 'rgba(0,48,120,1)',
                width: 2
            }),
            radius: 5
        }),
    }
}

export { draw_layer_styles }
