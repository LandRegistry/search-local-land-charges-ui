applicant_address = {
    "line-1": "123 Fake Street",
    "line-2": "Test Town",
    "line-3": "Up",
    "postcode": "12H 2ND",
    "country": "United Kingdom"
}


structure_position_and_dimension = {
    "height": "28 Metres",
    "extent-covered": "Part of the extent",
    "part-explanatory-text": "Over yonder"
}


documents_filed = {
    "form-a": [{
        'bucket': 'abucket',
        'subdirectory': 'adirectory',
        'reference': 'some reference'
    }],
    "definitive-certificate": [{
        'bucket': 'abucket',
        'subdirectory': 'adirectory',
        'reference': 'some reference'
    }]
}


def mock_light_obstruction_notice():
    return {
        'local-land-charge': 123,
        'registration-date': '2011-01-01',
        'originating-authority-charge-identifier': 'an identifier',
        'charge-type': 'Light obstruction notice',
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
        'tribunal-definitive-certificate-date': '2012-01-01',
        'applicants': [{'applicant-name': 'Human Name', 'applicant-address': applicant_address}],
        'servient-land-interest-description': 'land interest description',
        'structure-position-and-dimension': structure_position_and_dimension,
        'documents-filed': documents_filed,
        'adjoining': False
    }


def mock_paid_lon():
    return {
        'local-land-charge': 123,
        'display-id': 'LLC-3Z',
        'geometry': 'Not provided',
        'charge-type': 'Light obstruction notice',
        'charge-sub-category': 'Not provided',
        'supplementary-information': 'Not provided',
        'further-information-location': 'a location',
        'further-information-reference': 'a reference',
        'originating-authority': 'an authority',
        'charge-creation-date': '2011-01-01',
        'registration-date': '2011-01-01',
        'charge-geographic-description': 'a description',
        'servient-land-interest-description': 'land interest description',
        'structure-position-and-dimension': structure_position_and_dimension,
        'applicants': [{'applicant-name': 'Human Name', 'applicant-address': applicant_address}],
        'tribunal-definitive-certificate-date': '2012-01-01',
        'expiry-date': '2011-01-01',
        'documents-filed': ["definitive-certificate", "form-a"],
        'law': 'a provision',
        'legal-document': 'An instrument',
        'adjoining': False
    }
