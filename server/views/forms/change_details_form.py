from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ChangeDetailsForm(FlaskForm):
    first_name = StringField(
        _("First name"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter a first name")),
            Length(max=256, message=_("First name must be 256 characters or fewer")),
        ],
    )

    last_name = StringField(
        _("Last name"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter a last name")),
            Length(max=256, message=_("Last name must be 256 characters or fewer")),
        ],
    )

    submit = SubmitField(_("Save changes"), widget=GovSubmitInput())
