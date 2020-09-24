# -*- coding: utf-8 -*-
"""
Utility functions to convert back and forth between a timestring and timedelta.
"""
import re
from datetime import timedelta

from django.core.exceptions import ValidationError


TIME_FORMAT = (r"(?:(?P<weeks>\d+)\W*(?:weeks?|w),?)?\W*(?:(?P<days>\d+)\W*(?:days?|d),?)?\W*"
               r"(?:(?P<hours>\d+):(?P<minutes>\d+)(?::(?P<seconds>\d+)"
               r"(?:\.(?P<microseconds>\d+))?)?)?")
TIME_FORMAT_RE = re.compile(TIME_FORMAT)


def str_to_timedelta(td_str):
    """
    Returns a timedelta parsed from the native string output of a timedelta.

    Timedelta displays in the format ``X day(s), H:MM:SS.ffffff``
    Both the days section and the microseconds section are optional and ``days``
    is singular in cases where there is only one day.
    """
    # Treat floats are hours and fractions of hours
    try:
        hours = float(td_str)
        return timedelta(hours=hours)
    except ValueError:
        pass

    # Empty strings or None corresponds to NULL
    if not td_str:
        return None

    time_matches = TIME_FORMAT_RE.match(td_str)
    time_groups = time_matches.groupdict()

    # If passed an invalid string, the regex will return all None's, so as
    # soon as we get a non-None value, we are more confident the string
    # is valid (possibly some invalid numeric formats this will not catch.
    # Refs #11
    is_valid = False
    for key in time_groups.keys():
        if time_groups[key] is not None:
            is_valid = True
            time_groups[key] = int(time_groups[key])
        else:
            time_groups[key] = 0

    if not is_valid:
        raise ValidationError(u"Invalid timedelta string, '{0}'".format(td_str))

    time_groups["days"] = time_groups["days"] + (time_groups["weeks"] * 7)

    return timedelta(
        days=time_groups["days"],
        hours=time_groups["hours"],
        minutes=time_groups["minutes"],
        seconds=time_groups["seconds"],
        microseconds=time_groups["microseconds"]
    )


def format_duration_hhmm(d):
    """
    Utility function to format durations in the widget as hh:mm
    """
    if d is None:
        return ''
    elif isinstance(d, str):
        return d

    hours = d.days * 24 + d.seconds // 3600
    minutes = int(round((d.seconds % 3600) / 60))
    return '{}:{:02}'.format(hours, minutes)
