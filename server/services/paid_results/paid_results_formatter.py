from dicttoxml import dicttoxml
from server.services.charge_id_utils import calc_display_id
import csv
import io
from flask_babel import gettext

STATUTORY_PROVISION_DISPLAY_NAME = 'law'
INSTRUMENT_DISPLAY_NAME = 'legal-document'


class PaidResultsFormatter(object):

    common_fieldnames = ["local-land-charge", "geometry", "charge-type", "charge-sub-category",
                         "supplementary-information", "further-information-location", "further-information-reference",
                         "originating-authority", "charge-creation-date", "registration-date", "statutory-provision",
                         "instrument"]

    light_obstruction_notice_fieldnames = ["applicants", "servient-land-interest-description",
                                           "structure-position-and-dimension"]

    optional_field_names = ['charge-geographic-description', 'charge-address', 'amount-originally-secured',
                            'rate-of-interest', 'land-compensation-paid', 'land-compensation-amount-type',
                            'land-capacity-description', 'land-works-particulars', 'land-sold-description',
                            'tribunal-temporary-certificate-date', 'tribunal-temporary-certificate-expiry-date',
                            'tribunal-definitive-certificate-date', 'expiry-date', 'documents-filed', 'display-id',
                            'amount-of-compensation', 'adjoining']

    def __init__(self, charges):
        self.charges = charges

    def to_json(self):
        converted_charges = []

        if not self.charges:
            return {'result': 'There are 0 local land charges in this area'}

        for charge in self.charges:
            converted_charge = self.local_land_charge_fields(charge)

            if "Land compensation" in charge['charge-type']:
                converted_charge.update(self.land_compensation_charge_fields(charge))
            elif "Light obstruction notice" in charge['charge-type']:
                del converted_charge['further-information-reference']
                del converted_charge['originating-authority']
                converted_charge.update(self.light_obstruction_notice_fields(charge))
            elif "Financial" in charge['charge-type']:
                converted_charge.update(self.financial_charge_fields(charge))

            converted_charges.append(converted_charge)

        return converted_charges

    def to_xml(self):
        json_charges = self.to_json()
        return dicttoxml(json_charges)

    def to_csv(self):
        all_field_names = self.common_fieldnames + self.light_obstruction_notice_fieldnames + self.optional_field_names

        statutory_provision_position = all_field_names.index('statutory-provision')
        all_field_names[statutory_provision_position] = STATUTORY_PROVISION_DISPLAY_NAME
        instrument_position = all_field_names.index('instrument')
        all_field_names[instrument_position] = INSTRUMENT_DISPLAY_NAME

        formatted_charges = self.to_json()

        csvfile = io.StringIO()

        writer = csv.DictWriter(csvfile, fieldnames=all_field_names)

        if 'result' in formatted_charges:
            writer = csv.DictWriter(csvfile, fieldnames=['result'])
            writer.writeheader()
            writer.writerows([formatted_charges])
        else:
            writer.writeheader()
            writer.writerows(formatted_charges)

        return csvfile.getvalue()

    def local_land_charge_fields(self, charge):
        converted_charge = {}

        for key in self.common_fieldnames:
            converted_charge[key] = self.format_field(charge.get(key))

        # Don't reformat adjoining
        converted_charge['adjoining'] = charge.get('adjoining')

        if charge.get('charge-geographic-description'):
            converted_charge["charge-geographic-description"] = charge.get('charge-geographic-description')
        else:
            converted_charge["charge-address"] = charge.get('charge-address')

        converted_charge['display-id'] = calc_display_id(charge.get('local-land-charge'))
        converted_charge[STATUTORY_PROVISION_DISPLAY_NAME] = converted_charge.pop('statutory-provision')
        converted_charge[INSTRUMENT_DISPLAY_NAME] = converted_charge.pop('instrument')

        return converted_charge

    def financial_charge_fields(self, charge):
        return {
            'amount-originally-secured': self.format_field(charge.get('amount-originally-secured')),
            'rate-of-interest': self.format_field(charge.get('rate-of-interest'))
        }

    def land_compensation_charge_fields(self, charge):
        if charge.get('land-compensation-paid') or charge.get('land-compensation-amount-type') \
                or charge.get('land-capacity-description'):
            fields = {
                'land-compensation-paid': self.format_field(charge.get('land-compensation-paid')),
                'amount-of-compensation': self.format_field(charge.get('amount-of-compensation')),
                'land-compensation-amount-type': self.format_field(charge.get('land-compensation-amount-type')),
                'land-capacity-description': self.format_field(charge.get('land-capacity-description'))
            }
        else:
            fields = {
                'land-works-particulars': self.format_field(charge.get('land-works-particulars')),
                'land-sold-description': self.format_field(charge.get('land-sold-description'))
            }

        return fields

    def light_obstruction_notice_fields(self, charge):
        fields = {}

        for key in self.light_obstruction_notice_fieldnames:
            fields[key] = self.format_field(charge.get(key))

        fields['documents-filed'] = []
        for key in charge.get('documents-filed'):
            fields['documents-filed'].append(key)

        fields['documents-filed'].sort()

        if 'temporary-certificate' in fields['documents-filed']:
            fields["tribunal-temporary-certificate-date"] = \
                self.format_field(charge.get("tribunal-temporary-certificate-date"))
            fields["tribunal-temporary-certificate-expiry-date"] = \
                self.format_field(charge.get("tribunal-temporary-certificate-expiry-date"))

        if 'definitive-certificate' in fields['documents-filed']:
            fields["expiry-date"] = self.format_field(charge.get("expiry-date", ''))
            fields["tribunal-definitive-certificate-date"] = \
                self.format_field(charge.get("tribunal-definitive-certificate-date"))

        return fields

    def format_field(self, field):
        if field:
            return field
        return gettext('Not provided')
