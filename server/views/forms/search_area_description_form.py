from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovCharacterCount,
    GovRadioInput,
    GovSubmitInput,
    GovTextInput,
)
from wtforms.fields import (
    HiddenField,
    RadioField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length


class SearchAreaDescriptionForm(FlaskForm):
    has_address = RadioField(
        widget=GovRadioInput(),
        choices=["enter_own_description", "find_address"],
        validators=[InputRequired(_("Choose one option"))],
    )

    selected_address = HiddenField()

    search_area_description = TextAreaField(
        _("Describe the area you have searched"),
        description=_("For example, 'flats 1-5 Church Lane' or 'land to the north of the bypass'."),
        validators=[Length(max=1000, message=_("Description must be shorter than 1000 characters"))],
        widget=GovCharacterCount(),
    )

    search_postcode = StringField(_("Enter a postcode"), widget=GovTextInput())

    find = SubmitField(_("Find address"), widget=GovSubmitInput())

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())
