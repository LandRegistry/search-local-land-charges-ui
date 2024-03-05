from flask_wtf import FlaskForm
from server.views.forms.custom_fields import FieldGroup
from server.views.forms.validate_common import valid_password_rules
from wtforms.fields import SubmitField, StringField, PasswordField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput, GovPasswordInput
from wtforms.validators import Email, InputRequired, Length, ValidationError
from flask_babel import lazy_gettext as _


class EmailAddressesForm(FlaskForm):

    email_address = StringField(
        _("Email address"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter an email address")),
            Length(max=256, message=_("Email address must be 256 characters or fewer")),
            Email(message=_("Enter an email address in the correct format, like name@example.com"))
        ],
    )

    confirm_email_address = StringField(
        _("Confirm email address"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter an email address")),
            Length(max=256, message=_("Email address must be 256 characters or fewer")),
            Email(message=_("Enter an email address in the correct format, like name@example.com"))
        ],
    )


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


class RegisterForm(FlaskForm):

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

    email_addresses = FieldGroup(EmailAddressesForm)

    passwords = FieldGroup(PasswordsForm)

    submit = SubmitField(_("Submit"), widget=GovSubmitInput())

    def validate_email_addresses(self, field):
        if field.email_address.data != field.confirm_email_address.data:
            raise ValidationError(_("Email addresses do not match, try again"))

    def validate_passwords(self, field):
        if field.password.data != field.confirm_password.data:
            raise ValidationError(_("Passwords do not match, try again"))
