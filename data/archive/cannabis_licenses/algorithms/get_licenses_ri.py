"""
Cannabis Licenses | Get Rhode Island Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 4/25/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Rhode Island cannabis license data.

Data Source:

    - Rhode Island
    URL: <https://dbr.ri.gov/office-cannabis-regulation/compassion-centers/licensed-compassion-centers>

TODO:

    [ ] Split up functionality into re-usable functions.
    [ ] Make geocoding optional.
    [ ] Make the code more robust to errors.

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
DATA_DIR = '../data/ri'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'RI'
RHODE_ISLAND = {
    'licensing_authority_id': 'RIDBH',
    'licensing_authority': 'Rhode Island Department of Business Regulation',
    'retailers': {
        'url': 'https://dbr.ri.gov/office-cannabis-regulation/compassion-centers/licensed-compassion-centers',
        'columns': [
            'license_number',
            'business_legal_name',
            'address',
            'business_phone',
            'business_website',
            'cultivator',
            'retailer',
        ],
    }
}


def get_licenses_ri(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Rhode Island cannabis license data."""

    # Load environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']

    # Get the licenses webpage.
    url = RHODE_ISLAND['retailers']['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse the table data.
    data = []
    columns = RHODE_ISLAND['retailers']['columns']
    table =  soup.find('table')
    rows = table.find_all('tr')
    for row in rows[1:]:
        cells = row.find_all('td')
        obs = {}
        for i, cell in enumerate(cells):
            column = columns[i]
            if column == 'business_website':
                obs[column] = cell.find('a')['href']
            else:
                obs[column] = cell.text.replace('\n', '').replace('\t\t\t', ' ')
        data.append(obs)

    # Optional: It's possible to download the certificate to get it's `issue_date`.

    # Standardize the license data.
    retailers = pd.DataFrame(data)
    retailers['id'] = retailers['license_number']
    retailers['licensing_authority_id'] = RHODE_ISLAND['licensing_authority_id']
    retailers['licensing_authority'] = RHODE_ISLAND['licensing_authority']
    retailers['license_type'] = 'Commercial - Retailer'
    retailers['premise_state'] = STATE
    retailers['license_status'] = 'Active'
    retailers['license_status_date'] = None
    retailers['license_term'] = None
    retailers['issue_date'] = None
    retailers['expiration_date'] = None
    retailers['business_owner_name'] = None
    retailers['business_structure'] = None
    retailers['business_email'] = None
    retailers['activity'] = None
    retailers['parcel_number'] = None
    retailers['business_image_url'] = None

    # Correct `license_designation`.
    coding = dict(Yes='Adult Use and Cultivation', No='Adult Use')
    retailers['license_designation'] = retailers['cultivator'].map(coding)

    # Correct `business_dba_name`.
    criterion = retailers['business_legal_name'].str.contains('D/B/A')
    retailers['business_dba_name'] = retailers['business_legal_name']
    retailers.loc[criterion, 'business_dba_name'] = retailers['business_legal_name'].apply(
        lambda x: x.split('D/B/A')[1].strip() if 'D/B/A' in x else x
    )
    retailers.loc[criterion, 'business_legal_name'] = retailers['business_legal_name'].apply(
        lambda x: x.split('D/B/A')[0].strip()
    )
    criterion = retailers['business_legal_name'].str.contains('F/K/A')
    retailers.loc[criterion, 'business_dba_name'] = retailers['business_legal_name'].apply(
        lambda x: x.split('F/K/A')[1].strip()  if 'D/B/A' in x else x
    )
    retailers.loc[criterion, 'business_legal_name'] = retailers['business_legal_name'].apply(
        lambda x: x.split('F/K/A')[0].strip()
    )

    # Get the refreshed date.
    par = soup.find_all('p')[-1]
    date = par.text.split('updated on ')[-1].split('.')[0]
    retailers['data_refreshed_date'] = pd.to_datetime(date).isoformat()

    # Geocode the licenses.
    retailers = geocode_addresses(
        retailers,
        api_key=google_maps_api_key,
        address_field='address',
    )
    retailers['premise_street_address'] = retailers['formatted_address'].apply(
        lambda x: x.split(',')[0]
    )
    retailers['premise_city'] = retailers['formatted_address'].apply(
        lambda x: x.split(', ')[1].split(',')[0]
    )
    retailers['premise_zip_code'] = retailers['formatted_address'].apply(
        lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1]
    )
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    retailers.drop(columns=drop_cols, inplace=True)
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    retailers.rename(columns=gis_cols, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)

    # Return the curated licenses.
    return retailers


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
    data = get_licenses_ri(data_dir, env_file=env_file)
