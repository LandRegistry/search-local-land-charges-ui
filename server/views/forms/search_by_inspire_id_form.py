from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired


class SearchByInspireIDForm(FlaskForm):
    inspire_id = StringField(
        _("Enter a local land charge INSPIRE ID"),
        widget=GovTextInput(),
        validators=[InputRequired(message=_("Enter an INSPIRE ID"))],
    )

    submit = SubmitField(_("Search"), widget=GovSubmitInput())
