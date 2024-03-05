from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.validators import InputRequired
from flask_babel import lazy_gettext as _


class SearchByInspireIDForm(FlaskForm):
    inspire_id = StringField(
        _("Enter a local land charge INSPIRE ID"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_('Enter an INSPIRE ID'))
        ])

    submit = SubmitField(
        _("Search"),
        widget=GovSubmitInput())
