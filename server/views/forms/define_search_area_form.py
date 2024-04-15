from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields import HiddenField, SubmitField


class DefineSearchAreaForm(FlaskForm):
    saved_features = HiddenField(name="saved-features")
    submit = SubmitField(widget=GovSubmitInput())
