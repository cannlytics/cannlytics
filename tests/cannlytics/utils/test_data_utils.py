"""
Test Data Utility Functions
Copyright (c) 2021-2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 11/22/2021
Updated: 5/02/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
# Standard imports.
import os
from pathlib import Path
import yaml

# External imports.
import pytest

# Internal imports.
import sys
sys.path.append('./')
sys.path.append('../')
from cannlytics.utils.data import (
    convert_month_year_to_date,
    end_of_month,
    end_of_year,
    end_of_period_timeseries,
    format_billions,
    format_millions,
    format_thousands,
    get_state_population,
    get_state_current_population,
    months_elapsed,
    reverse_dataframe,
    set_training_period,
    sorted_nicely,
    sentence_case,
    rmerge,
)


def test_get_state_current_population():
    """Test the `get_state_current_population` function."""

    # Read the FRED API key.
    path = Path(os.path.realpath(__file__))
    dir_path = 'ai/get_cannabis_data'
    with open(f'{path.parent.parent}/{dir_path}/env.yaml', 'r') as env:
        config = yaml.load(env, Loader=yaml.FullLoader)
        fred_api_key = config['FRED_API_KEY']

    # Test getting Massachusetts population from lowercase abbreviation.
    population_data = get_state_current_population('ma', fred_api_key)
    assert population_data['population'] == 6893574 # MA 2020 population

    # Test getting Massachusetts population from uppercase abbreviation.
    population_data = get_state_current_population('MA', fred_api_key)
    assert population_data['population'] == 6893574 # MA 2020 population

    # Test getting Massachusetts population with no API key.
    with pytest.raises(Exception):
        get_state_current_population('MA')

    # Test getting Massachusetts population with no API key after setting
    # `FRED_API_KEY` environment variable.
    os.environ['FRED_API_KEY'] = fred_api_key
    population_data = get_state_current_population('MA')
    assert population_data['population'] == 6893574 # MA 2020 population


# TODO: Test `get_state_population`
def test_get_state_population():
    """Test ..."""
    result = get_state_population()
    assert


# TODO: Test `convert_month_year_to_date`
def test_convert_month_year_to_date():
    """Test ..."""
    result = convert_month_year_to_date()
    assert


# TODO: Test `end_of_month`
def test_end_of_month():
    """Test ..."""
    result = end_of_month()
    assert

# TODO: Test `end_of_year`
def test_end_of_year():
    """Test ..."""
    result = end_of_year()
    assert


# TODO: Test `end_of_period_timeseries`
def test_end_of_period_timeseries():
    """Test ..."""
    result = end_of_period_timeseries()
    assert


# TODO: Test `months_elapsed`
def test_months_elapsed():
    """Test ..."""
    result = months_elapsed()
    assert


# TODO: Test `reverse_dataframe`
def test_reverse_dataframe():
    """Test ..."""
    result = reverse_dataframe()
    assert


# TODO: Test `set_training_period`
def test_set_training_period():
    """Test ..."""
    result = set_training_period()
    assert

# TODO: Test `format_billions`
def test_format_billions():
    """Test ..."""
    result = format_billions()
    assert


# TODO: `format_millions`
def test_format_millions():
    """Test ..."""
    result = format_millions()
    assert


# TODO: `format_thousands`
def test_format_thousands():
    """Test ..."""
    result = format_thousands()
    assert


# TODO: `sorted_nicely`
def test_sorted_nicely():
    """Test ..."""
    result = sorted_nicely()
    assert


# TODO: `sentence_case`
def test_sentence_case():
    """Test ..."""
    result = sentence_case()
    assert


# TODO: `rmerge`
def test_rmerge():
    """Test ..."""
    result = rmerge()
    assert

if __name__ == '__main__':

    test_convert_month_year_to_date()
    test_end_of_month()
    test_end_of_year()
    test_end_of_period_timeseries()
    test_format_billions()
    test_format_millions()
    test_format_thousands()
    test_get_state_population()
    test_get_state_current_population()
    test_months_elapsed()
    test_reverse_dataframe()
    test_set_training_period()
    test_sorted_nicely()
    test_sentence_case()
    test_rmerge()
