"""
Test Logistics Utility Functions
Copyright (c) 2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/2/2022
Updated: 5/2/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
from cannlytics.firebase import initialize_firebase
from cannlytics.utils.logistics import (
    geocode_addresses,
    get_google_maps_api_key,
    get_place_details,
    search_for_address,
)
import pandas as pd


def test_get_google_maps_api_key(env_file):
    """Test getting Google Maps API key from Firestore."""
    try:
        initialize_firebase(env_file)
    except ValueError:
        pass
    result = get_google_maps_api_key()
    assert len(result) > 8


def test_geocode_addresses(env_file):
    """Test geocoding an address."""
    sample = pd.DataFrame([{
        'street': '1600 Pennsylvania Avenue',
        'city': 'Washington',
        'state': 'DC',
        'zip_code': '20500',
    }])
    result = geocode_addresses(sample)
    result['latitude'] = result.latitude.apply(lambda x: round(x, 4))
    result['longitude'] = result.longitude.apply(lambda x: round(x, 4))
    obs = result.iloc[0]
    coords = (obs.latitude, obs.longitude)
    assert coords == (38.8977, -77.0366)
    sample = pd.DataFrame([{
        'address': '1600 Pennsylvania Avenue, Washington, DC 20500',
    }])
    result = geocode_addresses(sample, address_field='address')
    result['latitude'] = result.latitude.apply(lambda x: round(x, 4))
    result['longitude'] = result.longitude.apply(lambda x: round(x, 4))
    obs = result.iloc[0]
    coords = (obs.latitude, obs.longitude)
    assert coords == (38.8977, -77.0366)
    try:
        initialize_firebase(env_file)
    except ValueError:
        pass
    api_key = get_google_maps_api_key()
    result = geocode_addresses(sample, api_key=api_key, address_field='address')
    result['latitude'] = result.latitude.apply(lambda x: round(x, 4))
    result['longitude'] = result.longitude.apply(lambda x: round(x, 4))
    obs = result.iloc[0]
    coords = (obs.latitude, obs.longitude)
    assert coords == (38.8977, -77.0366)
    result = geocode_addresses(sample, address_field='address', pause=2)
    result['latitude'] = result.latitude.apply(lambda x: round(x, 4))
    result['longitude'] = result.longitude.apply(lambda x: round(x, 4))
    obs = result.iloc[0]
    coords = (obs.latitude, obs.longitude)
    assert coords == (38.8977, -77.0366)


# TODO: Test `search_for_address`.
def test_search_for_address():
    """Test searching for an address."""
    result = search_for_address()
    # assert
    raise NotImplementedError


# TODO: Test `get_place_details`.
def test_get_place_details():
    """Test getting a place's details."""
    result = get_place_details()
    # assert
    raise NotImplementedError


if __name__ == '__main__':

    test_get_google_maps_api_key('../../../.env')
    test_geocode_addresses('../../../.env')
    # TODO:
    # test_search_for_address()
    # test_get_place_details()
