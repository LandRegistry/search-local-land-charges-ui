from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovPasswordInput, GovSubmitInput
from wtforms.fields import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from server.views.forms.validate_common import valid_password_rules


class ChangePasswordWithTokenForm(FlaskForm):
    password = PasswordField(
        _("Password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer")),
        ],
    )

    def validate_password(self, field):
        if not valid_password_rules(field.data):
            raise ValidationError(_("Enter a password in the correct format"))

    submit = SubmitField(_("Submit"), widget=GovSubmitInput())
