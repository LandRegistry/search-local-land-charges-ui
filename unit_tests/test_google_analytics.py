import base64
import json
import re
import unittest
from unittest import mock

from flask import render_template, g
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.fields import StringField
from wtforms.validators import InputRequired
from werkzeug.http import dump_cookie

from server.custom_extensions.google_analytics.main import build_form_errors
from server.main import app


class ExampleForm(FlaskForm):
    string_field = StringField(
        "StringField",
        widget=GovTextInput(),
        validators=[InputRequired(message="StringField is required")],
    )


class TestGoogleAnalytics(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["WTF_CSRF_ENABLED"] = False

    def tearDown(self):
        app.config["WTF_CSRF_ENABLED"] = True

    def render_form(self):
        cookie = dump_cookie("cookies_policy", base64.b64encode('{"analytics": "yes"}'.encode()))
        ctx = app.test_request_context("/", headers={'Cookie': cookie})
        ctx.push()
        ctx.request.cookies
        g.locale = 'en'

        form = ExampleForm()
        form.validate()

        html = render_template("base-templates/base.html", form=form).replace("\n", "")

        return html

    def test_raised_form_errors_appear_in_script_block(self):
        with mock.patch('server.custom_extensions.google_analytics.main.config') as mock_config:
            mock_config.GOOGLE_ANALYTICS_KEY = "123"
            html = self.render_form()

        # Check that the script block is there
        self.assertIn(
            '<script type="application/json" id="form-error-data" data-form-name="ExampleForm">',
            html,
        )

        # Grab the contents of the script block
        regex = re.compile(
            '<script type="application/json" id="form-error-data" data-form-name="ExampleForm">(.*?)</script>'
        )
        matches = regex.search(html)

        # Attempt to parse it as json an check the structure matches what we want
        error_json = json.loads(matches.group(1))
        self.assertEqual(
            error_json,
            [{"name": "string_field", "errors": ["StringField is required"]}],
        )

    def test_raised_form_errors_dont_appear_in_script_block_when_analytics_disabled(
        self,
    ):
        with mock.patch('server.custom_extensions.google_analytics.main.config') as mock_config:
            mock_config.GOOGLE_ANALYTICS_KEY = False
            html = self.render_form()

        # Check that the script block is not there
        self.assertNotIn(
            '<script type="application/json" id="form-error-data" data-form-name="ExampleForm">',
            html,
        )

    def test_google_analytics_snippet_present(self):
        with mock.patch('server.custom_extensions.google_analytics.main.config') as mock_config:
            mock_config.GOOGLE_ANALYTICS_KEY = "123"
            html = self.render_form()

        # Check for a couple of the bits of JS. Not all of it, just enought to be confident it's there
        self.assertIn('<script async src="https://www.googletagmanager.com/gtag/js?id=', html)
        self.assertIn("window.dataLayer = window.dataLayer || [];", html)

    def test_google_analytics_snippet_absent_when_no_key_specified(self):
        with mock.patch('server.custom_extensions.google_analytics.main.config') as mock_config:
            mock_config.GOOGLE_ANALYTICS_KEY = False
            html = self.render_form()

        # Check for a couple of the bits of JS. Not all of it, just enought to be confident it's not there
        self.assertNotIn('<script async src="https://www.googletagmanager.com/gtag/js?id=', html)
        self.assertNotIn("window.dataLayer = window.dataLayer || [];", html)


class TestGoogleAnalyticsFormErrorBuilder(unittest.TestCase):
    def test_build_form_errors_with_one_field_and_error(self):
        data = {"boolean_field": ["Please tick the box"]}

        result = build_form_errors(data)

        self.assertIsInstance(result, list)
        self.assertDictEqual(result[0], {"errors": ["Please tick the box"], "name": "boolean_field"})

    def test_build_form_errors_with_nested_sub_forms(self):
        data = {
            "string_field": ["StringField is required"],
            "subform": {
                "integer_field": ["IntegerField is required"],
                "sub_subform": {"another_field": ["Another field is required"]},
            },
        }

        result = build_form_errors(data)

        self.assertIsInstance(result, list)
        expected_error_list = [
            {
                "errors": ["Another field is required"],
                "name": "subform-sub_subform-another_field",
            },
            {"errors": ["IntegerField is required"], "name": "subform-integer_field"},
            {"errors": ["StringField is required"], "name": "string_field"},
        ]
        self.assertCountEqual(result, expected_error_list)

    def test_build_form_errors_with_empty_data(self):
        data = {}

        result = build_form_errors(data)

        self.assertEqual(result, [])
