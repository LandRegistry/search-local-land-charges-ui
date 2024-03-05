from flask import render_template
from markupsafe import Markup
from govuk_frontend_wtf.gov_form_base import GovFormBase


class FieldGroupWidget(GovFormBase):

    template = "custom-wtf-widgets/field-group-widget.html"

    def __call__(self, field, **kwargs):
        return Markup(render_template(self.template, field=field, kwargs=kwargs))
