import re
import typing
from dataclasses import field, make_dataclass

from flask_babel import lazy_gettext as _
from marshmallow import Schema, post_dump, pre_load

from server.services.charge_id_utils import calc_display_id
from server.services.datetime_formatter import format_date

default_text = _("Not provided")


class BaseSchema(Schema):
    """Base schema class to auto (de)hyphen the field names."""

    @pre_load
    def preload_process(self, data, **kwargs):
        return {key.replace("-", "_"): value for key, value in data.items()}

    @post_dump
    def postdump_process(self, data, **kwargs):
        return {key.replace("_", "-"): value for key, value in data.items()}


def jsonnamedlist(schema, name, fields, **kwargs):
    """Modified namedlist to support to_json and from_json."""

    def to_json(self):
        return schema.dump(self)

    def from_json(json_dict):
        return schema.load(json_dict)

    def from_json_list(json_dict):
        return schema.load(json_dict, many=True)

    def format_field_for_display(self, field):
        field = getattr(self, field)
        if field:
            return field
        return default_text

    def format_date_for_display(self, date, default=default_text, translate=True):
        date = getattr(self, date)
        if date:
            return format_date(date, translate)
        return default

    def format_date_for_screen_reader(self, date, default=default_text):
        date = getattr(self, date)
        if date:
            return date.strftime("%d %B %Y %I %M %p")
        return default

    def format_money_field_for_display(self, field):
        field = getattr(self, field)
        if field:
            return "{:,.2f}".format(float(field))
        return default_text

    def format_llc_ref_for_display(self, llc_id):
        llc_id = getattr(self, llc_id)
        if llc_id:
            return calc_display_id(llc_id)
        return llc_id

    obj = make_dataclass(
        name,
        [
            (field_name.strip(), typing.Any, field(default=kwargs["default"]))
            for field_name in re.split(r"\s*,\s*", fields)
        ],
    )

    obj.to_json = to_json
    obj.from_json = from_json
    obj.from_json_list = from_json_list
    obj.format_field_for_display = format_field_for_display
    obj.format_date_for_display = format_date_for_display
    obj.format_date_for_screen_reader = format_date_for_screen_reader
    obj.format_money_field_for_display = format_money_field_for_display
    obj.format_llc_ref_for_display = format_llc_ref_for_display
    obj.schema = schema

    return obj
