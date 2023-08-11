"""
Cannabis Licenses | Get Washington Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Washington cannabis license data.

Data Source:

    - Washington State Liquor and Cannabis Board | Frequently Requested Lists
    URL: <https://lcb.wa.gov/records/frequently-requested-lists>

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
DATA_DIR = '../data/wa'
ENV_FILE = '../../../.env'

# Specify state-specific constants.
STATE = 'WA'
WASHINGTON = {
    'licensing_authority_id': 'WSLCB',
    'licensing_authority': 'Washington State Liquor and Cannabis Board',
    'licenses_urls': 'https://lcb.wa.gov/records/frequently-requested-lists',
    'labs': {
        'key': 'Lab-List',
        'columns': {
            'Lab Name': 'business_legal_name',
            'Lab #': 'license_number',
            'Address 1': 'premise_street_address',
            'Address 2': 'premise_street_address_2',
            'City': 'premise_city',
            'Zip': 'premise_zip_code',
            'Phone': 'business_phone',
            'Status': 'license_status',
            'Certification Date': 'issue_date',
        },
        'drop_columns': [
            'Pesticides',
            'Heavy Metals',
            'Mycotoxins',
            'Water Activity',
            'Terpenes',
        ],
    },
    'medical': {
        'key': 'MedicalCannabisEndorsements',
        'columns': {
            'License': 'license_number',
            'UBI': 'id',
            'Tradename': 'business_dba_name',
            'Privilege': 'license_type',
            'Status': 'license_status',
            'Med Privilege Code': 'license_designation',
            'Termination Code': 'license_term',
            'Street Adress': 'premise_street_address',
            'Suite Rm': 'premise_street_address_2',
            'City': 'premise_city',
            'State': 'premise_state',
            'County': 'premise_county',
            'Zip Code': 'premise_zip_code',
            'Date Created': 'issue_date',
            'Day Phone': 'business_phone',
            'Email': 'business_email',
        },
    },
    'retailers': {
        'key': 'CannabisApplicants',
        'columns': {
            'Tradename': 'business_dba_name',
            'License ': 'license_number',
            'UBI': 'id',
            'Street Address': 'premise_street_address',
            'Suite Rm': 'premise_street_address_2',
            'City': 'premise_city',
            'State': 'premise_state',
            'county': 'premise_county',
            'Zip Code': 'premise_zip_code',
            'Priv Desc': 'license_type',
            'Privilege Status': 'license_status',
            'Day Phone': 'business_phone',
        },
    },
}


def download_file(url, dest='./', headers=None):
    """Download a file from a given URL to a local destination.
    Args:
        url (str): The URL of the data file.
        dest (str): The destination for the data file, `./` by default (optional).
        headers (dict): HTTP headers, `None` by default (optional).
    Returns:
        (str): The location for the data file.
    """
    filename = url.split('/')[-1]
    data_file = os.path.join(dest, filename)
    response = requests.get(url, headers=headers)
    with open(data_file, 'wb') as doc:
        doc.write(response.content)
    return data_file


def get_licenses_wa(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Washington cannabis license data."""

    # Create the necessary directories.
    file_dir = f'{data_dir}/.datasets'
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(file_dir): os.makedirs(file_dir)

    # Get the URLs for the license workbooks.
    labs_url, medical_url, retailers_url = None, None, None
    labs_key = WASHINGTON['labs']['key']
    medical_key = WASHINGTON['medical']['key']
    retailers_key = WASHINGTON['retailers']['key']
    url = WASHINGTON['licenses_urls']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link['href']
        if labs_key in href:
            labs_url = href
        elif retailers_key in href:
            retailers_url = href
        elif medical_key in href:
            medical_url = href
            break

    # Download the workbooks.
    lab_source_file = download_file(labs_url, dest=file_dir)
    medical_source_file = download_file(medical_url, dest=file_dir)
    retailers_source_file = download_file(retailers_url, dest=file_dir)

    # Extract and standardize the data from the workbook.
    retailers = pd.read_excel(retailers_source_file)
    retailers.rename(columns=WASHINGTON['retailers']['columns'], inplace=True)
    retailers['license_designation'] = 'Adult-Use'
    retailers['license_type'] = 'Adult-Use Retailer'
    
    labs = pd.read_excel(lab_source_file)
    labs.rename(columns=WASHINGTON['labs']['columns'], inplace=True)
    labs.drop(columns=WASHINGTON['labs']['drop_columns'], inplace=True)
    labs['license_type'] = 'Lab'

    medical = pd.read_excel(medical_source_file, skiprows=2)
    medical.rename(columns=WASHINGTON['medical']['columns'], inplace=True)
    medical['license_designation'] = 'Medicinal'
    medical['license_type'] = 'Medical Retailer'

    # Aggregate the licenses.
    licenses = pd.concat([retailers, medical, labs])

    # Standardize all of the licenses at once!
    licenses = licenses.assign(
        licensing_authority_id=WASHINGTON['licensing_authority_id'],
        licensing_authority=WASHINGTON['licensing_authority'],
        premise_state=STATE,
        license_status_date=None,
        expiration_date=None,
        activity=None,
        parcel_number=None,
        business_owner_name=None,
        business_structure=None,
        business_image_url=None,
        business_website=None,
    )

    # Fill legal and DBA names.
    licenses['id'].fillna(licenses['license_number'], inplace=True)
    licenses['business_legal_name'].fillna(licenses['business_dba_name'], inplace=True)
    licenses['business_dba_name'].fillna(licenses['business_legal_name'], inplace=True)
    cols = ['business_legal_name', 'business_dba_name']
    for col in cols:
        licenses[col] = licenses[col].apply(
            lambda x: x.title().replace('Llc', 'LLC').replace("'S", "'s").strip()
        )

    # Keep only active licenses.
    license_statuses = ['Active', 'ACTIVE (ISSUED)', 'ACTIVE TITLE CERTIFICATE',]
    licenses = licenses.loc[licenses['license_status'].isin(license_statuses)]

    # Convert certain columns from upper case title case.
    cols = ['business_dba_name', 'premise_city', 'premise_county',
            'premise_street_address', 'license_type', 'license_status']
    for col in cols:
        retailers[col] = retailers[col].apply(lambda x: x.title().strip())

    # Get the refreshed date.
    date = retailers_source_file.split('\\')[-1].split('.')[0]
    date = date.replace('CannabisApplicants', '')
    date = date[:2] + '-' + date[2:4] + '-' + date[4:8]
    licenses['data_refreshed_date'] = pd.to_datetime(date).isoformat()

    # Append `premise_street_address_2` to `premise_street_address`.
    cols = ['premise_street_address', 'premise_street_address_2']
    licenses['premise_street_address'] = licenses[cols].apply(
        lambda x : '{} {}'.format(x[0].strip(), x[1]).replace('nan', '').strip().replace('  ', ' '),
        axis=1,
    )
    licenses.drop(columns=['premise_street_address_2'], inplace=True)

    # Geocode licenses to get `premise_latitude` and `premise_longitude`.
    config = dotenv_values(env_file)
    api_key = config['GOOGLE_MAPS_API_KEY']
    cols = ['premise_street_address', 'premise_city', 'premise_state',
            'premise_zip_code']
    licenses['address'] = licenses[cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    licenses = geocode_addresses(licenses, address_field='address', api_key=api_key)
    drop_cols = ['state', 'state_name', 'county', 'address', 'formatted_address']
    gis_cols = {'latitude': 'premise_latitude', 'longitude': 'premise_longitude'}
    licenses.drop(columns=drop_cols, inplace=True)
    licenses.rename(columns=gis_cols, inplace=True)

    # TODO: Search for business website and image.

    # Save and return the data.
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
        retailers = licenses.loc[licenses['license_type'] == 'Adult-Use Retailer']
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        labs = licenses.loc[licenses['license_type'] == 'Lab']
        labs.to_csv(f'{data_dir}/labs-{STATE.lower()}-{timestamp}.csv', index=False)
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
    data = get_licenses_wa(data_dir, env_file=env_file)
