from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields import HiddenField, SubmitField


class SearchResultsForm(FlaskForm):
    enc_search_id = HiddenField(name="enc-search-id")
    submit = SubmitField(_("Continue"), widget=GovSubmitInput())
