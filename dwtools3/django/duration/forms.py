from django.forms import ValidationError
from django.forms.fields import Field
from django.utils.translation import ugettext_lazy as _

from .utils import str_to_timedelta
from .widgets import DurationInput


class DurationField(Field):
    widget = DurationInput

    default_error_messages = {
        "invalid": _("Enter a valid duration."),
    }

    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Returns a datetime.timedelta object.
        """
        super(DurationField, self).clean(value)
        try:
            return str_to_timedelta(value)
        except ValueError:
            raise ValidationError(self.default_error_messages["invalid"])

    def to_python(self, value):
        try:
            return str_to_timedelta(value)
        except ValueError:
            raise ValidationError(self.default_error_messages["invalid"])
