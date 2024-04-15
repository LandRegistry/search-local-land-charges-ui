import itertools

from wtforms.fields.core import Field
from wtforms.utils import unset_value

from server.views.forms.custom_widgets import FieldGroupWidget


class FieldGroup(Field):
    """
    Encapsulate a form as a field in another form.

    :param form_class:
        A subclass of Form that will be encapsulated.
    :param separator:
        A string which will be suffixed to this field's name to create the
        prefix to enclosed fields. The default is fine for most uses.
    """

    widget = FieldGroupWidget()

    def __init__(self, form_class, label=None, validators=None, separator="-", **kwargs):
        super().__init__(label, validators, **kwargs)
        self.form_class = form_class
        self.separator = separator
        self.errors = []
        self._obj = None
        if self.filters:
            raise TypeError("FormField cannot take filters, as the encapsulated" " data is not mutable.")

    def process(self, formdata, data=unset_value, extra_filters=None):
        if extra_filters:
            raise TypeError("FormField cannot take filters, as the encapsulated" "data is not mutable.")

        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
            self._obj = data

        self.object_data = data

        prefix = self.name + self.separator
        if isinstance(data, dict):
            self.form = self.form_class(formdata=formdata, prefix=prefix, **data)
        else:
            self.form = self.form_class(formdata=formdata, obj=data, prefix=prefix)

    def validate(self, form, extra_validators=()):
        self.errors = []

        chain = itertools.chain(self.validators, extra_validators)
        self._run_validation_chain(form, chain)

        if len(self.errors) > 0:
            self.errors = {self.name: self.errors}
            self.errors["first_child_name"] = next(iter(self.form)).name
        else:
            self.errors = {}
            if not self.form.validate():
                self.errors.update(self.form.errors)

        return len(self.errors.keys()) == 0

    def populate_obj(self, obj, name):
        candidate = getattr(obj, name, None)
        if candidate is None:
            if self._obj is None:
                raise TypeError(
                    "populate_obj: cannot find a value to populate from" " the provided obj or input data/defaults"
                )
            candidate = self._obj

        self.form.populate_obj(candidate)
        setattr(obj, name, candidate)

    def __iter__(self):
        return iter(self.form)

    def __getitem__(self, name):
        return self.form[name]

    def __getattr__(self, name):
        return getattr(self.form, name)

    @property
    def data(self):
        return self.form.data
