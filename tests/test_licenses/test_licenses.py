"""
Tests for cannlytics.licenses
=============================
The identifier is stored as issued; the key is for matching. Known
answers are the probes on which the results-side and licenses-side
normalizers disagreed (STR-2026-0925-DATASETS-UPSTREAM-V1, U1).
"""
import pytest

from cannlytics.licenses import (
    categorize_license_type,
    is_active_status,
    license_key,
    license_match_level,
    normalize_license_number,
    split_license_numbers,
    standardize_license_status,
)

class TestIdentifier:

    @pytest.mark.parametrize('value, expected', [
        ('C10-0000123-LIC', 'C10-0000123-LIC'),
        ('  c10-0000123-lic ', 'C10-0000123-LIC'),
        ('"MMTC-2015-0001"', 'MMTC-2015-0001'),
        ('MMTC 2015 0001', 'MMTC 2015 0001'),          # kept as written; the key reconciles it
        ('OCM-RETL-23-000123', 'OCM-RETL-23-000123'),
        ('LIC-000123', 'LIC-000123'),                   # a prefix is part of the identifier
        ('  LIC-000123  ', 'LIC-000123'),
        (12345.0, '12345'), (412345, '412345'), (12.5, '12.5'), (True, None), (float('nan'), None),
        ('N/A', None), (None, None), ('', None), ('  ', None), ('nan', None),
    ])
    def test_normalize_license_number_is_verbatim(self, value, expected):
        assert normalize_license_number(value) == expected

    def test_leading_zeros_are_never_dropped_from_the_identifier(self):
        assert normalize_license_number('C10-0000936-LIC') == 'C10-0000936-LIC'

    @pytest.mark.parametrize('value, expected', [
        ('C10-0000123-LIC; C11-0000456-LIC', ['C10-0000123-LIC', 'C11-0000456-LIC']),
        ('A-1, A-2 / A-3', ['A-1', 'A-2', 'A-3']),
        ('A-1 and A-1', ['A-1']),
        ('single', ['SINGLE']), ('N/A', []), (None, []),
    ])
    def test_split(self, value, expected):
        assert split_license_numbers(value) == expected

class TestKey:

    @pytest.mark.parametrize('value, state, expected', [
        # The California disagreement, now one key from both spellings.
        ('C10-0000123-LIC', 'ca', 'C10-123'), ('c10-0000123-lic', 'ca', 'C10-123'),
        ('C10-0000123', 'ca', 'C10-123'), ('C10-123', 'ca', 'C10-123'), ('C10 0000123', 'ca', 'C10-123'),
        ('DCC-LIC-1234567', 'ca', 'DCC-LIC-1234567'),
        # Florida: hyphens, spaces, a state prefix, a label.
        ('MMTC-2015-0001', 'fl', 'MMTC-2015-1'), ('MMTC 2015 0001', 'fl', 'MMTC-2015-1'),
        ('FL LICENSE # CMTL-0003', 'fl', 'CMTL-3'), ('FL-CMTL-0003', 'fl', 'CMTL-3'),
        # New York: a hash separator and a site suffix.
        ('OCM-RETL-23-000123', 'ny', 'OCM-RETL-23-123'), ('OCM-CPL # 00005', 'ny', 'OCM-CPL-5'),
        ('OCM-MICR-21-000058-P1', 'ny', 'OCM-MICR-21-58'),
        # Labels and suffixes.
        ('LIC# 00000034DCOD00007550', 'ma', '34DCOD00007550'), ('License No. MR281236', 'ma', 'MR281236'),
        ('MR281236', 'ma', 'MR281236'), ('  LIC-000123  ', 'ma', '123'), ('LIC-000000-000123', 'ny', '0-123'),
        ('412345', 'wa', '412345'), (412345.0, 'wa', '412345'), ('050-1005678', 'or', '50-1005678'), ('#123', 'or', '123'),
        # A label must end where a word ends; these are numbers, not labels.
        ('DEAL-0042', 'ca', 'DEAL-42'), ('NORTH-0001', 'ca', 'NORTH-1'), ('REGAL-7', 'ca', 'REGAL-7'),
        ('PUBLIC-0001', 'ca', 'PUBLIC-1'), ('No. 0012345', 'ca', '12345'), ('C10-0000936LIC', 'ca', 'C10-936'),
        ('Registration # AU-C-0001', 'mi', 'AU-C-1'),
        # Florida's non-license identifiers are rejected in Florida only.
        ('IA15009-04', 'ca', 'IA15009-4'),
        ('AU-C-000123', 'md', 'AU-C-123'), ('CCB-0001', 'nv', 'CCB-1'),
        # Not license numbers.
        ('N/A', 'ca', None), (None, 'ca', None), ('', None, None), ('XXXXXXX', 'fl', None),
        ('10D1094068', 'fl', None), ('IA15009-04', 'fl', None), ('Retail Dispensary', 'ca', None),
    ])
    def test_license_key(self, value, state, expected):
        assert license_key(value, state) == expected

    def test_both_sides_of_a_join_agree(self):
        # What the results side and the licenses side used to produce.
        assert license_key('C10-0000123') == license_key('C10-123') == license_key('C10-0000123-LIC')

    def test_key_is_never_the_identifier(self):
        raw = 'C10-0000936-LIC'
        assert normalize_license_number(raw) == raw and license_key(raw) == 'C10-936'

class TestTypesAndStatuses:

    @pytest.mark.parametrize('value, expected', [
        ('Retail', 'Retail/Dispensary'), ('Adult-Use Retailer', 'Retail/Dispensary'), ('Medical Dispensary', 'Retail/Dispensary'),
        ('Cultivator - Tier 2', 'Cultivation'), ('Grower', 'Cultivation'), ('Manufacturer', 'Manufacturing/Processing'),
        ('Processor', 'Manufacturing/Processing'), ('Testing Laboratory', 'Testing Laboratory'), ('Lab', 'Testing Laboratory'),
        ('Distributor', 'Distribution/Transport'), ('Delivery', 'Distribution/Transport'),
        ('Microbusiness', 'Microbusiness'), ('Vertically Integrated', 'Vertically Integrated'),
        ('Event Organizer', 'Other/Unclassified'), (None, 'Other/Unclassified'), ('N/A', 'Other/Unclassified'),
    ])
    def test_categorize_license_type(self, value, expected):
        assert categorize_license_type(value) == expected

    @pytest.mark.parametrize('value, expected', [
        ('Active', 'active'), ('ACTIVE', 'active'), ('Issued', 'active'), ('Approved', 'active'),
        ('License Issued', 'active'), ('Active - Operating', 'active'), ('Expired', 'expired'),
        ('Revoked', 'revoked'), ('Suspended', 'suspended'), ('Pending', 'pending'),
        ('Renewal in Process', 'pending'), ('Provisional', 'provisional'), ('Inactive', 'inactive'),
        ('Surrendered', 'surrendered'), ('Cancelled', 'cancelled'), ('Denied', 'denied'),
        ('Active - Pending Renewal', 'active'), ('Not Active', 'inactive'), ('Expired - Renewal Pending', 'expired'),
        (None, 'unknown'), ('Bogus', 'unknown'), ('N/A', 'unknown'),
    ])
    def test_standardize_license_status(self, value, expected):
        assert standardize_license_status(value) == expected

    def test_is_active_status(self):
        assert is_active_status('Active (Issued)') and is_active_status('operating') and is_active_status('Current')
        assert not is_active_status('Expired') and not is_active_status(None) and not is_active_status('Pending')

class TestMergeCascade:

    @pytest.mark.parametrize('value, state, expected', [
        ('MMTC-2015-0001', 'fl', 'MMTC20150001'), ('MMTC 2015 0001', 'fl', 'MMTC20150001'),
        ('MMTC20150001', 'fl', 'MMTC20150001'), ('C10-0000936-LIC', 'ca', 'C100000936'), ('N/A', 'ca', None),
    ])
    def test_compact_key(self, value, state, expected):
        assert license_key(value, state, compact=True) == expected

    @pytest.mark.parametrize('left, right, state, level', [
        ('C10-0000936-LIC', ' c10-0000936-lic ', 'ca', 'identifier'),
        ('C10-0000936-LIC', 'C10-936', 'ca', 'key'),
        ('Lic# C10 0000936', 'C10-0000936', 'ca', 'key'),
        ('MMTC-2015-0001', 'MMTC20150001', 'fl', 'compact'),
        ('C10-0000936-LIC', 'C11-0000936-LIC', 'ca', None),
        (None, 'C10-936', 'ca', None), ('N/A', 'N/A', 'ca', None),
    ])
    def test_match_level(self, left, right, state, level):
        assert license_match_level(left, right, state) == level

    def test_matching_never_rewrites_the_identifier(self):
        raw = 'MMTC-2015-0001'
        license_match_level(raw, 'MMTC20150001', 'fl')
        assert normalize_license_number(raw) == raw
