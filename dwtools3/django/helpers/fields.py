"""
Useful custom model fields.
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _


# ASCII 00-31 mapped to None for translation
# Allow ASCII 10 = \n and 13 = \r
CONTROL_CHAR_MAP = dict.fromkeys(range(32))
del CONTROL_CHAR_MAP[10]
del CONTROL_CHAR_MAP[13]


class StrippedCharField(models.CharField):
    """
    Regular ``CharField`` but stripped of leading/trailing whitespace.
    """
    description = _("String stripped of whitespace (up to %(max_length)s)")

    def to_python(self, value):
        ret = super().to_python(value)
        return ret.strip().translate(CONTROL_CHAR_MAP) if ret is not None else ret


class StrippedTextField(models.TextField):
    """
    Regular ``TextField`` but stripped of leading/trailing whitespace.
    """
    description = _("Text stripped of whitespace")

    def to_python(self, value):
        ret = super().to_python(value)
        return ret.strip().translate(CONTROL_CHAR_MAP) if ret is not None else ret

    def get_prep_value(self, value):
        ret = super().get_prep_value(value)
        return ret.strip().translate(CONTROL_CHAR_MAP) if ret is not None else ret
