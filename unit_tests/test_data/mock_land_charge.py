
extent = {
    "features": [
        {"geometry": {
            "coordinates": [291574.80499999993, 91961.04499999997], "type": "Point"},
            "properties": {"id": 600},
            "crs": {
                "properties": {"name": "urn:ogc:def:crs:EPSG::27700"},
                "type": "name"},
            "type": "Feature"}],
    "type": "FeatureCollection"
}

charge_address = {
    "line-1": "Butternut Uk Limited",
    "line-2": "15 Guildhall Shopping Centre",
    "line-3": "Queen Street",
    "line-4": "Exeter",
    "line-5": "",
    "line-6": "",
    "postcode": "EX4 3HW",
    "unique-property-reference-number": 10023122962
}


def mock_land_charge():
    return {
        'local-land-charge': 123,
        'registration-date': '2011-01-01',
        'originating-authority-charge-identifier': 'an identifier',
        'charge-type': 'a charge type',
        'charge-geographic-description': 'a description',
        'charge-creation-date': '2011-01-01',
        'instrument': 'An instrument',
        'statutory-provision': 'a provision',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'unique-property-reference-numbers': [123, 456],
        'old-register-part': '1a',
        'originating-authority': 'an authority',
        'migrating-authority': 'another authority',
        'migration-supplier': 'a supplier',
        'expiry-date': '2011-01-01',
        'end-date': '2011-01-01',
        'start-date': '2011-01-01',
        'adjoining': False
    }


def mock_paid_land_charge():
    return {
        'local-land-charge': 123,
        'display-id': 'LLC-3Z',
        'geometry': 'Not provided',
        'charge-type': 'a charge type',
        'charge-sub-category': 'Not provided',
        'supplementary-information': 'Not provided',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'originating-authority': 'an authority',
        'charge-creation-date': '2011-01-01',
        'registration-date': '2011-01-01',
        'charge-geographic-description': 'a description',
        'legal-document': 'An instrument',
        'law': 'a provision',
        'adjoining': False
    }


def mock_land_compensation_charge():
    return {
        'local-land-charge': 123,
        'registration-date': '2011-01-01',
        'originating-authority-charge-identifier': 'an identifier',
        'charge-type': 'Land compensation',
        'charge-geographic-description': 'a description',
        'charge-creation-date': '2011-01-01',
        'instrument': 'An instrument',
        'statutory-provision': 'a provision',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'unique-property-reference-numbers': [123, 456],
        'old-register-part': '1a',
        'originating-authority': 'an authority',
        'migrating-authority': 'another authority',
        'migration-supplier': 'a supplier',
        'expiry-date': '2011-01-01',
        'end-date': '2011-01-01',
        'start-date': '2011-01-01',
        'land-sold-description': '10',
        'land-works-particulars': '21',
        'adjoining': False
    }


def mock_paid_land_compensation_charge():
    return {
        'local-land-charge': 123,
        'display-id': 'LLC-3Z',
        'geometry': 'Not provided',
        'charge-type': 'Land compensation',
        'charge-sub-category': 'Not provided',
        'supplementary-information': 'Not provided',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'originating-authority': 'an authority',
        'charge-creation-date': '2011-01-01',
        'registration-date': '2011-01-01',
        'charge-geographic-description': 'a description',
        'land-sold-description': '10',
        'land-works-particulars': '21',
        'legal-document': 'An instrument',
        'law': 'a provision',
        'adjoining': False
    }


def mock_financial_charge():
    return {
        'local-land-charge': 123,
        'registration-date': '2011-01-01',
        'originating-authority-charge-identifier': 'an identifier',
        'charge-type': 'Financial',
        'charge-geographic-description': 'a description',
        'charge-creation-date': '2011-01-01',
        'instrument': 'An instrument',
        'statutory-provision': 'a provision',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'unique-property-reference-numbers': [123, 456],
        'old-register-part': '1a',
        'originating-authority': 'an authority',
        'migrating-authority': 'another authority',
        'migration-supplier': 'a supplier',
        'expiry-date': '2011-01-01',
        'end-date': '2011-01-01',
        'start-date': '2011-01-01',
        'amount-originally-secured': '12',
        'rate-of-interest': '5',
        'adjoining': False
    }


def mock_paid_financial_charge():
    return {
        'local-land-charge': 123,
        'display-id': 'LLC-3Z',
        'geometry': 'Not provided',
        'charge-type': 'Financial',
        'charge-sub-category': 'Not provided',
        'supplementary-information': 'Not provided',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'originating-authority': 'an authority',
        'charge-creation-date': '2011-01-01',
        'registration-date': '2011-01-01',
        'charge-geographic-description': 'a description',
        'amount-originally-secured': '12',
        'rate-of-interest': '5',
        'legal-document': 'An instrument',
        'law': 'a provision',
        'adjoining': False
    }


def mock_land_compensation_csv():
    return 'local-land-charge,geometry,charge-type,charge-sub-category,supplementary-information,' \
           'further-information-location,further-information-reference,originating-authority,charge-creation-date,' \
           'registration-date,law,legal-document,applicants,' \
           'servient-land-interest-description,structure-position-and-dimension,charge-geographic-description,' \
           'charge-address,amount-originally-secured,rate-of-interest,land-compensation-paid,'\
           'land-compensation-amount-type,land-capacity-description,land-works-particulars,land-sold-description,' \
           'tribunal-temporary-certificate-date,tribunal-temporary-certificate-expiry-date,' \
           'tribunal-definitive-certificate-date,expiry-date,documents-filed,display-id,amount-of-compensation,' \
           'adjoining\r\n' \
           '123,Not provided,Land compensation,Not provided,Not provided,a location,a reference,an authority,' \
           '2011-01-01,2011-01-01,a provision,An instrument,,,,a description,,,,,,,21,10,,,,,,LLC-3Z,,False\r\n'


def mock_financial_csv():
    return 'local-land-charge,geometry,charge-type,charge-sub-category,supplementary-information,' \
           'further-information-location,further-information-reference,originating-authority,charge-creation-date,' \
           'registration-date,law,legal-document,applicants,' \
           'servient-land-interest-description,structure-position-and-dimension,charge-geographic-description,' \
           'charge-address,amount-originally-secured,rate-of-interest,land-compensation-paid,' \
           'land-compensation-amount-type,land-capacity-description,land-works-particulars,land-sold-description,' \
           'tribunal-temporary-certificate-date,tribunal-temporary-certificate-expiry-date,' \
           'tribunal-definitive-certificate-date,expiry-date,documents-filed,display-id,amount-of-compensation,' \
           'adjoining\r\n' \
           '123,Not provided,Financial,Not provided,Not provided,a location,a reference,an authority,2011-01-01,' \
           '2011-01-01,a provision,An instrument,,,,a description,,12,5,,,,,,,,,,,LLC-3Z,,False\r\n'
