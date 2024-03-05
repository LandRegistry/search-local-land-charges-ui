from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, HiddenField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput


class DefineSearchAreaForm(FlaskForm):

    saved_features = HiddenField(name="saved-features")
    submit = SubmitField(widget=GovSubmitInput())
