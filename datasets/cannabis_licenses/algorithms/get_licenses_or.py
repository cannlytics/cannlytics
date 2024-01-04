"""
Cannabis Licenses | Get Oregon Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/28/2022
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Oregon cannabis license data.

Data Source:

    - Oregon Liquor and Cannabis Commission
    URL: <https://www.oregon.gov/olcc/marijuana/pages/recreational-marijuana-licensing.aspx>

"""
# Standard imports.
from datetime import datetime
from io import BytesIO
import os
import re
from typing import Optional

# External imports.
from dotenv import dotenv_values
import pandas as pd
import pdfplumber
import requests
from cannlytics.data.gis import geocode_addresses


# Specify state-specific constants.
OREGON = {
    'licensing_authority_id': 'OLCC',
    'licensing_authority': 'Oregon Liquor and Cannabis Commission',
    'licenses': {
        'url': 'https://www.oregon.gov/olcc/marijuana/Documents/MarijuanaLicenses_Approved.xlsx',
    },
    'retailers': {
        'url': 'https://www.oregon.gov/olcc/marijuana/Documents/Approved_Retail_Licenses.xlsx',
        'columns': {
            'TRADE NAME': 'business_dba_name',
            'POSTAL CITY': 'premise_city',
            'COUNTY': 'premise_county',
            'STREET ADDRESS': 'premise_street_address',
            'ZIP': 'premise_zip_code',
            'Med Grade': 'medicinal',
            'Delivery': 'delivery',
        },
        'drop_columns': [
            'medicinal',
            'delivery',
        ],
    },
}

def get_licenses_or(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
        # Optional: Add print statements.
        # verbose: Optional[bool] = False,
    ):
    """Get Oregon cannabis license data."""

    # Create the necessary directories.
    file_dir = f'{data_dir}/.datasets'
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(file_dir): os.makedirs(file_dir)

    # Download the data workbooks.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    outfile = f'{file_dir}/retailers-or-{timestamp}.xlsx'
    response = requests.get(OREGON['retailers']['url'])
    with open(outfile, 'wb') as doc:
        doc.write(response.content)

    # Extract data from the workbooks, removing the footnote.
    data = pd.read_excel(outfile, skiprows=3)
    data = data[:-1]
    data.rename(columns=OREGON['retailers']['columns'], inplace=True)

    # Optional: Remove licenses with an asterisk (*).

    # Curate the data.
    data['licensing_authority_id'] = OREGON['licensing_authority_id']
    data['licensing_authority'] = OREGON['licensing_authority']
    data['license_status'] = 'Active'
    data['license_designation'] = 'Adult-Use'
    data['premise_state'] = 'OR'
    data.loc[data['medicinal'] == 'Yes', 'license_designation'] = 'Adult-Use and Medicinal'
    data['business_image_url'] = None
    data['license_status_date'] = None
    data['license_term'] = None
    data['issue_date'] = None
    data['expiration_date'] = None
    data['business_email'] = None
    data['business_owner_name'] = None
    data['business_structure'] = None
    data['business_website'] = None
    data['activity'] = None
    data['business_phone'] = None
    data['parcel_number'] = None
    data['business_legal_name'] = data['business_dba_name']

    # Optional: Convert `medicinal` and `delivery` columns to boolean.
    # data['medicinal'] = data['medicinal'].map(dict(Yes=1))
    # data['delivery'] = data['delivery'].map(dict(Yes=1))
    # data['medicinal'].fillna(0, inplace=True)
    # data['delivery'].fillna(0, inplace=True)
    data.drop(columns=['medicinal', 'delivery'], inplace=True)

    # Convert certain columns from upper case title case.
    cols = ['business_dba_name', 'premise_city', 'premise_county',
            'premise_street_address']
    for col in cols:
        data[col] = data[col].apply(lambda x: x.title().strip())

    # Convert zip code to a string.
    data.loc[:, 'premise_zip_code'] = data['premise_zip_code'].apply(lambda x: str(int(x)))

    # Get the `data_refreshed_date`.
    df = pd.read_excel(outfile, index_col=None, usecols='C', header=1, nrows=0)
    header = df.columns.values[0]
    date = pd.to_datetime(header.split(' ')[-1])
    data['data_refreshed_date'] = date.isoformat()

    # Get the `license_number` and `license_type` from license list.
    license_file = f'{file_dir}/licenses-or-{timestamp}.xlsx'
    response = requests.get(OREGON['licenses']['url'])
    with open(license_file, 'wb') as doc:
        doc.write(response.content)
    licenses = pd.read_excel(license_file, skiprows=2)
    licenses['BUSINESS NAME'] = licenses['BUSINESS NAME'].apply(
        lambda x: str(x).title().strip(),
    )
    licenses = licenses.loc[licenses['LICENSE TYPE'] == 'Recreational Retailer']
    data = pd.merge(
        data,
        licenses[['BUSINESS NAME', 'COUNTY', 'LICENSE NUMBER', 'LICENSE TYPE']],
        left_on=['business_dba_name', 'premise_county'],
        right_on=['BUSINESS NAME', 'COUNTY'],
        how='left',
    )

    # Clean the merged columns.
    data.drop_duplicates(subset='premise_street_address', inplace=True)
    columns = {
        'LICENSE NUMBER': 'license_number',
        'LICENSE TYPE': 'license_type',
    }
    data.rename(columns=columns, inplace=True)
    data.drop(columns=['BUSINESS NAME', 'COUNTY'], inplace=True)
    data['id'] = data['license_number']

    # Geocode licenses to get `premise_latitude` and `premise_longitude`.
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    cols = ['premise_street_address', 'premise_city', 'premise_state',
            'premise_zip_code']
    data['address'] = data[cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    data = geocode_addresses(
        data,
        api_key=google_maps_api_key,
        address_field='address',
    )
    drop_cols = ['state', 'state_name', 'county', 'address', 'formatted_address']
    data.drop(columns=drop_cols, inplace=True)
    gis_cols = {
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    data.rename(columns=gis_cols, inplace=True)

    # Optional: Lookup details by searching for business' websites.
    # - business_email
    # - business_phone

    # Optional: Create fields for standardization:
    # - id

    # Save the license data.
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        data.to_csv(f'{data_dir}/licenses-or-{timestamp}.csv', index=False)
        data.to_csv(f'{data_dir}/licenses-or-latest.csv', index=False)
    return data


# TODO: Add get cultivators, etc.


# TODO: Get Oregon labs.
# https://www.oregon.gov/oha/PH/LABORATORYSERVICES/ENVIRONMENTALLABORATORYACCREDITATION/Documents/canna-list.pdf


# === Test ===
# [✓] Tested: 2023-12-17 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '../data/or'
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

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')
    get_licenses_or(data_dir, env_file=env_file)
