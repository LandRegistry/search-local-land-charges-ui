from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.validators import Email, InputRequired, Length
from flask_babel import lazy_gettext as _


class ExpiredActivationForm(FlaskForm):
    email_address = StringField(
        _("Email address"),
        description=_("We will resend the email with details of how to activate your account"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter an email address")),
            Length(max=256, message=_("Email address must be 256 characters or fewer")),
            Email(message=_("Enter an email address in the correct format, like name@example.com"))
        ],
    )

    submit = SubmitField(_("Submit"), widget=GovSubmitInput())