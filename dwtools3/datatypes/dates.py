"""
Utility functions for working with dates and timezones.
"""

from datetime import datetime, timezone, time
import zoneinfo


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def date_to_unix_timestamp(dt):
    dt = datetime.combine(dt, time.min.replace(tzinfo=timezone.utc))
    return datetime_to_unix_timestamp(dt)


def datetime_to_unix_timestamp(dt):
    return int((dt - EPOCH).total_seconds())


def unix_timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)


def unix_timestamp_to_date(timestamp):
    return unix_timestamp_to_datetime(timestamp).date()


def common_timezones():
    """
    Returns a list of common timezone names, similar to pytz.common_timezones.
    """
    return sorted(
        [
            tz
            for tz in zoneinfo.available_timezones()
            if (
                "/" in tz
                and not tz.startswith(("Etc/", "SystemV/", "Mexico/", "Brazil/", "Chile/"))
            )
            or tz in ("UTC", "GMT")
        ]
    )
