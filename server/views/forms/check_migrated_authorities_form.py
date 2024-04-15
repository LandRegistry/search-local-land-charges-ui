from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSelect, GovSubmitInput
from wtforms.fields import SelectField, SubmitField
from wtforms.validators import InputRequired, ValidationError


class CheckMigratedAuthoritiesForm(FlaskForm):
    organisation_search = SelectField(
        "",
        default="",
        widget=GovSelect(),
        validators=[InputRequired(_("Enter a local authority"))],
        validate_choice=False,
    )

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def validate_organisation_search(self, field):
        if field.data.lower() not in [value.lower() for value, _ in field.choices]:
            raise ValidationError(
                _("No match found for %(search_auth)s", search_auth=field.data)
            )
