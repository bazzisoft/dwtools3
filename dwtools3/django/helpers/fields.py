"""
Useful custom model fields.
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class StrippedCharField(models.CharField):
    """
    Regular ``CharField`` but stripped of leading/trailing whitespace.
    """
    description = _("String stripped of whitespace (up to %(max_length)s)")

    def to_python(self, value):
        ret = super().to_python(value)
        return ret.strip() if ret is not None else ret


class StrippedTextField(models.TextField):
    """
    Regular ``TextField`` but stripped of leading/trailing whitespace.
    """
    description = _("Text stripped of whitespace")

    def to_python(self, value):
        ret = super().to_python(value)
        return ret.strip() if ret is not None else ret

    def get_prep_value(self, value):
        ret = super().get_prep_value(value)
        return ret.strip() if ret is not None else ret
