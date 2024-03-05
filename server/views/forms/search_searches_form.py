from wtforms import Form
from wtforms.fields import StringField, SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _


class SearchSearchesForm(Form):
    search_term = StringField(
        _("Search by reference or area"),
        widget=GovTextInput(),
        validators=[
            DataRequired(message=_('Enter a reference or area')),
            Length(max=80, message=_('Reference or area must be shorter than 80 characters'))
        ])

    submit = SubmitField(
        _("Search"),
        widget=GovSubmitInput())
