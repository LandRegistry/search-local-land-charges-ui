from flask_wtf import FlaskForm
from server.views.forms.custom_fields import FieldGroup
from server.views.forms.validate_common import valid_password_rules
from wtforms.fields import SubmitField, PasswordField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovPasswordInput
from wtforms.validators import InputRequired, Length, ValidationError
from flask_babel import lazy_gettext as _


class NewPasswordsForm(FlaskForm):
    new_password = PasswordField(
        _("New password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer"))
        ],
    )
    confirm_new_password = PasswordField(
        _("Confirm new password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer"))
        ],
    )

    def validate_new_password(self, field):
        if not valid_password_rules(field.data):
            raise ValidationError(_("Enter a password in the correct format"))

    def validate_confirm_new_password(self, field):
        if not valid_password_rules(field.data):
            raise ValidationError(_("Enter a password in the correct format"))


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        _("Current password"),
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message=_("Enter a password")),
            Length(max=256, message=_("Password must be 256 characters or fewer"))
        ],
    )

    new_passwords = FieldGroup(NewPasswordsForm)

    submit = SubmitField(_("Change password"), widget=GovSubmitInput())

    def validate_new_passwords(self, field):
        if field.new_password.data != field.confirm_new_password.data:
            raise ValidationError(_("Passwords do not match, try again"))
