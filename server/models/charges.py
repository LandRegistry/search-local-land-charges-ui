from marshmallow import fields, post_load, post_dump
from server.models.common import BaseSchema, jsonnamedlist, default_text


class LocalLandChargeItemSchema(BaseSchema):
    """Local Land Charge schema object."""
    geometry = fields.Dict()
    local_land_charge = fields.Int()
    registration_date = fields.Date()
    originating_authority_charge_identifier = fields.Str()
    charge_type = fields.Str()
    charge_sub_category = fields.Str()
    charge_geographic_description = fields.Str()
    charge_address = fields.Dict()
    charge_creation_date = fields.Date()
    instrument = fields.Str()
    statutory_provision = fields.Str()
    further_information_location = fields.Str()
    further_information_reference = fields.Str()
    unique_property_reference_numbers = fields.List(fields.Int())
    old_register_part = fields.Str()
    originating_authority = fields.Str()
    migrating_authority = fields.Str()
    migration_supplier = fields.Str()
    expiry_date = fields.Date()
    end_date = fields.Date()
    start_date = fields.Date()
    author = fields.Dict()
    supplementary_information = fields.Str()
    adjoining = fields.Boolean()
    schema_version = fields.Str()
    bulk_update_reason = fields.Str()

    # For charges don't serialize null fields (but do serialize booleans)
    @post_dump
    def postdump_process(self, data, **kwargs):
        return {
            key.replace('_', '-'): value for key, value in data.items()
            if value or isinstance(value, bool)
        }

    # Create LLC object
    @post_load
    def make_charge(self, data, **kwargs):
        return LocalLandChargeItem(**data)


class LandCompensationItemSchema(LocalLandChargeItemSchema):
    land_compensation_paid = fields.Str()
    land_compensation_amount_type = fields.Str()
    amount_of_compensation = fields.Str(allow_none=True)
    land_capacity_description = fields.Str()
    land_works_particulars = fields.Str()
    land_sold_description = fields.Str()

    # Create LLC object
    @post_load
    def make_charge(self, data, **kwargs):
        return LandCompensationItem(**data)


class LightObstructionNoticeItemSchema(LocalLandChargeItemSchema):
    tribunal_temporary_certificate_date = fields.Date()
    tribunal_temporary_certificate_expiry_date = fields.Date()
    tribunal_definitive_certificate_date = fields.Date()
    applicants = fields.List(fields.Dict())
    applicant_address = fields.Dict()
    servient_land_interest_description = fields.Str()
    structure_position_and_dimension = fields.Dict()
    documents_filed = fields.Dict()

    # Create LLC object
    @post_load
    def make_charge(self, data, **kwargs):
        return LightObstructionNoticeItem(**data)


class FinancialItemSchema(LocalLandChargeItemSchema):
    amount_originally_secured = fields.Str()
    rate_of_interest = fields.Str()

    # Create LLC object
    @post_load
    def make_charge(self, data, **kwargs):
        return FinancialItem(**data)


def local_land_charge_named_list(schema, name, members, **kwargs):
    obj = jsonnamedlist(schema, name, members, **kwargs)

    def format_charge_address_for_display(self):
        if self.charge_address:
            address = []
            if 'line-1' in self.charge_address and self.charge_address['line-1']:
                address.append(self.charge_address['line-1'])
            if 'line-2' in self.charge_address and self.charge_address['line-2']:
                address.append(self.charge_address['line-2'])
            if 'line-3' in self.charge_address and self.charge_address['line-3']:
                address.append(self.charge_address['line-3'])
            if 'line-4' in self.charge_address and self.charge_address['line-4']:
                address.append(self.charge_address['line-4'])
            if 'line-5' in self.charge_address and self.charge_address['line-5']:
                address.append(self.charge_address['line-5'])
            if 'line-6' in self.charge_address and self.charge_address['line-6']:
                address.append(self.charge_address['line-6'])
            if 'postcode' in self.charge_address and self.charge_address['postcode']:
                address.append(self.charge_address['postcode'])

            return address

        return default_text

    obj.format_charge_address_for_display = format_charge_address_for_display

    return obj


def financial_named_list(schema, name, members, **kwargs):
    obj = local_land_charge_named_list(schema, name, members, **kwargs)

    def format_interest_rate_for_display(self):
        if self.rate_of_interest:
            return self.rate_of_interest
        return default_text

    obj.format_interest_rate_for_display = format_interest_rate_for_display

    return obj


def format_applicants_for_display(self):
    display_applicants = []
    if not self.applicants:
        return {"applicant_name": default_text, 'applicant_address': []}
    for applicant in self.applicants:
        display_applicant = {}
        if applicant['applicant-name']:
            display_applicant['applicant_name'] = applicant['applicant-name']
        else:
            display_applicant['applicant_name'] = default_text
        if applicant['applicant-address']:
            address = []
            if 'line-1' in applicant['applicant-address'] and applicant['applicant-address']['line-1']:
                address.append(applicant['applicant-address']['line-1'])
            if 'line-2' in applicant['applicant-address'] and applicant['applicant-address']['line-2']:
                address.append(applicant['applicant-address']['line-2'])
            if 'line-3' in applicant['applicant-address'] and applicant['applicant-address']['line-3']:
                address.append(applicant['applicant-address']['line-3'])
            if 'line-4' in applicant['applicant-address'] and applicant['applicant-address']['line-4']:
                address.append(applicant['applicant-address']['line-4'])
            if 'line-5' in applicant['applicant-address'] and applicant['applicant-address']['line-5']:
                address.append(applicant['applicant-address']['line-5'])
            if 'line-6' in applicant['applicant-address'] and applicant['applicant-address']['line-6']:
                address.append(applicant['applicant-address']['line-6'])
            if 'postcode' in applicant['applicant-address'] and applicant['applicant-address']['postcode']:
                address.append(applicant['applicant-address']['postcode'])
            if 'country' in applicant['applicant-address'] and applicant['applicant-address']['country']:
                address.append(applicant['applicant-address']['country'])
            display_applicant['applicant_address'] = address
        else:
            display_applicant['applicant_address'] = []
        display_applicants.append(display_applicant)
    return display_applicants


def format_height_pos_for_display(self, key):
    pos_dim = self.structure_position_and_dimension
    if pos_dim:
        if key == 'height':
            if 'units' in pos_dim and 'height' in pos_dim:
                return '{} {}'.format(pos_dim['height'], pos_dim['units'])
            elif 'height' in pos_dim:
                return pos_dim['height']
        elif key == 'position':
            if 'part-explanatory-text' in pos_dim:
                return pos_dim['part-explanatory-text']
            elif 'extent-covered' in pos_dim:
                return pos_dim['extent-covered']

    return default_text


def light_obstruction_notice_named_list(schema, name, members, **kwargs):
    obj = local_land_charge_named_list(schema, name, members, **kwargs)

    obj.format_applicants_for_display = format_applicants_for_display
    obj.format_height_pos_for_display = format_height_pos_for_display

    return obj


local_land_charge_item_class = local_land_charge_named_list(
    LocalLandChargeItemSchema(),
    "LocalLandChargeItem",
    "schema_version, geometry, migration_supplier, originating_authority_charge_identifier, \
    registration_date, local_land_charge, charge_creation_date, charge_type, \
    charge_sub_category, migrating_authority, old_register_part, charge_geographic_description, \
    charge_address, instrument, statutory_provision, further_information_location, \
    further_information_reference, expiry_date, supplementary_information, start_date, \
    end_date, author, originating_authority, unique_property_reference_numbers, adjoining, bulk_update_reason",
    default=None)


class LocalLandChargeItem(local_land_charge_item_class):
    pass


land_compensation_item_class = local_land_charge_named_list(
    LandCompensationItemSchema(),
    "LandCompensationItemSchema",
    "schema_version, geometry, migration_supplier, originating_authority_charge_identifier, \
    registration_date, local_land_charge, charge_creation_date, charge_type, \
    charge_sub_category, migrating_authority, old_register_part, charge_geographic_description, \
    charge_address, instrument, statutory_provision, further_information_location, \
    further_information_reference, expiry_date, supplementary_information, start_date, \
    end_date, author, originating_authority, unique_property_reference_numbers, \
    land_works_particulars, land_sold_description, land_compensation_amount_type, land_capacity_description, \
    land_compensation_paid, amount_of_compensation, adjoining, bulk_update_reason", default=None)


class LandCompensationItem(land_compensation_item_class):
    pass


light_obstruction_notice_item_class = light_obstruction_notice_named_list(
    LightObstructionNoticeItemSchema(),
    "LightObstructionNoticeItemSchema",
    "schema_version, geometry, migration_supplier, originating_authority_charge_identifier, \
    registration_date, local_land_charge, charge_creation_date, charge_type, \
    charge_sub_category, migrating_authority, old_register_part, charge_geographic_description, \
    charge_address, instrument, statutory_provision, further_information_location, \
    further_information_reference, expiry_date, supplementary_information, start_date, \
    end_date, author, originating_authority, unique_property_reference_numbers, applicants, \
    servient_land_interest_description, structure_position_and_dimension, \
    tribunal_definitive_certificate_date, documents_filed, tribunal_temporary_certificate_date, \
    tribunal_temporary_certificate_expiry_date, adjoining, bulk_update_reason", default=None)


class LightObstructionNoticeItem(light_obstruction_notice_item_class):
    pass


financial_item_class = financial_named_list(
    FinancialItemSchema(),
    "FinancialItemSchema",
    "schema_version, geometry, migration_supplier, originating_authority_charge_identifier, \
    registration_date, local_land_charge, charge_creation_date, charge_type, \
    charge_sub_category, migrating_authority, old_register_part, charge_geographic_description, \
    charge_address, instrument, statutory_provision, further_information_location, \
    further_information_reference, expiry_date, supplementary_information, start_date, \
    end_date, author, unique_property_reference_numbers, originating_authority, amount_originally_secured, \
    rate_of_interest, adjoining, bulk_update_reason", default=None)


class FinancialItem(financial_item_class):
    pass
