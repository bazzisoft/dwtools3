"""
Utility functions for working with dates and timezones.
"""
from datetime import datetime, timedelta, tzinfo, time


class UTCTZInfo(tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    ZERO = timedelta(0)

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO


UTC = UTCTZInfo()
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def date_to_unix_timestamp(dt):
    dt = datetime.combine(dt, time.min.replace(tzinfo=UTC))
    return datetime_to_unix_timestamp(dt)


def datetime_to_unix_timestamp(dt):
    return int((dt - EPOCH).total_seconds())


def unix_timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, UTC)


def unix_timestamp_to_date(timestamp):
    return unix_timestamp_to_datetime(timestamp).date()
