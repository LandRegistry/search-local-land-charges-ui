import copy
from unittest import TestCase
from unittest.mock import patch
from xml.dom.minidom import parseString

from server.app import app
from server.services.paid_results.paid_results_formatter import PaidResultsFormatter
from unit_tests.test_data.mock_land_charge import (
    mock_financial_charge,
    mock_financial_csv,
    mock_land_charge,
    mock_land_compensation_charge,
    mock_land_compensation_csv,
    mock_paid_financial_charge,
    mock_paid_land_charge,
    mock_paid_land_compensation_charge,
)
from unit_tests.test_data.mock_lon import mock_light_obstruction_notice, mock_paid_lon


class TestPaidResultsFormatter(TestCase):
    def setUp(self):
        app.config["Testing"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.testing = True

    def test_local_land_charge_format(self):
        mock_charges = [mock_land_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        converted_charges = charge_formatter.to_json()
        self.assertEqual(converted_charges, [mock_paid_land_charge()])

    @patch("server.services.paid_results.paid_results_formatter.dicttoxml")
    def test_local_land_charge_xml(self, mock_dict_to_xml):
        mock_charges = [mock_land_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        charge_formatter.to_xml()
        mock_dict_to_xml.assert_called_with([mock_paid_land_charge()])

    @patch("server.services.paid_results.paid_results_formatter.csv")
    def test_local_land_charge_csv(self, mock_csv):
        mock_charges = [mock_land_charge()]
        mock_paid_charges = [mock_paid_land_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        charge_formatter.to_csv()
        mock_csv.DictWriter.assert_called()
        mock_csv.DictWriter.return_value.writeheader.assert_called()
        mock_csv.DictWriter.return_value.writerows.assert_called_with(mock_paid_charges)

    def test_local_land_charge_format_xml(self):
        mock_charges = [mock_land_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        xml = parseString(charge_formatter.to_xml())

        self.assertEqual(self.text_for_tag(xml, "local-land-charge"), "123")
        self.assertEqual(self.text_for_tag(xml, "geometry"), "Not provided")
        self.assertEqual(self.text_for_tag(xml, "charge-type"), "a charge type")
        self.assertEqual(self.text_for_tag(xml, "charge-sub-category"), "Not provided")
        self.assertEqual(self.text_for_tag(xml, "supplementary-information"), "Not provided")
        self.assertEqual(self.text_for_tag(xml, "further-information-location"), "a location")
        self.assertEqual(self.text_for_tag(xml, "further-information-reference"), "a reference")
        self.assertEqual(self.text_for_tag(xml, "originating-authority"), "an authority")
        self.assertEqual(self.text_for_tag(xml, "charge-creation-date"), "2011-01-01")
        self.assertEqual(self.text_for_tag(xml, "registration-date"), "2011-01-01")
        self.assertEqual(self.text_for_tag(xml, "charge-geographic-description"), "a description")
        self.assertEqual(self.text_for_tag(xml, "law"), "a provision")
        self.assertEqual(self.text_for_tag(xml, "legal-document"), "An instrument")

    def test_financial_charge_format_xml(self):
        mock_charges = [mock_financial_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        xml = parseString(charge_formatter.to_xml())

        self.assertEqual(self.text_for_tag(xml, "amount-originally-secured"), "12")
        self.assertEqual(self.text_for_tag(xml, "rate-of-interest"), "5")
        self.assertEqual(self.text_for_tag(xml, "law"), "a provision")
        self.assertEqual(self.text_for_tag(xml, "legal-document"), "An instrument")

    def test_financial_charge_format(self):
        mock_charges = [mock_financial_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        converted_charges = charge_formatter.to_json()
        self.assertEqual(converted_charges, [mock_paid_financial_charge()])

    def test_financial_charge_format_csv(self):
        mock_charges = [mock_financial_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        csv = charge_formatter.to_csv()
        print(mock_financial_csv())
        print(csv)
        self.assertEqual(csv, mock_financial_csv())

    def test_land_compensation_charge_format_xml(self):
        mock_charges = [mock_land_compensation_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        xml = parseString(charge_formatter.to_xml())

        self.assertEqual(self.text_for_tag(xml, "land-sold-description"), "10")
        self.assertEqual(self.text_for_tag(xml, "land-works-particulars"), "21")
        self.assertEqual(self.text_for_tag(xml, "law"), "a provision")
        self.assertEqual(self.text_for_tag(xml, "legal-document"), "An instrument")

    def test_land_compensation_charge_format_csv(self):
        mock_charges = [mock_land_compensation_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        csv = charge_formatter.to_csv()
        self.assertEqual(csv, mock_land_compensation_csv())

    def test_land_compensation_charge_format(self):
        mock_charges = [mock_land_compensation_charge()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        converted_charges = charge_formatter.to_json()
        self.assertEqual(converted_charges, [mock_paid_land_compensation_charge()])

    def test_light_obstruction_notice_charge_format_xml(self):
        mock_charges = [mock_light_obstruction_notice()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        xml = parseString(charge_formatter.to_xml())
        self.assertEqual(self.text_for_tag(xml, "tribunal-definitive-certificate-date"), "2012-01-01")
        self.assertEqual(
            self.text_for_tag(xml, "servient-land-interest-description"),
            "land interest description",
        )
        self.assertEqual(self.text_for_tag(xml, "expiry-date"), "2011-01-01")
        self.assertEqual(self.text_for_tag(xml, "law"), "a provision")
        self.assertEqual(self.text_for_tag(xml, "legal-document"), "An instrument")

    def test_light_obstruction_charge_format(self):
        mock_charges = [mock_light_obstruction_notice()]
        charge_formatter = PaidResultsFormatter(mock_charges)
        converted_charges = charge_formatter.to_json()
        formatted_lon = copy.deepcopy(mock_paid_lon())
        del formatted_lon["further-information-reference"]
        del formatted_lon["originating-authority"]
        print(converted_charges)
        print(formatted_lon)
        self.assertEqual(converted_charges, [formatted_lon])

    def test_no_charges(self):
        mock_charges = []
        charge_formatter = PaidResultsFormatter(mock_charges)
        converted_charges = charge_formatter.to_json()
        self.assertEqual(converted_charges, {"result": "There are 0 local land charges in this area"})

    def test_charges_none(self):
        charge_formatter = PaidResultsFormatter(None)
        converted_charges = charge_formatter.to_json()
        self.assertEqual(converted_charges, {"result": "There are 0 local land charges in this area"})

    def text_for_tag(self, xml, tag):
        return xml.getElementsByTagName(tag)[0].firstChild.nodeValue
