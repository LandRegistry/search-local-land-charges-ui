import {Style, Stroke, Circle, Fill} from 'ol/style';

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
    // Associated Feature Styles for mode
    style: {
        0: new Style({
            fill: new Fill({
                color: [6, 88, 229, 0.1]
            }),
            stroke: new Stroke({
                color: '#0658e5',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: '#0658e5'
                })
            })
        }),
        1: new Style({
            fill: new Fill({
                color: [244, 203, 66, 0.3]
            }),
            stroke: new Stroke({
                color: '#ffcc33',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: '#ffcc33'
                })
            })
        }),
        2: new Style({
            stroke: new Stroke({
                color: [255,0,0,0.4],
                width: 2,
                lineDash: [1, 5]
            }),
            fill: new Fill({
                color: [255,0,0,0.2]
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: '#ff0000'
                })
            }),
            zIndex: 1
        }),
        3: new Style({
            fill: new Fill({
                color: [6, 88, 229, 0.1]
            }),
            stroke: new Stroke({
                color: '#0658e5',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new Circle({
                radius: 5,
                fill: new Fill({
                    color: '#0658e5'
                })
            })
        }),
        4: new Style({
            stroke: new Stroke({
                color: 'rgba(0, 0, 255, 0)',
                width: 1
            }),
            fill: new Fill({
                color: 'rgba(0, 0, 255, 0)'
            })
        })
    }
}

export {draw_layer_styles}
