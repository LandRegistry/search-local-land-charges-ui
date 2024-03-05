from server.app import app
from unittest import TestCase
from server.services.datetime_formatter import format_date, format_long_date
from flask import g
from unit_tests.utilities_tests import super_test_context
from datetime import datetime


welsh_dates = ["22ain Ionawr 2023",
               "10fed Mai 2023",
               "1af Ionawr 2020",
               "2ail Mehefin 2021",
               "3ydd Gorffennaf 2022",
               "11eg Tachwedd 2019",
               "5ed Medi 2022"]

english_dates = ["22nd January 2023",
                 "10th May 2023",
                 "1st January 2020",
                 "2nd June 2021",
                 "3rd July 2022",
                 "11th November 2019",
                 "5th September 2022"]


class TestDatetimeFormatter(TestCase):

    def setUp(self):
        app.config['Testing'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True

    def test_format_date_ok_welsh(self):
        with super_test_context(app):
            g.locale = "cy"
            result = format_date(datetime(2001, 1, 1, 0, 0, 0, 0))
            self.assertEqual(result, "01 Ionawr 2001")

    def test_format_date_ok(self):
        with super_test_context(app):
            g.locale = "en"
            result = format_date(datetime(2001, 1, 1, 0, 0, 0, 0))
            self.assertEqual(result, "01 January 2001")

    def test_format_long_date_welsh(self):
        with super_test_context(app):
            g.locale = "cy"
            result = []
            for date in english_dates:
                result.append(format_long_date(date))
            self.assertEqual(result, welsh_dates)
