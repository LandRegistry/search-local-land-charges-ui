def get_mock_extent():
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [-378838.7455502291, 6966202.685233321],
                        [159887.69930341933, 6965138.008464836],
                        [177987.20436767233, 6568013.573819755],
                        [-456560.1496496685, 6562690.189977327],
                        [-378838.7455502291, 6966202.685233321]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }
        ]
    }


def get_multiple_feature_extent():
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [-378838.7455502291, 6966202.685233321],
                        [159887.69930341933, 6965138.008464836],
                        [177987.20436767233, 6568013.573819755],
                        [-456560.1496496685, 6562690.189977327],
                        [-378838.7455502291, 6966202.685233321]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }, {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [-378838.7455502291, 6966202.685233321],
                        [159887.69930341933, 6965138.008464836],
                        [177987.20436767233, 6568013.573819755],
                        [-456560.1496496685, 6562690.189977327],
                        [-378838.7455502291, 6966202.685233321]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }
        ]
    }


pre_union = \
    {
        'type': 'FeatureCollection',
        'features': [
            {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [1, 1],
                        [3, 1],
                        [3, 3],
                        [1, 3],
                        [1, 1]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }, {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [2, 2],
                        [4, 2],
                        [4, 4],
                        [2, 4],
                        [2, 2]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }
        ]
    }

post_union = \
    {
        'type': 'FeatureCollection',
        'features': [
            {
                'geometry': {
                    'type': "Polygon",
                    'coordinates': [[
                        [3.0, 2.0],
                        [3.0, 1.0],
                        [1.0, 1.0],
                        [1.0, 3.0],
                        [2.0, 3.0],
                        [2.0, 4.0],
                        [4.0, 4.0],
                        [4.0, 2.0],
                        [3.0, 2.0]
                    ]]
                },
                'type': "Feature",
                "properties": None
            }
        ]
    }
