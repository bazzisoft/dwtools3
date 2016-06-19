"""
Useful custom model fields.
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError


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


class SeparatedValuesField(models.TextField):
    """
    A textfield containing a list of values, separated by a delimiter.
    """
    description = _("A list of values separated by a delimiter")

    def __init__(self, delimiter=',', *args, **kwargs):
        self.delimiter = delimiter
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.delimiter != ',':
            kwargs['delimiter'] = self.delimiter
        return name, path, args, kwargs

    def _parse_value(self, value):
        if value is None:
            return None
        elif value == '':
            return []
        else:
            return value.split(self.delimiter)

    def from_db_value(self, value, expression, connection, context):
        return self._parse_value(value)

    def to_python(self, value):
        if isinstance(value, (list, tuple)):
            return value
        else:
            return self._parse_value(value)

    def get_prep_value(self, value):
        return self.delimiter.join(value)

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self._choices and value not in self.empty_values:
            choice_keys = frozenset(k for k, v in self.choices)
            for v in value:
                if v not in choice_keys:
                    raise ValidationError(
                        self.error_messages['invalid_choice'],
                        code='invalid_choice',
                        params={'value': repr(v)},
                    )

        if value is None and not self.null:
            raise ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise ValidationError(self.error_messages['blank'], code='blank')

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField,
                    'choices_form_class': forms.TypedMultipleChoiceField,
                    'coerce': lambda x: x}
        if self.choices:
            defaults['widget'] = forms.SelectMultiple
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_choices(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs['include_blank'] = False
        return super().get_choices(*args, **kwargs)
