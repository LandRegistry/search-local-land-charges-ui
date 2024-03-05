from flask_wtf import FlaskForm
from server.views.forms.custom_fields import FieldGroup
from server.views.forms.validate_common import valid_password_rules
from wtforms.fields import SubmitField, PasswordField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovPasswordInput
from wtforms.validators import InputRequired, Length, ValidationError
from flask_babel import lazy_gettext as _


class PasswordsForm(FlaskForm):

    password = PasswordField(
        _("Password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer"))
        ],
    )
    confirm_password = PasswordField(
        _("Confirm password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer"))
        ],
    )

    def validate_password(self, field):
        if not valid_password_rules(field.data):
            raise ValidationError(_("Enter a password in the correct format"))

    def validate_confirm_password(self, field):
        if not valid_password_rules(field.data):
            raise ValidationError(_("Enter a password in the correct format"))


class ChangePasswordWithTokenForm(FlaskForm):

    passwords = FieldGroup(PasswordsForm)

    submit = SubmitField(_("Submit"), widget=GovSubmitInput())

    def validate_passwords(self, field):
        if field.password.data != field.confirm_password.data:
            raise ValidationError(_("Passwords do not match, try again"))
