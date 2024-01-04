"""
Cannabis Licenses | Get Missouri Licenses
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/26/2023
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Missouri cannabis license data.

Requirements:

    The script leverages Google Maps to attempt to geocode license
    addresses. Ensure that you have a `.env` file with a valid
    Google Maps API specified as `GOOGLE_MAPS_API_KEY`.

Command-line Usage:

    python get_licenses_mo.py --data_dir <DATA_DIR> --env <ENV_FILE>

Data Source:

    - Missouri Medical Cannabis Licenses
    URL: <https://health.mo.gov/safety/medical-marijuana/licensed-facilities.php>

"""
# Standard imports:
from datetime import datetime
import os
import re
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import numpy as np
import pandas as pd
import requests
import zipcodes


# Specify state-specific constants.
STATE = 'MO'
MISSOURI = {
    'licensing_authority_id': 'MDHSS',
    'licensing_authority': 'Missouri Department of Health and Senior Services',
    'licenses_url': 'https://health.mo.gov/safety/cannabis/licensed-facilities.php',
    'columns': {
        'Medical': 'medical',
        'Comprehensive': 'adult_use',
        'Approved to Operate': 'license_status',
        'License \nNumber': 'license_number',
        'Entity Name': 'business_legal_name',
        'City': 'premise_city',
        'State': 'premise_state',
        'Postal Code': 'premise_zip_code',
        ' Contact \nInformation 1': 'first_name',
        'Contact \nInformation 1': 'first_name',
        'Contact \nInformation 2': 'last_name',
        'Contact \nPhone': 'business_phone'
    },
    'license_types': {
        'cultivation': 'cultivator',
        'dispensary': 'retailer',
        'infused-product-manufacturing': 'processor',
        'laboratory-testing': 'lab',
        'transportation': 'delivery',
    },
    'drop': ['first_name', 'last_name'],
}


def format_phone_number(x):
    """Format phone numbers as ###-###-####."""
    digits = re.sub(r'\D', '', x)
    return '{}-{}-{}'.format(digits[:3], digits[3:6], digits[6:])


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


def get_licenses_mo(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Missouri cannabis license data."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')
    
    # Create the download directory if it doesn't exist.
    download_dir = os.path.join(data_dir, '.datasets')
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get the licenses website content.
    url = MISSOURI['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all workbook links on the website.
    links = soup.find_all('a')
    xlsx_links = [x for x in links if x.get('href').endswith('.xlsx')]

    # Download the files to the download directory.
    datafiles = []
    base = 'https://health.mo.gov/safety/cannabis/xls/'
    for link in xlsx_links:
        file_url = base + link.get('href').split('/')[-1]
        file_name = os.path.join(download_dir, os.path.basename(file_url))
        with open(file_name, 'wb') as file:
            response = requests.get(file_url)
            file.write(response.content)
        datafiles.append(file_name)

    # Open each datafile and extract the data.
    licenses = []
    for datafile in datafiles:

        # Get the license type from the filename.
        license_type = datafile.split('\\')[-1].replace('.xlsx', '') \
            .replace('licensed-', '') \
            .replace('-facilities', '')
    
        # Standardize the license type.
        license_type = MISSOURI['license_types'].get(license_type, license_type)

        # Open the workbook.
        data = pd.read_excel(datafile, skiprows=1)

        # Rename columns.
        data.rename(columns=MISSOURI['columns'], inplace=True)

        # Replace non-NaN columns with True and NaN columns with False.
        data['license_status'] = data['license_status'].notna() \
            .map({True: 'Active', False: 'Inactive'})

        # Combine medical / adult_use into `license_designation`.
        try:
            data['medical'] = data['medical'].notna().map({True: True, False: False})
            data['adult_use'] = data['adult_use'].notna().map({True: True, False: False})
            conditions = [
                (data['medical'] & data['adult_use']),
                (data['medical']),
                (data['adult_use'])
            ]
            choices = [
                'medical and adult-use',
                'medical',
                'adult-use'
            ]
            data['license_designation'] = np.select(conditions, choices, default=None)
        except KeyError:
            data['license_designation'] = 'adult-use'

        # Combine owner name columns.
        data['business_owner_name'] = data['first_name'].str.cat(
            data['last_name'],
            sep=' ',
        )

        # Clean the phone numbers.
        data['business_phone'] = data['business_phone'].apply(str).apply(format_phone_number)

        # Drop unused columns.
        unnamed = [x for x in data.columns if re.match('^Unnamed', x)]
        to_drop = MISSOURI['drop'] + unnamed
        data.drop(to_drop, axis=1, inplace=True)

        # Augment GIS data.
        data['address'] = data['business_legal_name'] + ', ' + data['premise_city'] + ', ' + data['premise_state'] + ' ' + data['premise_zip_code'].astype(str)
        data = get_gis_data(data, google_maps_api_key)

        # Get the county.
        get_county = lambda x: zipcodes.matching(x)[0]['county']
        data['county'] = data['premise_zip_code'].astype(str).apply(get_county)

        # Standardize the license data.
        data = data.assign(
            id=data['license_number'].astype(str),
            business_dba_name=data['business_legal_name'],
            licensing_authority_id=MISSOURI['licensing_authority_id'],
            licensing_authority=MISSOURI['licensing_authority'],
            premise_state=STATE,
            license_status_date=None,
            license_type=license_type,
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

        # Save the data.
        if data_dir is not None:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            date = datetime.now().isoformat()[:10]
            plural = f'{license_type.replace("y", "")}ies' if license_type.endswith('y') else f'{license_type}s'
            outfile = f'{data_dir}/{plural}-{STATE.lower()}-{date}.csv'
            data.to_csv(outfile, index=False)

        # Record the licenses.
        licenses.append(data)

    # Save all of the licenses.
    licenses = pd.concat(licenses)
    if data_dir is not None:
        date = datetime.now().isoformat()[:10]
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
    
    # Return the licenses.
    return licenses


# === Test ===
# [✓] Tested: 2023-12-17 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '../data/mo'
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
        args = {'data_dir': DATA_DIR, 'env_file': ENV_FILE}

    # FIXME:
    # ValueError: Invalid format, zipcode must be of the format: "#####" or "#####-####"

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')
    data = get_licenses_mo(data_dir, env_file=env_file)
