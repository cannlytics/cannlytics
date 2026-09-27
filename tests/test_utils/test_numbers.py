"""
Tests for numeric utilities in cannlytics.utils.utils
======================================================
Covers: convert_to_numeric.
"""
import pytest
from cannlytics.utils.utils import convert_to_numeric

class TestConvertToNumeric:

    def test_integer_string(self):
        assert convert_to_numeric('42') == 42.0

    def test_float_string(self):
        assert convert_to_numeric('3.14') == 3.14

    def test_non_numeric_returns_original(self):
        assert convert_to_numeric('hello') == 'hello'

    def test_strip_non_numeric(self):
        assert convert_to_numeric('$1,234.56', strip=True) == 1234.56

    def test_strip_percent(self):
        assert convert_to_numeric('24.5%', strip=True) == 24.5

    def test_empty_string(self):
        assert convert_to_numeric('') == ''

    def test_strip_empty_becomes_original(self):
        result = convert_to_numeric('abc', strip=True)
        assert result == 'abc' or result == ''

    def test_none_returns_none(self):
        assert convert_to_numeric(None) is None

    def test_negative_number(self):
        assert convert_to_numeric('-5.5') == -5.5
