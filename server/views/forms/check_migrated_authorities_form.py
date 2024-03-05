from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovSelect
from wtforms.validators import InputRequired, ValidationError
from flask_babel import lazy_gettext as _


class CheckMigratedAuthoritiesForm(FlaskForm):
    organisation_search = SelectField(
        _("Enter an authority name to search"),
        default="",
        widget=GovSelect(),
        validators=[InputRequired(_('Local authority is required'))],
        validate_choice=False)

    submit = SubmitField(
        _("Check authority"),
        widget=GovSubmitInput())

    def validate_organisation_search(self, field):
        if (field.data, field.data) not in field.choices:
            raise ValidationError(_("No match found for %(search_auth)s", search_auth=field.data))
