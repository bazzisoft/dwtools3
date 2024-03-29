# pylint: disable=consider-using-f-string
from datetime import timedelta

from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils import formats
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe


class DurationInput(TextInput):
    def __init__(self, attrs=None, to_string_fn=None):
        self.to_string_fn = to_string_fn
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""

        extra_attrs = dict(self.attrs or {}, type=self.input_type, name=name)
        final_attrs = self.build_attrs(attrs, extra_attrs)
        if value != "":
            # Only add the 'value' attribute if a value is non-empty.
            if isinstance(value, int):
                value = timedelta(microseconds=value)

            # Otherwise, we've got a timedelta already
            if self.to_string_fn:
                final_attrs["value"] = force_str(self.to_string_fn(value))
            else:
                final_attrs["value"] = force_str(formats.localize_input(value))
        return mark_safe("<input%s />" % flatatt(final_attrs))
