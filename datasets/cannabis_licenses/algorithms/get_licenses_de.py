"""
Cannabis Licenses | Get Delaware Licenses
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/25/2023
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Delaware cannabis license data.

Data Source:

    - Delaware Health Care Commission
    URL: <https://dhss.delaware.gov/dhss/dph/hsp/medmarcc.html>

"""
# Standard imports:
from datetime import datetime
import os
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/de'
ENV_FILE = '../../../.env'

# Specify state-specific constants.
STATE = 'DE'
DELAWARE = {
    'licensing_authority_id': 'DHCC',
    'licensing_authority': 'Delaware Health Care Commission',
    'licenses_url': 'https://dhss.delaware.gov/dhss/dph/hsp/medmarcc.html',
}


def get_gis_data(df: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """Get GIS data."""
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    rename_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    df = geocode_addresses(df, api_key=api_key, address_field='address')
    get_city = lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    df['premise_city'] = df['formatted_address'].apply(get_city)
    df.drop(columns=drop_cols, inplace=True)
    return df.rename(columns=rename_cols)


def get_licenses_de(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Delaware cannabis license data."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')
    
    # Get the license webpage.
    url = DELAWARE['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the licenses table.
    table =  soup.find('table')

    # Extract the license names.
    license_names = [x.text for x in table.find_all('strong') + table.find_all('b')]
    license_names = [x for x in license_names if x != 'Additional Links']

    # Extract the license websites.
    websites = [x.text for x in table.find_all('a') if x]
    websites = [x for x in websites if x.startswith('http')]

    # Get address and phone number.
    pars = table.find_all('p')
    addresses, phone_numbers = [], []
    for par in pars:

        # Identify the company name.
        names = [x.text for x in par.find_all('strong') + par.find_all('b')]
        if not names:
            continue

        # Iterate over all companies.
        for name in names:

            # Get the lines.
            lines = par.text.split(name)[-1].split('http')[0].split('\t\t\t\t\t\t')
            lines = [x.replace('\r', '').replace('\n', '') for x in lines[1:]]

            # Get the phone number.
            phone_number = lines[-1]
            phone_numbers.append(phone_number)

            # Get the address.
            address = ' '.join(lines[:-1])
            addresses.append(address)

    # Compile the license data.
    data = pd.DataFrame({
        'business_legal_name': license_names,
        'business_website': websites,
        'address': addresses,
        'phone_number': phone_numbers,
    })

    # Augment with GIS data.
    if google_maps_api_key:
        data = get_gis_data(data, google_maps_api_key)

    # Standardize the licenses.
    data = data.assign(
        id=data.index.astype(str),
        business_dba_name=data['business_legal_name'],
        licensing_authority_id=DELAWARE['licensing_authority_id'],
        licensing_authority=DELAWARE['licensing_authority'],
        premise_state=STATE,
        license_status_date=None,
        license_type='Commercial - Retailer',
        license_term=None,
        issue_date=None,
        expiration_date=None,
        business_structure=None,
        activity=None,
        parcel_number=None,
        business_image_url=None,
    )

    # Define metadata.
    data['data_refreshed_date'] = datetime.now().isoformat()

    # Sort the columns in alphabetical order
    data.sort_index(axis=1, inplace=True)

    # Save all of the licenses.
    if data_dir is not None:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        date = datetime.now().isoformat()[:10]
        data.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        data.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
    
    # Return the licenses.
    return data


# === Test ===
# [✓] Tested: 2023-08-13 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Support command line usage.
    import argparse
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--d', dest='data_dir', type=str)
        arg_parser.add_argument('--data_dir', dest='data_dir', type=str)
        arg_parser.add_argument('--env', dest='env_file', type=str)
        args = arg_parser.parse_args()
    except SystemExit:
        args = {'d': DATA_DIR, 'env_file': ENV_FILE}

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')
    data = get_licenses_de(data_dir, env_file=env_file)
