from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovPasswordInput,
    GovSubmitInput,
    GovTextInput,
)
from wtforms.fields import HiddenField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length

from server.views.forms.custom_fields import FieldGroup


class UsernamePasswordForm(FlaskForm):
    username = StringField(
        _("Email address"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter an email address")),
            Length(max=256, message=_("Email address must be 256 characters or fewer")),
            Email(message=_("Enter an email address in the correct format, like name@example.com")),
        ],
    )

    password = PasswordField(
        _("Password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer")),
        ],
    )


class SignInForm(FlaskForm):
    # Group together fields using FormField so we can apply one error to multiple fields
    username_password = FieldGroup(UsernamePasswordForm)

    redirect_uri = HiddenField()

    submit = SubmitField(_("Sign in"), widget=GovSubmitInput())
