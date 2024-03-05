from flask_wtf import FlaskForm
from wtforms.fields import SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from flask_babel import lazy_gettext as _


class ConfirmSearchAreaForm(FlaskForm):
    submit = SubmitField(
        _("Confirm area"),
        widget=GovSubmitInput())
