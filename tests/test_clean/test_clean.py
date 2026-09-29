"""
Tests for cannlytics.clean
==========================
Known answers for the probe sets on which the state collectors' own
cleaners disagreed (STR-2026-0925-DATASETS-UPSTREAM-V1, U4), plus the
null-versus-zero rules.
"""
from datetime import date, datetime, timezone

import pandas as pd
import pytest

from cannlytics.clean import (
    PARTIAL_DATE_POLICIES,
    SENTINELS,
    clean_email,
    clean_phone_number,
    clean_text,
    clean_url,
    clean_zip_code,
    date_precision,
    is_placeholder,
    parse_date,
    parse_datetime,
    parse_timestamp,
    safe_float,
    smart_title_case,
)

class TestPlaceholders:

    @pytest.mark.parametrize('value', [None, float('nan'), pd.NA, pd.NaT, '', '  ', 'N/A', 'n/a', 'NA', 'None', 'nan', 'Not Published', 'Confidential', 'TBD', '--', '#N/A'])
    def test_placeholders(self, value):
        assert is_placeholder(value) is True

    @pytest.mark.parametrize('value', [0, 0.0, '0', '0.0', False, 'false', 'No', 'ND', 'active', 1, 'a'])
    def test_zero_and_false_are_values(self, value):
        # The null-versus-zero doctrine: a zero is a measurement.
        assert is_placeholder(value) is False

    def test_no_zero_or_boolean_sentinel(self):
        assert not {'0', '0.0', 'false', 'no', 'true'} & SENTINELS

class TestText:

    @pytest.mark.parametrize('value, expected', [
        ('  Green  Thumb\tIndustries ', 'Green Thumb Industries'),
        ('"Quoted Name"', 'Quoted Name'),
        ('ﬁne\u00a0leaf', 'fine leaf'),
        ('N/A', None), (None, None), (float('nan'), None), ('', None), (42, '42'),
    ])
    def test_clean_text(self, value, expected):
        assert clean_text(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('GREEN THUMB INDUSTRIES LLC', 'Green Thumb Industries LLC'),
        ('the flower co. of nyc', 'The Flower Co. of NYC'),
        ("AJ'S CANNABIS INC", "Aj's Cannabis Inc"),
        ("o'malley's dispensary", "O'Malley's Dispensary"),
        ("DON'T PANIC LLC", "Don't Panic LLC"),
        ('MCDONALD FARMS', 'McDonald Farms'),
        ('A&B HOLDINGS L.L.C.', 'A&B Holdings L.L.C.'),
        ('CURALEAF NY, LLC', 'Curaleaf NY, LLC'),
        ('Curaleaf NY, LLC', 'Curaleaf NY, LLC'),
        ('123 MAIN ST NW, SUITE 3RD', '123 Main St NW, Suite 3rd'),
        ('GROW ON MAIN', 'Grow on Main'),
        ('CASA LA ROSA', 'Casa La Rosa'),
        ('SEVEN-ELEVEN CBD', 'Seven-Eleven CBD'),
        ('THE BUD FOR US', 'The Bud for Us'),
        ('dba: The Botanist', 'dba: The Botanist'),
        ('JOHNS ISLAND GROW', 'Johns Island Grow'),
        ('N/A', None),
    ])
    def test_smart_title_case(self, value, expected):
        assert smart_title_case(value) == expected

class TestNumbers:

    @pytest.mark.parametrize('value, expected', [
        ('24.5', 24.5), ('1,234.5', 1234.5), ('24.5%', 24.5), ('$1,200', 1200.0), ('< 0.05', None), ('>100', None), ('<LOQ', None),
        ('ND', None), ('nd', None), ('Not Detected', None), ('N/A', None), (None, None),
        (0, 0.0), ('0', 0.0), (True, None), (False, None), (float('nan'), None), ('abc', None), (7, 7.0),
    ])
    def test_safe_float(self, value, expected):
        assert safe_float(value) == expected

class TestDates:

    @pytest.mark.parametrize('value, expected', [
        # The probes on which ten parse_date functions had nine behaviors.
        ('01/15/2024', '2024-01-15'), ('2024-01-15', '2024-01-15'), ('January 15, 2024', '2024-01-15'),
        ('1/5/24', '2024-01-05'), ('20240115', '2024-01-15'), ('2024-01-15T10:30:00', '2024-01-15'),
        ('2024-01-15 10:30:00', '2024-01-15'), ('Jan 15 2024', '2024-01-15'), ('15 January 2024', '2024-01-15'),
        (45306, '2024-01-15'), (45306.0, '2024-01-15'), ('45306', '2024-01-15'), (20240115, '2024-01-15'),
        ('2024-13-45', None), ('N/A', None), (None, None), ('', None), ('0', None), (0, None),
        # Partial dates are kept at the precision given (ISO 8601), never
        # completed with today's date; a date without a year cannot be placed.
        ('January 2024', '2024-01'), ('2024-01', '2024-01'), ('01/2024', '2024-01'), ('2024', '2024'),
        ('January 15', None), ('Q1 2024', None), ('2024-13', None), ('13/2024', None),
        # Beyond 2100 (and past what Windows can convert) is not a date.
        (5e10, None), (9e12, None),
        # Forms found by the 1.0.4 census of the published files.
        ('Wed Apr 17 2024 04:00:00 GMT-0400 (Eastern Daylight Time)', '2024-04-17'),
        ('Mon Dec 18 2023 03:00:00 GMT-0500 (Eastern Standard Time)', '2023-12-18'),
        ('Sat Jun 01 2019 03:52:48 GMT-0400', '2019-06-01'),
        ('03/26/202104:10', '2021-03-26'), ('2023 2:06 p.m.-08-29', '2023-08-29'),
        ('Date Tested:', None), ('24', None), ('12/152022', None), ('Spring 2024', None),
        ('Lot 2023-A', None), ('2023 batch 7', None),
        # dateutil reads these as a month; they are ambiguous (the 8th, or
        # August?) or not dates at all ('7 of 2023' is more likely a batch).
        ('8 2023', None), ('2023 8', None), ('12 2023', None), ('2023, 8', None), ('7 of 2023', None),
        ('1970-01-01', '1970-01-01'), ('12/31/1899', None), ('2101-01-01', None),
        (date(2024, 1, 15), '2024-01-15'), (datetime(2024, 1, 15, 10, 30), '2024-01-15'),
        (pd.Timestamp('2024-01-15 10:30'), '2024-01-15'), (pd.NaT, None),
        (datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc), '2024-01-15'),
        (1705312800, '2024-01-15'), (1705312800000, '2024-01-15'),
    ])
    def test_parse_date(self, value, expected):
        assert parse_date(value) == expected

    def test_dayfirst(self):
        assert parse_date('05/01/2024') == '2024-05-01'
        assert parse_date('05/01/2024', dayfirst=True) == '2024-01-05'
        assert parse_date('15/01/2024', dayfirst=True) == '2024-01-15'

    def test_timestamps(self):
        assert parse_timestamp('2024-01-15T10:30:00') == '2024-01-15T10:30:00'
        assert parse_timestamp('2024-01-15 10:30:00-05:00') == '2024-01-15T10:30:00'
        assert parse_datetime('2024-01-15') == datetime(2024, 1, 15)

    def test_excel_serial_boundary(self):
        assert parse_date(25569) == '1970-01-01'

class TestContactFields:

    @pytest.mark.parametrize('value, expected', [
        # The probes on which thirteen clean_zip_code functions had eight behaviors.
        ('12345', '12345'), ('12345-6789', '12345'), ('123456789', '12345'), ('1234', '01234'),
        (12345.0, '12345'), ('02134', '02134'), (2134, '02134'), (2134.0, '02134'), ('2134.0', '02134'),
        (' 98501 ', '98501'), (None, None), ('N/A', None), ('V6B 1A1', 'V6B 1A1'), ('v6b1a1', 'V6B 1A1'),
        ('', None), ('abc', None), ('1234567', None), (False, None), ('501', '00501'), (501, '00501'),
        ('12', None), (12, None), ('PO Box 100', None), ('Olympia, WA 98501', '98501'), ('98501 0001', '98501'),
    ])
    def test_clean_zip_code(self, value, expected):
        assert clean_zip_code(value) == expected

    def test_plus4(self):
        assert clean_zip_code('12345-6789', plus4=True) == '12345-6789'
        assert clean_zip_code('123456789', plus4=True) == '12345-6789'
        assert clean_zip_code(123456789, plus4=True) == '12345-6789'
        assert clean_zip_code(123456789) == '12345'
        assert clean_zip_code('Olympia, WA 98501-0001', plus4=True) == '98501-0001'
        assert clean_zip_code('98501', plus4=True) == '98501'

    @pytest.mark.parametrize('value, expected', [
        # The probes on which nine clean_phone_number functions had eight behaviors.
        ('(555) 123-4567', '(555) 123-4567'), ('555.123.4567', '(555) 123-4567'), ('5551234567', '(555) 123-4567'),
        ('+1 555 123 4567', '(555) 123-4567'), ('15551234567', '(555) 123-4567'), (5551234567.0, '(555) 123-4567'),
        ('555-123-4567 ext 12', '(555) 123-4567 ext. 12'), ('555-123-4567 x12', '(555) 123-4567 ext. 12'),
        ('555-1234', None), ('N/A', None), (None, None), ('', None), ('call us', None),
    ])
    def test_clean_phone_number(self, value, expected):
        assert clean_phone_number(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('Info@Example.com ', 'info@example.com'), ('not an email', None), ('a@b.co; c@d.org', 'a@b.co'),
        ('N/A', None), (None, None), ('mailto:x@y.com', 'x@y.com'), ('x@y.com (primary)', 'x@y.com'),
    ])
    def test_clean_email(self, value, expected):
        assert clean_email(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('example.com', 'https://example.com'), ('https://Example.com/', 'https://example.com'),
        ('http://example.com/coa?id=1', 'http://example.com/coa?id=1'), ('ftp://x.com', None),
        ('not a url', None), ('N/A', None), (None, None), ('www.lab.com/results.', 'https://www.lab.com/results'),
    ])
    def test_clean_url(self, value, expected):
        assert clean_url(value) == expected

class TestPartialDates:
    """Where partial dates come from (Oregon's monthly results; COAs that
    print EXP 03/2026) and the conventions for completing them."""

    @pytest.mark.parametrize('value, keep, start, end, precision', [
        ('January 2024', '2024-01', '2024-01-01', '2024-01-31', 'month'),
        ('Feb 2024', '2024-02', '2024-02-01', '2024-02-29', 'month'),      # leap year
        ('Feb 2023', '2023-02', '2023-02-01', '2023-02-28', 'month'),
        ('03/2026', '2026-03', '2026-03-01', '2026-03-31', 'month'),       # EXP 03/2026
        ('2026/3', '2026-03', '2026-03-01', '2026-03-31', 'month'),
        ('2024', '2024', '2024-01-01', '2024-12-31', 'year'),
        ('2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15', 'day'),   # full dates are untouched
    ])
    def test_policies(self, value, keep, start, end, precision):
        assert parse_date(value) == keep
        assert parse_date(value, partial='start') == start
        assert parse_date(value, partial='end') == end
        assert date_precision(value) == precision

    def test_none_declines_partial_dates_only(self):
        assert parse_date('January 2024', partial=None) is None
        assert parse_date('2024-01-15', partial=None) == '2024-01-15'

    def test_datetimes_cannot_be_partial(self):
        assert parse_datetime('January 2024') is None
        assert parse_datetime('January 2024', partial='end') == datetime(2024, 1, 31)
        assert parse_timestamp('2024', partial='start') == '2024-01-01T00:00:00'
        with pytest.raises(ValueError):
            parse_datetime('January 2024', partial='keep')

    def test_unknown_policy_is_an_error(self):
        assert 'keep' in PARTIAL_DATE_POLICIES
        with pytest.raises(ValueError):
            parse_date('January 2024', partial='middle')

    def test_precision_of_non_dates(self):
        assert date_precision('N/A') is None and date_precision('Q1 2024') is None and date_precision(None) is None

    def test_pandas_reads_mixed_precision(self):
        series = pd.Series([parse_date(v) for v in ('2024-01-15', 'January 2024', '2024')])
        assert list(pd.to_datetime(series, format='ISO8601').dt.day) == [15, 1, 1]

    def test_census_forms_keep_their_time_and_precision(self):
        # The wall-clock time is kept; dateutil's inverted GMT sign is never applied.
        assert parse_timestamp('Wed Apr 17 2024 04:00:00 GMT-0400 (Eastern Daylight Time)') == '2024-04-17T04:00:00'
        assert parse_timestamp('2023 2:06 p.m.-08-29') == '2023-08-29T14:06:00'
        # A full date with a time in the wrong place is a day, not a bare year.
        assert date_precision('2023 2:06 p.m.-08-29') == 'day'
        assert date_precision('Mar. 2026') == 'month' and date_precision('2026 March') == 'month'
