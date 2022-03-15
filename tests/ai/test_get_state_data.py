"""
Get State Data Test
Copyright (c) 2021 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 11/22/2021
Updated: 11/22/2021
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
from ai.get_cannabis_data.get_state_data import ( # pylint: disable=import-error
    get_state_current_population
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


if __name__ == '__main__':
    test_get_state_current_population()
