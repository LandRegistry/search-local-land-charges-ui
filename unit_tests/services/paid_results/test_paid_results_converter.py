from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from server.app import app
from server.services.paid_results.paid_results_converter import PaidResultsConverter
from unit_tests.test_data.mock_land_charge import mock_land_charge, mock_paid_land_charge
from unittest import TestCase
from unittest.mock import patch
import json


class TestPaidResultsConverter(TestCase):

    def setUp(self):
        app.config['Testing'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True

    def to_xml(self, charges):
        return dicttoxml(charges)

    @patch('server.services.paid_results.paid_results_converter.io')
    @patch('server.services.paid_results.paid_results_converter.PaidResultsFormatter')
    def test_to_json(self, mock_formatter, mock_io):
        mock_charges = [mock_land_charge()]
        mock_paid_charges = [mock_paid_land_charge()]
        mock_formatter.return_value.to_json.return_value = mock_paid_charges
        PaidResultsConverter.to_json(mock_charges)
        mock_formatter.return_value.to_json.assert_called()
        mock_io.BytesIO.return_value.write.assert_called_with(
            json.dumps(mock_paid_charges, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8'))
        mock_io.BytesIO.return_value.seek.assert_called_with(0)

    @patch('server.services.paid_results.paid_results_converter.io')
    @patch('server.services.paid_results.paid_results_converter.PaidResultsFormatter')
    def test_to_xml(self, mock_formatter, mock_io):
        mock_charges = [mock_land_charge()]
        mock_xml_charges = self.to_xml([mock_paid_land_charge()])
        mock_formatter.return_value.to_xml.return_value = mock_xml_charges
        PaidResultsConverter.to_xml(mock_charges)
        mock_formatter.return_value.to_xml.assert_called()
        mock_io.BytesIO.return_value.write.assert_called_with(
            parseString(mock_xml_charges).toprettyxml().encode('utf-8'))
        mock_io.BytesIO.return_value.seek.assert_called_with(0)

    @patch('server.services.paid_results.paid_results_converter.io')
    @patch('server.services.paid_results.paid_results_converter.PaidResultsFormatter')
    def test_to_csv(self, mock_formatter, mock_io):
        mock_charges = [mock_land_charge()]
        mock_formatter.return_value.to_csv.return_value = 'charges in csv format'
        PaidResultsConverter.to_csv(mock_charges)
        mock_formatter.return_value.to_csv.assert_called()
        mock_io.BytesIO.return_value.write.assert_called_with('charges in csv format'.encode('utf-8'))
        mock_io.BytesIO.return_value.seek.assert_called_with(0)
