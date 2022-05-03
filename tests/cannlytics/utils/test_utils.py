"""
Test General Utility Functions
Copyright (c) 2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/2/2022
Updated: 5/2/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
import sys
sys.path.append('./')
sys.path.append('../../../')
from cannlytics.utils.utils import (
    camelcase,
    clean_column_strings,
    clean_dictionary,
    clean_nested_dictionary,
    get_keywords,
    get_random_string,
    get_timestamp,
    remove_dict_fields,
    remove_dict_nulls,
    snake_case,
    update_dict,
)
import pandas as pd


def test_camelcase():
    """Test turning a string into camelcase formatting."""
    result = camelcase('Old-time Moonshine')
    assert result == 'OldTimeMoonshine'


def test_snake_case():
    """Test turning a string into snake_case formatting."""
    result = snake_case('Old-time Moonshine')
    assert result == 'old_time_moonshine'


def test_clean_column_strings():
    """Test cleaning a column with messy string values."""
    observations = [
        {'string': '1 %',},
        {'string': '# 1',},
        # Optional: Add more cases.
    ]
    sample = pd.DataFrame(observations)
    result = clean_column_strings(sample, column='string')
    assert list(result.values) == [
        '1 percent',
        'number 1',
    ]


def test_clean_dictionary():
    """Test cleaning the keys of a dictionary."""
    sample = {
        'funky column': 1,
        'cannabis 3.0': 1,
        '$ per oz.': 1,
        '# of days': 1,
        'THC / CBD': 1,
        # Optional: Add additional cases.
    }
    result = clean_dictionary(sample)
    columns = list(result.keys())
    assert columns == [
        'funky_column',
        'cannabis_3_0',
        'dollars_per_oz',
        'number_of_days',
        'thc_to_cbd'
    ]
    result = clean_dictionary(sample, function=camelcase)
    columns = list(result.keys())
    assert columns == [
        'FunkyColumn',
        'Cannabis30',
        'DollarsPerOz',
        'NumberOfDays',
        'ThcToCbd',
    ]


def test_clean_nested_dictionary():
    """Test cleaning the keys of a nested dictionary."""
    sample = {
        'funky column': {
            'cannabis 3.0': 1,
            '$ per oz.': 1,
            '# of days': 1,
            'THC / CBD': 1,
            # Optional: Add additional cases.
        }
    }
    result = clean_nested_dictionary(sample)
    assert list(result['funky_column'].keys()) == [
        'cannabis_3_0',
        'dollars_per_oz',
        'number_of_days',
        'thc_to_cbd',
    ]
    result = clean_nested_dictionary(sample, function=camelcase)
    assert list(result['FunkyColumn'].keys()) == [
        'Cannabis30',
        'DollarsPerOz',
        'NumberOfDays',
        'ThcToCbd',
    ]


def test_get_keywords():
    """Test getting keywords from a string."""
    result = get_keywords('Old-time Moonshine')
    assert result == ['old-time', 'moonshine']


def test_get_random_string():
    """Test getting a random string, n characters long."""
    result = get_random_string(42)
    assert len(result) == 42
    result = get_random_string(42, allowed_chars=['a','b'])
    assert set(result) == {'a', 'b'} and len(result) == 42


# TODO: Test `get_timestamp`.
def test_get_timestamp():
    """Test ..."""
    result = get_timestamp()
    assert
    result = get_timestamp(date='2022-04-20')
    assert 

    # TODO: Test params: date, past, future, zone


def test_remove_dict_fields():
    """Test removing specific fields from a dictionary."""
    sample = {'result': 1, 'results': None}
    result = remove_dict_fields(sample, ['results'])
    assert 'results' not in list(result.keys())


def test_remove_dict_nulls():
    """Test removing fields with null values from a dictionary."""
    sample = {'result': 1, 'results': None}
    result = remove_dict_nulls(sample)
    assert 'results' not in list(result.keys())


def test_update_dict():
    """Test ..."""
    sample = {'funky_column': 1}
    result = update_dict(sample)
    assert 'FunkyColumn' in list(result.keys())
    # FIXME:
    # sample = {'FunkyColumn': 1}
    # result = update_dict(sample, function=snake_case)
    # assert 'funky_column' in list(result.keys())
    sample = {'FunkyColumn': 1}
    result = update_dict(sample, results='yes')
    assert result['Results'] == 'yes'


if __name__ == '__main__':

    test_camelcase()
    test_snake_case()
    test_clean_column_strings()
    test_clean_dictionary()
    test_clean_nested_dictionary()
    test_get_keywords()
    test_get_random_string()
    test_get_timestamp()
    test_remove_dict_fields()
    test_remove_dict_nulls()
    test_update_dict()
    print('Utility functions test successful.')
