"""
DurationField form field to store datetime.timedelta objects.

Works with Django ``models.DurationField``.

Borrowed from https://github.com/johnpaulett/django-durationfield.


Dependencies
------------
None.


Installation
------------
None.


Usage
-----

In your models::

    from django.db import models

    class Time(models.Model):
        ...
        duration = models.DurationField()
        ...


In your forms::

    from dwtools3.django.duration.forms import DurationField

    class MyForm(forms.ModelForm):
        duration = DurationField()


Enter time values as::

    3 days 2:20:10
    3d 2:20:10.123456
"""
from .forms import DurationField
from .widgets import DurationInput
from .utils import format_duration_hhmm
