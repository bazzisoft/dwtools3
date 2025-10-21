"""
Unit tests for dates module.
"""

import unittest
from datetime import datetime, timezone, date

from dwtools3.datatypes.dates import (
    date_to_unix_timestamp,
    datetime_to_unix_timestamp,
    unix_timestamp_to_datetime,
    unix_timestamp_to_date,
)


class TestDates(unittest.TestCase):
    """Tests for dates module functions."""

    def test_date_to_unix_timestamp(self):
        """Test converting various dates to Unix timestamps."""
        test_cases = [
            # (date, expected_timestamp, description)
            (date(1970, 1, 1), 0, "epoch date"),
            (date(2000, 1, 1), 946684800, "Y2K"),
            (date(2024, 1, 1), 1704067200, "2024 start"),
            (date(2025, 10, 21), 1761004800, "current date example"),
            (date(1969, 12, 31), -86400, "day before epoch"),
        ]

        for test_date, expected, description in test_cases:
            with self.subTest(description=description, date=test_date):
                result = date_to_unix_timestamp(test_date)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)

    def test_datetime_to_unix_timestamp(self):
        """Test converting various datetimes to Unix timestamps."""
        test_cases = [
            # (datetime, expected_timestamp, description)
            (datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 0, "epoch"),
            (datetime(1970, 1, 1, 1, 0, 0, tzinfo=timezone.utc), 3600, "one hour after epoch"),
            (datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 946684800, "Y2K midnight"),
            (datetime(2000, 1, 1, 12, 30, 45, tzinfo=timezone.utc), 946729845, "Y2K with time"),
            (datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc), 1718461800, "mid-2024"),
            (
                datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
                -1,
                "one second before epoch",
            ),
        ]

        for test_datetime, expected, description in test_cases:
            with self.subTest(description=description, datetime=test_datetime):
                result = datetime_to_unix_timestamp(test_datetime)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)

    def test_datetime_to_unix_timestamp_precision(self):
        """Test that fractional seconds are truncated (not rounded)."""
        test_cases = [
            (datetime(1970, 1, 1, 0, 0, 0, 500000, tzinfo=timezone.utc), 0, "0.5 seconds"),
            (datetime(1970, 1, 1, 0, 0, 1, 999999, tzinfo=timezone.utc), 1, "1.999999 seconds"),
        ]

        for test_datetime, expected, description in test_cases:
            with self.subTest(description=description):
                result = datetime_to_unix_timestamp(test_datetime)
                self.assertEqual(result, expected)

    def test_unix_timestamp_to_datetime(self):
        """Test converting various Unix timestamps to datetimes."""
        test_cases = [
            # (timestamp, expected_datetime, description)
            (0, datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "epoch"),
            (3600, datetime(1970, 1, 1, 1, 0, 0, tzinfo=timezone.utc), "one hour after epoch"),
            (946684800, datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "Y2K"),
            (1704067200, datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "2024 start"),
            (-1, datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc), "negative timestamp"),
            (-86400, datetime(1969, 12, 31, 0, 0, 0, tzinfo=timezone.utc), "day before epoch"),
        ]

        for timestamp, expected, description in test_cases:
            with self.subTest(description=description, timestamp=timestamp):
                result = unix_timestamp_to_datetime(timestamp)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, datetime)

    def test_unix_timestamp_to_datetime_returns_aware(self):
        """Test that returned datetime is timezone-aware (UTC)."""
        result = unix_timestamp_to_datetime(0)
        self.assertIsNotNone(result.tzinfo)
        self.assertEqual(result.tzinfo.tzname(result), "UTC")

    def test_unix_timestamp_to_datetime_fractional(self):
        """Test handling of fractional timestamps."""
        test_cases = [
            (0.5, datetime(1970, 1, 1, 0, 0, 0, 500000, tzinfo=timezone.utc), "half second"),
            (1.999999, datetime(1970, 1, 1, 0, 0, 1, 999999, tzinfo=timezone.utc), "microseconds"),
        ]

        for timestamp, expected, description in test_cases:
            with self.subTest(description=description):
                result = unix_timestamp_to_datetime(timestamp)
                self.assertEqual(result, expected)

    def test_unix_timestamp_to_date(self):
        """Test converting various Unix timestamps to dates."""
        test_cases = [
            # (timestamp, expected_date, description)
            (0, date(1970, 1, 1), "epoch"),
            (946684800, date(2000, 1, 1), "Y2K"),
            (1704067200, date(2024, 1, 1), "2024 start"),
            (1761004800, date(2025, 10, 21), "current date example"),
            (-86400, date(1969, 12, 31), "day before epoch"),
        ]

        for timestamp, expected, description in test_cases:
            with self.subTest(description=description, timestamp=timestamp):
                result = unix_timestamp_to_date(timestamp)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, date)

    def test_unix_timestamp_to_date_ignores_time(self):
        """Test that time component is ignored when converting to date."""
        test_cases = [
            (946684800, date(2000, 1, 1), "midnight"),
            (946729845, date(2000, 1, 1), "12:30:45 PM - same date"),
            (946771199, date(2000, 1, 1), "23:59:59 - same date"),
        ]

        for timestamp, expected, description in test_cases:
            with self.subTest(description=description):
                result = unix_timestamp_to_date(timestamp)
                self.assertEqual(result, expected)

    def test_datetime_roundtrip(self):
        """Test that datetime -> timestamp -> datetime preserves the value."""
        test_datetimes = [
            datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2000, 1, 1, 12, 30, 45, tzinfo=timezone.utc),
            datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc),
            datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        ]

        for original_dt in test_datetimes:
            with self.subTest(datetime=original_dt):
                timestamp = datetime_to_unix_timestamp(original_dt)
                recovered_dt = unix_timestamp_to_datetime(timestamp)
                # Compare without microseconds since int conversion truncates
                self.assertEqual(
                    original_dt.replace(microsecond=0), recovered_dt.replace(microsecond=0)
                )

    def test_date_roundtrip(self):
        """Test that date -> timestamp -> date preserves the value."""
        test_dates = [
            date(1970, 1, 1),
            date(2000, 1, 1),
            date(2024, 6, 15),
            date(1969, 12, 31),
        ]

        for original_date in test_dates:
            with self.subTest(date=original_date):
                timestamp = date_to_unix_timestamp(original_date)
                recovered_date = unix_timestamp_to_date(timestamp)
                self.assertEqual(original_date, recovered_date)


if __name__ == "__main__":
    unittest.main()
