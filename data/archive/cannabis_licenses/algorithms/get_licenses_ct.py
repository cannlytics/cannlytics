"""
Cannabis Licenses | Get Connecticut Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/3/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Connecticut cannabis license data.

Data Source:

    - Connecticut State Department of Consumer Protection
    URL: <https://portal.ct.gov/DCP/Medical-Marijuana-Program/Connecticut-Medical-Marijuana-Dispensary-Facilities>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/ct'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'CT'
CONNECTICUT = {
    'licensing_authority_id': 'CSDCP',
    'licensing_authority': 'Connecticut State Department of Consumer Protection',
    'licenses_url': 'https://portal.ct.gov/DCP/Medical-Marijuana-Program/Connecticut-Medical-Marijuana-Dispensary-Facilities',
    'retailers': {
        'columns': [
            'business_legal_name',
            'address',
            'business_website',
            'business_email',
            'business_phone',
        ]
    }
}


def get_licenses_ct(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Connecticut cannabis license data."""

    # Get the license webpage.
    url = CONNECTICUT['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the license data.
    data = []
    columns = CONNECTICUT['retailers']['columns']
    table =  soup.find('table')
    rows = table.find_all('tr')
    for row in rows[1:]:
        cells = row.find_all('td')
        obs = {}
        for i, cell in enumerate(cells):
            column = columns[i]
            obs[column] = cell.text
        data.append(obs)

    # Standardize the license data.
    retailers = pd.DataFrame(data)
    retailers = retailers.assign(
        id=retailers.index,
        license_status=None,
        business_dba_name=retailers['business_legal_name'],
        license_number=None,
        licensing_authority_id=CONNECTICUT['licensing_authority_id'],
        licensing_authority=CONNECTICUT['licensing_authority'],
        license_designation='Adult-Use',
        premise_state=STATE,
        license_status_date=None,
        license_term=None,
        issue_date=None,
        expiration_date=None,
        business_owner_name=None,
        business_structure=None,
        activity=None,
        parcel_number=None,
        business_image_url=None,
        license_type=None,
    )

    # Get address parts.
    retailers['premise_street_address'] = retailers['address'].apply(
        lambda x: x.split(',')[0]
    )
    retailers['premise_city'] = retailers['address'].apply(
        lambda x: x.split('CT')[0].strip().split(',')[-2]
    )
    retailers['premise_zip_code'] = retailers['address'].apply(
        lambda x: x.split('CT')[-1].replace('\xa0', '').replace(',', '').strip()
    )

    # Geocode the licenses.
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    retailers = geocode_addresses(
        retailers,
        api_key=google_maps_api_key,
        address_field='address',
    )
    retailers['premise_city'] = retailers['formatted_address'].apply(
        lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    )
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    retailers.drop(columns=drop_cols, inplace=True)
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    retailers.rename(columns=gis_cols, inplace=True)

    # Get the refreshed date.
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)

    # Return the licenses.
    return retailers


# === Test ===
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
    data = get_licenses_ct(data_dir, env_file=env_file)
