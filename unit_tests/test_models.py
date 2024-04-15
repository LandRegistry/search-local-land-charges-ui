import copy
import unittest
from datetime import date

from server.models.charges import (
    FinancialItem,
    LandCompensationItem,
    LightObstructionNoticeItem,
    LocalLandChargeItem,
)
from unit_tests.test_data.mock_land_charge import (
    mock_financial_charge,
    mock_land_charge,
    mock_land_compensation_charge,
)
from unit_tests.test_data.mock_lon import (
    applicant_address,
    documents_filed,
    mock_light_obstruction_notice,
    structure_position_and_dimension,
)

mock_charge_item = LocalLandChargeItem(
    local_land_charge=123,
    registration_date=date(2011, 1, 1),
    originating_authority_charge_identifier="an identifier",
    charge_type="a charge type",
    charge_geographic_description="a description",
    charge_creation_date=date(2011, 1, 1),
    instrument="An instrument",
    statutory_provision="a provision",
    further_information_location="a location",
    further_information_reference="a reference",
    unique_property_reference_numbers=[123, 456],
    old_register_part="1a",
    originating_authority="an authority",
    migrating_authority="another authority",
    migration_supplier="a supplier",
    expiry_date=date(2011, 1, 1),
    end_date=date(2011, 1, 1),
    start_date=date(2011, 1, 1),
    adjoining=False,
)

mock_financial_item = FinancialItem(
    local_land_charge=123,
    registration_date=date(2011, 1, 1),
    originating_authority_charge_identifier="an identifier",
    charge_type="Financial",
    charge_geographic_description="a description",
    charge_creation_date=date(2011, 1, 1),
    instrument="An instrument",
    statutory_provision="a provision",
    further_information_location="a location",
    further_information_reference="a reference",
    unique_property_reference_numbers=[123, 456],
    old_register_part="1a",
    originating_authority="an authority",
    migrating_authority="another authority",
    migration_supplier="a supplier",
    expiry_date=date(2011, 1, 1),
    end_date=date(2011, 1, 1),
    start_date=date(2011, 1, 1),
    amount_originally_secured="12",
    rate_of_interest="5",
    adjoining=False,
)

mock_land_compensation_item = LandCompensationItem(
    local_land_charge=123,
    registration_date=date(2011, 1, 1),
    originating_authority_charge_identifier="an identifier",
    charge_type="Land compensation",
    charge_geographic_description="a description",
    charge_creation_date=date(2011, 1, 1),
    instrument="An instrument",
    statutory_provision="a provision",
    further_information_location="a location",
    further_information_reference="a reference",
    unique_property_reference_numbers=[123, 456],
    old_register_part="1a",
    originating_authority="an authority",
    migrating_authority="another authority",
    migration_supplier="a supplier",
    expiry_date=date(2011, 1, 1),
    end_date=date(2011, 1, 1),
    start_date=date(2011, 1, 1),
    land_sold_description="10",
    land_works_particulars="21",
    land_compensation_paid=None,
    land_compensation_amount_type=None,
    land_capacity_description=None,
    adjoining=False,
)

mock_lon_item = LightObstructionNoticeItem(
    local_land_charge=123,
    registration_date=date(2011, 1, 1),
    originating_authority_charge_identifier="an identifier",
    charge_type="Light obstruction notice",
    charge_geographic_description="a description",
    charge_creation_date=date(2011, 1, 1),
    instrument="An instrument",
    statutory_provision="a provision",
    further_information_location="a location",
    further_information_reference="a reference",
    unique_property_reference_numbers=[123, 456],
    old_register_part="1a",
    originating_authority="an authority",
    migrating_authority="another authority",
    migration_supplier="a supplier",
    expiry_date=date(2011, 1, 1),
    end_date=date(2011, 1, 1),
    start_date=date(2011, 1, 1),
    tribunal_temporary_certificate_date=None,
    tribunal_temporary_certificate_expiry_date=None,
    tribunal_definitive_certificate_date=date(2012, 1, 1),
    applicants=[{"applicant-name": "Human Name", "applicant-address": applicant_address}],
    servient_land_interest_description="land interest description",
    structure_position_and_dimension=structure_position_and_dimension,
    documents_filed=documents_filed,
    adjoining=False,
)


class TestLocalLandChargeItemModel(unittest.TestCase):
    def test_local_land_charge_item_serialise(self):
        self.assertEqual(mock_charge_item.to_json(), mock_land_charge())

    def test_local_land_charge_item_deserialise(self):
        llc = LocalLandChargeItem.from_json(mock_land_charge())
        self.assertEqual(llc, mock_charge_item)
        self.assertIsNone(llc.geometry)

    def test_financial_item_serialise(self):
        self.assertEqual(mock_financial_item.to_json(), mock_financial_charge())

    def test_financial_item_deserialise(self):
        llc = FinancialItem.from_json(mock_financial_charge())
        self.assertEqual(llc, mock_financial_item)
        self.assertIsNone(llc.geometry)

    def test_land_compensation_item_serialise(self):
        self.assertEqual(mock_land_compensation_item.to_json(), mock_land_compensation_charge())

    def test_land_compensation_item_deserialise(self):
        llc = LandCompensationItem.from_json(mock_land_compensation_charge())
        self.assertEqual(llc, mock_land_compensation_item)
        self.assertIsNone(llc.geometry)
        self.assertIsNone(llc.land_compensation_paid)
        self.assertIsNone(llc.land_compensation_amount_type)
        self.assertIsNone(llc.land_capacity_description)

    def test_lon_item_serialise(self):
        self.assertEqual(mock_lon_item.to_json(), mock_light_obstruction_notice())

    def test_lon_item_deserialise(self):
        llc = LightObstructionNoticeItem.from_json(mock_light_obstruction_notice())
        self.assertEqual(llc, mock_lon_item)
        self.assertIsNone(llc.geometry)
        self.assertIsNone(llc.tribunal_temporary_certificate_date)
        self.assertIsNone(llc.tribunal_temporary_certificate_expiry_date)

    def test_lon_item_format_applicants_for_display(self):
        llc = LightObstructionNoticeItem.from_json(mock_light_obstruction_notice())
        self.assertEqual(
            llc.format_applicants_for_display(),
            [
                {
                    "applicant_address": [
                        "123 Fake Street",
                        "Test Town",
                        "Up",
                        "12H 2ND",
                        "United Kingdom",
                    ],
                    "applicant_name": "Human Name",
                }
            ],
        )

    def test_lon_item_not_allow_weird(self):
        llc = LightObstructionNoticeItem.from_json(mock_light_obstruction_notice())
        llc.aardvark = "trousers"

    def test_lon_item_deserialise_missing_mandatory_items(self):
        lon_mandatory = copy.deepcopy(mock_light_obstruction_notice())
        del lon_mandatory["tribunal-definitive-certificate-date"]
        del lon_mandatory["applicants"]
        del lon_mandatory["servient-land-interest-description"]

        del lon_mandatory["structure-position-and-dimension"]["height"]

        llc = LightObstructionNoticeItem.from_json(lon_mandatory)
        self.assertEqual(
            llc.format_date_for_display("tribunal_definitive_certificate_date"),
            "Not provided",
        )
        self.assertEqual(llc.format_applicants_for_display()["applicant_name"], "Not provided")
        self.assertEqual(llc.format_applicants_for_display()["applicant_address"], [])
        self.assertEqual(
            llc.format_field_for_display("servient_land_interest_description"),
            "Not provided",
        )
        self.assertEqual(llc.format_height_pos_for_display("height"), "Not provided")

    def test_llc_format_charge_address_for_display(self):
        llc = LocalLandChargeItem.from_json(mock_land_charge())
        llc.charge_address = {
            "line-1": "aline1",
            "line-2": "aline2",
            "line-3": "aline3",
            "line-4": "aline4",
            "line-5": "aline5",
            "line-6": "aline6",
            "postcode": "apostcode",
        }
        self.assertEqual(
            llc.format_charge_address_for_display(),
            ["aline1", "aline2", "aline3", "aline4", "aline5", "aline6", "apostcode"],
        )
