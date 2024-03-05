from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.validators import InputRequired, Length
from flask_babel import lazy_gettext as _


class SearchByTitleNumberForm(FlaskForm):
    title_number = StringField(
        _("Search by title number"),
        description=_("You can find the title number on HM Land Registry documents, including copies of the register."),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_('Enter a title number')),
            Length(max=20, message=_('Title number must be shorter than 20 characters'))
        ])

    submit = SubmitField(
        _("Search"),
        widget=GovSubmitInput())
