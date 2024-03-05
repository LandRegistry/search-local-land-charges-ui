import io
import json
from defusedxml.minidom import parseString
from server.services.paid_results.paid_results_formatter import PaidResultsFormatter


class PaidResultsConverter(object):

    @staticmethod
    def to_json(charges):
        json_charges = PaidResultsFormatter(charges).to_json()
        json_charges = json.dumps(json_charges, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
        stream = io.BytesIO()
        stream.write(json_charges)
        stream.seek(0)
        return stream

    @staticmethod
    def to_csv(charges):
        csvfile = PaidResultsFormatter(charges).to_csv()
        stream = io.BytesIO()
        stream.write(csvfile.encode('utf-8'))
        stream.seek(0)
        return stream

    @staticmethod
    def to_xml(charges):
        xml_charges = PaidResultsFormatter(charges).to_xml()
        xml_charges = parseString(xml_charges).toprettyxml().encode('utf-8')
        stream = io.BytesIO()
        stream.write(xml_charges)
        stream.seek(0)
        return stream
