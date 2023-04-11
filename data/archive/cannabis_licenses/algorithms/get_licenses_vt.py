"""
Cannabis Licenses | Get Vermont Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Vermont cannabis license data.

Data Source:

    - Vermont
    URL: <https://ccb.vermont.gov/licenses>

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
DATA_DIR = '../data/vt'
ENV_FILE = '../.env'

# Specify state-specific constants.
STATE = 'VT'
VERMONT = {
    'licensing_authority_id': 'VTCCB',
    'licensing_authority': 'Vermont Cannabis Control Board',
    'licenses_url': 'https://ccb.vermont.gov/licenses',
    'licenses': {
        'licensedcultivators': {
            'columns': [
                'business_legal_name',
                'license_type',
                'address',
                'license_designation',
            ],
        },
        'outdoorcultivators': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
            ],
        },
        'mixedcultivators': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
            ],
        },
        'testinglaboratories': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
                'address'
            ],
        },
        'integrated': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
            ],
        },
        'retailers': {
            'columns': [
                'business_legal_name',
                'license_type',
                'address',
                'license_designation',
            ],
        },
        'manufacturers': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
            ],
        },
        'wholesalers': {
            'columns': [
                'business_legal_name',
                'license_type',
                'premise_city',
                'license_designation',
            ],
        },
    },
}


def get_licenses_vt(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Vermont cannabis license data."""

    # Get the licenses from the webpage.
    url = VERMONT['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse the various table types.
    data = []
    for license_type, values in VERMONT['licenses'].items():
        columns = values['columns']
        table = block = soup.find(attrs={'id': f'block-{license_type}'})
        rows = table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            obs = {}
            for i, cell in enumerate(cells):
                column = columns[i]
                obs[column] = cell.text
            data.append(obs)

    # Standardize the licenses.
    licenses = pd.DataFrame(data)
    licenses['id'] = licenses.index
    licenses['license_number'] = None # FIXME: It would be awesome to find these!
    licenses['licensing_authority_id'] = VERMONT['licensing_authority_id']
    licenses['licensing_authority'] = VERMONT['licensing_authority']
    licenses['license_designation'] = 'Adult-Use'
    licenses['premise_state'] = STATE
    licenses['license_status'] = None
    licenses['license_status_date'] = None
    licenses['license_term'] = None
    licenses['issue_date'] = None
    licenses['expiration_date'] = None
    licenses['business_owner_name'] = None
    licenses['business_structure'] = None
    licenses['activity'] = None
    licenses['parcel_number'] = None
    licenses['business_phone'] = None
    licenses['business_email'] = None
    licenses['business_image_url'] = None
    licenses['business_website'] = None

    # Separate the `license_designation` from `license_type` if (Tier x).
    criterion = licenses['license_type'].str.contains('Tier ')
    licenses.loc[criterion, 'license_designation'] = licenses.loc[criterion]['license_type'].apply(
        lambda x: 'Tier ' + x.split('(Tier ')[1].rstrip(')')
    )
    licenses.loc[criterion, 'license_type'] = licenses.loc[criterion]['license_type'].apply(
        lambda x: x.split('(Tier ')[0].strip()
    )

    # Separate labs' `business_email` and `business_phone` from the `address`.
    criterion = licenses['license_type'] == 'Testing Lab'
    licenses.loc[criterion, 'business_email'] = licenses.loc[criterion]['address'].apply(
        lambda x: x.split('Email: ')[-1].rstrip('\n') if isinstance(x, str) else x
    )
    licenses.loc[criterion, 'business_phone'] = licenses.loc[criterion]['address'].apply(
        lambda x: x.split('Phone: ')[-1].split('Email: ')[0].rstrip('\n') if isinstance(x, str) else x
    )
    licenses.loc[criterion, 'address'] = licenses.loc[criterion]['address'].apply(
        lambda x: x.split('Phone: ')[0].replace('\n', ' ').strip() if isinstance(x, str) else x
    )

    # Split any DBA from the legal name.
    splits = [';', 'DBA - ', '(DBA)', 'DBA ', 'dba ']
    licenses['business_dba_name'] = licenses['business_legal_name']
    for split in splits:
        criterion = licenses['business_legal_name'].str.contains(split)
        licenses.loc[criterion, 'business_dba_name'] = licenses.loc[criterion]['business_legal_name'].apply(
            lambda x: x.split(split)[1].replace(')', '').strip() if split in x else x
        )
        licenses.loc[criterion, 'business_legal_name'] = licenses.loc[criterion]['business_legal_name'].apply(
            lambda x: x.split(split)[0].replace('(', '').strip()
        )
    licenses.loc[licenses['business_legal_name'] == '', 'business_legal_name'] = licenses['business_dba_name']

    # Get the refreshed date.
    licenses['data_refreshed_date'] = datetime.now().isoformat()

    # Geocode the licenses.
    # FIXME: There are some wonky addresses that are output!
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    licenses = geocode_addresses(
        licenses,
        api_key=google_maps_api_key,
        address_field='address',
    )
    licenses['premise_street_address'] = licenses['formatted_address'].apply(
        lambda x: x.split(',')[0] if STATE in str(x) else x
    )
    licenses['premise_city'] = licenses['formatted_address'].apply(
        lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    )
    licenses['premise_zip_code'] = licenses['formatted_address'].apply(
        lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1] if STATE in str(x) else x
    )
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    licenses.drop(columns=drop_cols, inplace=True)
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    licenses.rename(columns=gis_cols, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers = licenses.loc[licenses['license_type'] == 'Retail']
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
    return licenses


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
    data = get_licenses_vt(data_dir, env_file=env_file)
