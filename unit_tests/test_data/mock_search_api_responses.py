from unit_tests.test_data.mock_land_charge import mock_land_charge


def mock_charges_response():
    charge = mock_land_charge()

    return [
        {
            "geometry": charge.get("geometry"),
            "type": charge.get("charge-type"),
            "item": charge,
        },
        {
            "geometry": charge.get("geometry"),
            "type": charge.get("charge-type"),
            "item": charge,
        },
    ]
