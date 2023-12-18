"""
Cannabis Licenses | Get Connecticut Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 8/17/2023
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

NE_LABS = {
    'coa_algorithm': 'ne_labs.py',
    'coa_algorithm_entry_point': 'parse_ne_labs_coa',
    'lims': 'Northeast Laboratories',
    'url': 'www.nelabsct.com',
    'lab': 'Northeast Laboratories',
    'lab_website': 'www.nelabsct.com',
    'lab_license_number': '#PH-0404',
    'lab_image_url': 'https://www.nelabsct.com/images/Northeast-Laboratories.svg',
    'lab_address': '129 Mill Street, Berlin, CT 06037',
    'lab_street': '129 Mill Street',
    'lab_city': 'Berlin',
    'lab_county': 'Hartford',
    'lab_state': 'CT',
    'lab_zipcode': '06037',
    'lab_latitude': 41.626190,
    'lab_longitude': -72.748250,
    'lab_phone': '860-828-9787',
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
    timestamp = datetime.now().isoformat()
    retailers['data_refreshed_date'] = timestamp

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        date = datetime.now().strftime('%Y-%m-%d')
        labs = pd.DataFrame([NE_LABS])
        labs.to_csv(f'{data_dir}/labs-{STATE.lower()}-latest.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)

    # Return the licenses.
    return retailers


# === Test ===
# [✓] Tested: 2023-12-17 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '../data/ct'
    ENV_FILE = '../../../.env'

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

    # FIXME: It appears the licenses are now listed in an iframe.
    # ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')
    data = get_licenses_ct(data_dir, env_file=env_file)
