from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length


class ResetPasswordForm(FlaskForm):
    email_address = StringField(
        _("Email address"),
        description=_("We will send you details on how to change your password"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter an email address")),
            Length(max=256, message=_("Email address must be 256 characters or fewer")),
            Email(message=_("Enter an email address in the correct format, like name@example.com")),
        ],
    )

    submit = SubmitField(_("Submit"), widget=GovSubmitInput())
