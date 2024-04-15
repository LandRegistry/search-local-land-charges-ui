from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields import SubmitField


class ConfirmSearchAreaForm(FlaskForm):
    submit = SubmitField(_("Confirm area"), widget=GovSubmitInput())
