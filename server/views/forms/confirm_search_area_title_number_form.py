from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ConfirmSearchAreaTitleNumberForm(FlaskForm):
    title_number = StringField(
        _("Add another title number"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter a title number")),
            Length(max=20, message=_("Title number must be shorter than 20 characters")),
        ],
    )

    submit = SubmitField(_("Add another"), widget=GovSubmitInput())
