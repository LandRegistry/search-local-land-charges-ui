from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput, GovTextInput
from wtforms.validators import InputRequired, ValidationError
from flask_babel import lazy_gettext as _


class SearchByCoordinatesForm(FlaskForm):
    eastings = StringField(
        _("Enter X coordinates (Eastings)"),
        description=_("Coordinates must be of a numerical value"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_('Enter X coordinates'))
        ])

    northings = StringField(
        _("Enter Y coordinates (Northings)"),
        description=_("Coordinates must be of a numerical value"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_('Enter Y coordinates'))
        ])

    submit = SubmitField(
        _("Search"),
        widget=GovSubmitInput())

    def validate_eastings(self, field):
        if not is_valid_coord(field.data):
            raise ValidationError(_('Enter coordinates in the correct format'))

    def validate_northings(self, field):
        if not is_valid_coord(field.data):
            raise ValidationError(_('Enter coordinates in the correct format'))


def is_valid_coord(coord):
    coord_float = None
    try:
        coord_float = float(coord)
    except ValueError:
        return False
    if coord_float > 800000:
        return False
    return True
