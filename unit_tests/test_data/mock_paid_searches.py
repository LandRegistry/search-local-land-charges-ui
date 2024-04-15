mock_valid_paid_search = {
    "search-id": 2,
    "search-extent": {
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [293229.16874999995, 93577.13750000001],
                            [293240.98124999995, 93551.32500000001],
                            [293267.31875, 93569.7875],
                            [293229.16874999995, 93577.13750000001],
                        ]
                    ],
                },
                "properties": {"id": 1520344387395},
            }
        ],
        "type": "FeatureCollection",
    },
    "user-id": "533724bd-0a9a-4f2d-9cb6-2496792ca026",
    "document-url": "http://storage-api:8080/v1.0/storage/llc1/5f589cd7-ba59-4f8a-8ff7-202e8290cf52",
    "search-date": "2018-03-01T13:54:25.987113",
    "payment-id": "some id",
    "lapsed-date": None,
    "charges": [],
}

mock_valid_search_with_repeats = {
    "search-id": 3,
    "search-extent": {
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [293229.16874999995, 93577.13750000001],
                            [293240.98124999995, 93551.32500000001],
                            [293267.31875, 93569.7875],
                            [293229.16874999995, 93577.13750000001],
                        ]
                    ],
                },
                "properties": {"id": 1520344387395},
            }
        ],
        "type": "FeatureCollection",
    },
    "user-id": "533724bd-0a9a-4f2d-9cb6-2496792ca026",
    "document-url": "http://storage-api:8080/v1.0/storage/llc1/5f589cd7-ba59-4f8a-8ff7-202e8290cf52",
    "search-date": "2018-03-01T13:54:25.987113",
    "payment-id": "some id",
    "lapsed-date": None,
    "charges": [],
    "repeat_searches": [mock_valid_paid_search],
}

mock_lapsed_searches = [
    {
        "search-id": 4,
        "search-extent": {
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [293229.16874999995, 93577.13750000001],
                                [293240.98124999995, 93551.32500000001],
                                [293267.31875, 93569.7875],
                                [293229.16874999995, 93577.13750000001],
                            ]
                        ],
                    },
                    "properties": {"id": 1520344387395},
                }
            ],
            "type": "FeatureCollection",
        },
        "user-id": "533724bd-0a9a-4f2d-9cb6-2496792ca026",
        "document-url": "http://storage-api:8080/v1.0/storage/llc1/5f589cd7-ba59-4f8a-8ff7-202e8290cf52",
        "search-date": "2018-03-01T13:54:25.987113",
        "lapsed-date": "2018-03-01T13:54:25.987113",
        "payment-id": "some id",
        "charges": [],
    }
]
