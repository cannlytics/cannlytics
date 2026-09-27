"""
Tests for date/time utilities in cannlytics.utils.utils
========================================================
Covers: format_iso_date, get_date_range, get_timestamp.
"""
import pytest
from cannlytics.utils.utils import format_iso_date, get_date_range, get_timestamp

class TestFormatIsoDate:

    def test_basic(self):
        assert format_iso_date('3/22/2026') == '2026-03-22'

    def test_single_digit_month_day(self):
        assert format_iso_date('1/5/2026') == '2026-01-05'

    def test_two_digit_year(self):
        assert format_iso_date('12/25/26') == '2026-12-25'

    def test_custom_separator(self):
        assert format_iso_date('03-22-2026', sep='-') == '2026-03-22'

class TestGetDateRange:

    def test_single_day(self):
        result = get_date_range('2026-01-01', '2026-01-01')
        assert len(result) == 1
        assert result[0] == ('2026-01-01', '2026-01-02')

    def test_multi_day(self):
        result = get_date_range('2026-01-01', '2026-01-03')
        assert len(result) == 3

    def test_tuples_are_consecutive(self):
        result = get_date_range('2026-03-20', '2026-03-22')
        assert result[0] == ('2026-03-20', '2026-03-21')
        assert result[1] == ('2026-03-21', '2026-03-22')
        assert result[2] == ('2026-03-22', '2026-03-23')

class TestGetTimestamp:

    def test_returns_iso_string(self):
        ts = get_timestamp()
        assert 'T' in ts
        assert len(ts) > 10

    def test_utc_default(self):
        ts = get_timestamp(zone='utc')
        assert '+00:00' in ts or 'UTC' in ts

    def test_state_abbreviation(self):
        ts = get_timestamp(zone='CA')
        assert isinstance(ts, str)
        assert 'T' in ts

    def test_specific_date(self):
        ts = get_timestamp(date='2026-03-22')
        assert '2026-03-22' in ts

    def test_past_minutes(self):
        now = get_timestamp()
        past = get_timestamp(past=60)
        # Past timestamp should be earlier (lexicographically smaller).
        assert past < now

    def test_future_minutes(self):
        now = get_timestamp()
        future = get_timestamp(future=60)
        assert future > now
