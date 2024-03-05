from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, HiddenField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from flask_babel import lazy_gettext as _


class SearchResultsForm(FlaskForm):

    enc_search_id = HiddenField(name="enc-search-id")
    submit = SubmitField(_("Pay now"), widget=GovSubmitInput())
