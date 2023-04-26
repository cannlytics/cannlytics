"""
Cannabis Licenses | Get Missouri Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 11/29/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Missouri cannabis license data.

Data Source:

    - Missouri Medical Cannabis Licenses
    URL: <https://health.mo.gov/safety/medical-marijuana/licensed-facilities.php>

"""
# Standard imports:
from datetime import datetime
import os
from typing import Optional
from bs4 import BeautifulSoup

# External imports:
import numpy as np
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/mo'
ENV_FILE = '../../../../.env'

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
        'Contact \nInformation 1': 'first_name',
        'Contact \nInformation 2': 'last_name',
        'Contact \nPhone': 'business_phone'
    },
    'drop': ['first_name', 'last_name'],
}


def get_licenses_mo(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Missouri cannabis license data."""
    
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
    base = 'https://health.mo.gov'
    for link in xlsx_links:
        file_url = base + link.get('href')
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
        print(license_type)

        # Open the workbook.
        data = pd.read_excel(datafile, skiprows=1)

        # Rename columns.
        data.rename(columns=MISSOURI['columns'], inplace=True)

        # Replace non-NaN columns with True and NaN columns with False
        data['license_status'] = data['license_status'].notna() \
            .map({True: 'Active', False: 'Inactive'})

        # FIXME: Combine medical / adult_use into `license_type`.
        try:
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
            data['license_type'] = np.select(conditions, choices, default=None)
        except KeyError:
            data['license_type'] = 'adult-use'

        # Combine owner name columns.
        data['business_owner_name'] = data['first_name'].str.cat(
            data['last_name'],
            sep=' ',
        )

        # Drop unused columns.
        data.drop(MISSOURI['drop'], axis=1, inplace=True)

        # TODO: Augment GIS data.

        # Standardize the license data.
        data = data.assign(
            id=data.index,
            license_status=None,
            business_dba_name=data['business_legal_name'],
            license_number=None,
            licensing_authority_id=MISSOURI['licensing_authority_id'],
            licensing_authority=MISSOURI['licensing_authority'],
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

        # Define metadata.
        data['data_refreshed_date'] = datetime.now().isoformat()

        # Save the data.
        if data_dir is not None:
            if not os.path.exists(data_dir): os.makedirs(data_dir)
            timestamp = datetime.now().isoformat()[:19].replace(':', '-')
            outfile = f'{data_dir}/{license_type}-{STATE.lower()}-{timestamp}.csv'
            data.to_csv(outfile, index=False)
        
        # Record the licenses.
        licenses.append(data)

    # Return the licenses.
    return pd.concat(licenses)


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
    data = get_licenses_mo(data_dir, env_file=env_file)
