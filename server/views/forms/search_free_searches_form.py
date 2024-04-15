from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class SearchFreeSearchesForm(FlaskForm):
    search_term = StringField(
        _("Find a result by Search ID"),
        widget=GovTextInput(),
        validators=[
            DataRequired(message=_("You have entered an invalid Search ID. Check it and try again")),
            Length(max=80, message=_("Search ID must be shorter than 80 characters")),
        ],
    )

    submit = SubmitField(_("Search"), widget=GovSubmitInput())

    def validate_search_term(self, field):
        if not field.data.strip().isnumeric():
            raise ValidationError(_("You have entered an invalid Search ID. Check it and try again"))
