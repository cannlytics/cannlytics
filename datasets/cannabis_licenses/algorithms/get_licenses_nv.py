"""
Cannabis Licenses | Get Nevada Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 4/25/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Nevada cannabis license data.

Data Source:

    - Nevada
    URL: <https://ccb.nv.gov/list-of-licensees/>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from cannlytics.utils.constants import DEFAULT_HEADERS
from dotenv import dotenv_values
import pandas as pd
import requests

# Specify where your data lives.
DATA_DIR = '../data/nv'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'NV'
NEVADA = {
    'licensing_authority_id': 'NVCCB',
    'licensing_authority': 'Nevada Cannabis Compliance Board',
    'licenses': {
        'key': 'Active-License-List',
        'columns': {
            'LicenseNumber': 'license_number',
            'LicenseName': 'business_dba_name',
            'CE ID': 'id',
            'LicenseType': 'license_type',
            'County': 'premise_county',
        },
        'url': 'https://ccb.nv.gov/list-of-licensees/',
    }
}


def get_licenses_nv(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Nevada cannabis license data."""

    # Get the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']

    # Create the necessary directories.
    file_dir = f'{data_dir}/.datasets'
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(file_dir): os.makedirs(file_dir)

    #--------------------------------------------------------------------------
    # Get all license data.
    #--------------------------------------------------------------------------

    # Find the latest licenses workbook.
    licenses_url = ''
    retailer_key = NEVADA['licenses']['key']
    url = NEVADA['licenses']['url']
    response = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link['href']
        if retailer_key in href:
            licenses_url = href
            break
    
    # Download the workbook.
    filename = licenses_url.split('/')[-1]
    licenses_source_file = os.path.join(file_dir, filename)
    response = requests.get(licenses_url, headers=DEFAULT_HEADERS)
    with open(licenses_source_file, 'wb') as doc:
        doc.write(response.content)

    # Extract and standardize the data from the workbook.
    licenses = pd.read_excel(licenses_source_file, skiprows=1)
    licenses.rename(columns=NEVADA['licenses']['columns'], inplace=True)
    licenses['id'] = licenses['license_number']
    licenses['licensing_authority_id'] = NEVADA['licensing_authority_id']
    licenses['licensing_authority'] = NEVADA['licensing_authority']
    licenses['license_designation'] = 'Adult-Use'
    licenses['premise_state'] = STATE
    licenses['license_status_date'] = None
    licenses['license_term'] = None
    licenses['issue_date'] = None
    licenses['expiration_date'] = None
    licenses['business_legal_name'] = licenses['business_dba_name']
    licenses['business_owner_name'] = None
    licenses['business_structure'] = None
    licenses['business_email'] = None
    licenses['activity'] = None
    licenses['parcel_number'] = None
    licenses['business_image_url'] = None
    licenses['business_phone'] = None
    licenses['business_website'] = None

    # Convert certain columns from upper case title case.
    cols = ['business_dba_name', 'premise_county']
    for col in cols:
        licenses[col] = licenses[col].apply(lambda x: x.title().strip())

    # Get the refreshed date.
    date = filename.split('.')[0].replace(retailer_key, '').lstrip('-')
    date = '-'.join([date[:2], date[2:4], date[4:]])
    licenses['data_refreshed_date'] = pd.to_datetime(date)

    # Wish: Geocode licenses to get `premise_latitude` and `premise_longitude`.

    # Save the licenses    
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)

    #--------------------------------------------------------------------------
    # Get retailer data
    #--------------------------------------------------------------------------

    # Get the retailer data.
    retailers = []
    tables = soup.find_all('table', attrs={'class': 'customTable'})
    for table in tables:
        try:
            city = table.find('span').text
        except AttributeError:
            continue
        rows = table.find_all('td')
        vector = [x.text for x in rows]
        retailer = {}
        for cell in vector:
            if ' – ' in cell:
                parts = cell.split(' – ')
                retailer['business_legal_name'] = parts[0]
                retailer['business_dba_name'] = parts[0]
                retailer['premise_street_address'] = parts[1]
                retailer['license_designation'] = parts[-1]
                retailer['premise_city'] = city
            else:
                retailer['delivery'] = cell
            retailers.append(retailer)

    # Standardize the retailers.
    retailers = pd.DataFrame(retailers)
    retailers['licensing_authority_id'] = NEVADA['licensing_authority_id']
    retailers['licensing_authority'] = NEVADA['licensing_authority']
    retailers['license_type'] = 'Commercial - Retailer'
    retailers['license_status'] = 'Active'
    retailers['license_designation'] = 'Adult-Use'
    retailers['premise_state'] = STATE
    retailers['license_status_date'] = None
    retailers['license_term'] = None
    retailers['issue_date'] = None
    retailers['expiration_date'] = None
    retailers['business_owner_name'] = None
    retailers['business_structure'] = None
    retailers['business_email'] = None
    retailers['activity'] = None
    retailers['parcel_number'] = None
    retailers['business_website'] = None
    retailers['business_image_url'] = None
    retailers['business_phone'] = None

    # FIXME: Merge `license_number`, `premise_county`, `data_refreshed_date`
    # from licenses.
    retailers['license_number'] = None
    retailers['id'] = None
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Geocode the retailers.
    cols = ['premise_street_address', 'premise_city', 'premise_state']
    retailers['address'] = retailers[cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    retailers = geocode_addresses(
        retailers,
        api_key=google_maps_api_key,
        address_field='address',
    )
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    retailers['premise_zip_code'] = retailers['formatted_address'].apply(
        lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1] if STATE in str(x) else x
    )
    retailers.drop(columns=drop_cols, inplace=True)
    retailers.rename(columns=gis_cols, inplace=True)

    # Save the retailers    
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-latest.csv', index=False)

    # Return all of the data.
    return pd.concat([licenses, retailers])


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
    data = get_licenses_nv(data_dir, env_file=env_file)
