from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, RadioField, TextAreaField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovRadioInput, GovCharacterCount
from wtforms.validators import InputRequired, Length
from flask_babel import lazy_gettext as _


class ConfirmAddressForm(FlaskForm):

    address_matches = RadioField(widget=GovRadioInput(), choices=["yes", "no"],
                                 validators=[InputRequired(_("Choose one option"))])

    search_area_description = \
        TextAreaField(_("Describe all search areas"),
                      description=_("For example, 'flats 1-5 Church Lane' or 'land to the north of the bypass'."),
                      validators=[Length(max=1000, message=_("Description must be shorter than 1000 characters"))],
                      widget=GovCharacterCount())

    submit = SubmitField(
        _("Continue"),
        widget=GovSubmitInput())
