"""
Cannabis Licenses | Get Maine Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 4/25/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Maine cannabis license data.

Data Source:

    - Maine Office of Cannabis Policy
    URL: <https://www.maine.gov/dafs/ocp/open-data/adult-use>

# TODO:

    [ ] Priority: Save the retailers in a stand-alone data file.
    [ ] Separate the functionality into functions.
    [ ] Make the code more robust to errors.
    [ ] Make Google Maps API key optional.    

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
DATA_DIR = '../data/me'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'ME'
MAINE = {
    'licensing_authority_id': 'MEOCP',
    'licensing_authority': 'Maine Office of Cannabis Policy',
    'licenses': {
        'url': 'https://www.maine.gov/dafs/ocp/open-data/adult-use',
        'key': 'Adult_Use_Establishments_And_Contacts',
        'columns': {
            'LICENSE': 'license_number',
            'LICENSE_CATEGORY': 'license_type',
            'LICENSE_TYPE': 'license_designation',
            'LICENSE_NAME': 'business_legal_name',
            'DBA': 'business_dba_name',
            'LICENSE_STATUS': 'license_status',
            'LICENSE_CITY': 'premise_city',
            'WEBSITE': 'business_website',
            'CONTACT_NAME': 'business_owner_name',
            'CONTACT_TYPE': 'contact_type',
            'CONTACT_CITY': 'contact_city',
            'CONTACT_DESCRIPTION': 'contact_description',
        },
    }
}


def get_licenses_me(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Maine cannabis license data."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    api_key = config['GOOGLE_MAPS_API_KEY']

    # Create the necessary directories.
    file_dir = f'{data_dir}/.datasets'
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(file_dir): os.makedirs(file_dir)

    # Get the download link.
    licenses_url = None
    licenses_key = MAINE['licenses']['key']
    url = MAINE['licenses']['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        try:
            href = link['href']
        except KeyError:
            continue
        if licenses_key in href:
            licenses_url = href
            break

    # Download the licenses workbook.
    filename = licenses_url.split('/')[-1].split('?')[0]
    licenses_source_file = os.path.join(file_dir, filename)
    response = requests.get(licenses_url)
    with open(licenses_source_file, 'wb') as doc:
        doc.write(response.content)

    # Extract the data from the license workbook.
    licenses = pd.read_excel(licenses_source_file)
    licenses.rename(columns=MAINE['licenses']['columns'], inplace=True)
    licenses = licenses.assign(
        licensing_authority_id=MAINE['licensing_authority_id'],
        licensing_authority=MAINE['licensing_authority'],
        license_designation='Adult-Use',
        premise_state=STATE,
        license_status_date=None,
        license_term=None,
        issue_date=None,
        expiration_date=None,
        business_structure=None,
        business_email=None,
        business_phone=None,
        activity=None,
        parcel_number=None,
        premise_street_address=None,
        id=licenses['license_number'],
        business_image_url=None,
    )

    # Remove duplicates.
    licenses.drop_duplicates(subset='license_number', inplace=True)

    # Replace null DBA with legal name.
    criterion = licenses['business_dba_name'].isnull()
    licenses.loc[criterion,'business_dba_name'] = licenses['business_legal_name']

    # Convert certain columns from upper case title case.
    cols = ['business_legal_name', 'business_dba_name', 'business_owner_name']
    for col in cols:
        licenses[col] = licenses[col].apply(
            lambda x: x.title().strip() if isinstance(x, str) else x
        )

    # Get the refreshed date.
    try:
        date = licenses_source_file[-15:]
        date = date.replace('_', '-').replace('.xlsx', '')
        licenses['data_refreshed_date'] = pd.to_datetime(date).isoformat()
    except:
        licenses['data_refreshed_date'] = datetime.now().isoformat()

    # Geocode licenses to get `premise_latitude` and `premise_longitude`.
    cols = ['premise_city', 'premise_state']
    licenses['address'] = licenses[cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    licenses = geocode_addresses(licenses, address_field='address', api_key=api_key)
    drop_cols = ['state', 'state_name', 'address', 'formatted_address',
                'contact_type', 'contact_city', 'contact_description']
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude',
    }
    licenses['premise_zip_code'] = licenses['formatted_address'].apply(
        lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1] if STATE in str(x) else x
    )
    licenses.drop(columns=drop_cols, inplace=True)
    licenses.rename(columns=gis_cols, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
        # TODO: Save the retailers in a stand-alone data file.

    # Return the licenses.
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
    data = get_licenses_me(data_dir, env_file=env_file)
