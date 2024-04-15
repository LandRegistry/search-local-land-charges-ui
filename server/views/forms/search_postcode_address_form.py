from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired


class SearchPostcodeAddressForm(FlaskForm):
    search_term = StringField(
        _("Search by postcode or street name"),
        description=_("For example, ‘SE5 9QY’ or ‘High Street’"),
        widget=GovTextInput(),
        validators=[InputRequired(message=_("Enter a postcode or location"))],
    )

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())
