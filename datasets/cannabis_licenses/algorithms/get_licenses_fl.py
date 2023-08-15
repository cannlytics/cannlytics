"""
Florida cannabis licenses and lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 8/14/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis license data.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)

Resources:

    - 'https://www.reddit.com/r/FLMedicalTrees/search/?q=COA'
    - https://www.reddit.com/r/FLMedicalTrees/comments/1272per/anyone_have_batch_s_they_can_share_for_our/
    - https://www.reddit.com/r/FLMedicalTrees/comments/vdnpqf/coa_accumulation/

"""
# Standard imports:
from datetime import datetime
import os
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests


# Specify state-specific constants.
STATE = 'FL'
FLORIDA = {
    'licensing_authority_id': 'OMMU',
    'licensing_authority': 'Florida Office of Medical Marijuana Use',
    'licenses_url': 'https://knowthefactsmmj.com/mmtc/',
    'labs_url': 'https://knowthefactsmmj.com/cmtl/',
    'columns': {
        'Name': 'business_dba_name',
        'Phone': 'business_phone',
        'Email': 'business_email',
        'Authorization Status': 'license_status',
        'License Number': 'license_number',
    },
    'labs_columns': {
        'Name': 'business_dba_name',
        'Phone': 'business_phone',
        'Email': 'business_email',
        'Address': 'address',
        'Date Certified': 'issue_date',
    }
}


#-----------------------------------------------------------------------
# Get Florida labs.
#-----------------------------------------------------------------------

def get_labs_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get labs in Florida."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Get the licenses URL.
    url = FLORIDA['labs_url']
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # Get the table data.
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:]
    columns = FLORIDA['labs_columns']
    observations = []
    for row in rows:
        cells = row.find_all('td')
        cells = [x.text.replace('\n', ' ').strip() for x in cells]
        observations.append(cells)

    # Convert the list of rows into a DataFrame.
    df = pd.DataFrame(observations)
    df.columns = list(columns.values())

    # Geocode licenses.
    if google_maps_api_key is not None:
        df = geocode_addresses(
            df,
            api_key=google_maps_api_key,
            address_field='address',
        )
        df.rename(columns={
            # 'county': 'premise_county',
            'latitude': 'premise_latitude',
            'longitude': 'premise_longitude'
        }, inplace=True)
        parts = df['formatted_address'].str.split(',', n=3, expand=True)
        df['premise_street'] = parts[0]
        df['premise_city'] = parts[1]
        df['premise_state'] = STATE
        df['premise_zip_code'] = parts[2].str.replace(STATE, '').str.strip()
        drop_cols = ['address', 'formatted_address', 'county', 'state', 'state_name']
        df.drop(columns=drop_cols, inplace=True)

    # Standardize the licenses data.
    df = df.assign(
        business_legal_name=df['business_dba_name'],
        licensing_authority_id=FLORIDA['licensing_authority_id'],
        licensing_authority=FLORIDA['licensing_authority'],
        business_structure=None,
        business_owner_name=None,
        parcel_number=None,
        expiration_date=None,
        business_image_url=None,
        business_website=None,
        license_status_date=None,
        license_type='Lab',
        license_designation=None,
        activity=None,
    )

    # Set metadata.
    df['data_refreshed_date'] = datetime.now().isoformat()

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        df.to_csv(f'{data_dir}/labs-{STATE.lower()}-latest.csv', index=False)

    # Return the data.
    return df


#-----------------------------------------------------------------------
# Get Florida retailers.
#-----------------------------------------------------------------------

def get_retailers_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get retailers in Florida."""

    # Get the licenses URL.
    url = FLORIDA['licenses_url']
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # TODO: Get the retailers from each page!

    # Geocode licenses.
    if google_maps_api_key is not None:
        df = geocode_addresses(
            df,
            api_key=google_maps_api_key,
            address_field='address',
        )
        # FIXME: Would be ideal to also get the county.
        df['premise_county'] = None
        df.rename(columns={
            # 'county': 'premise_county',
            'latitude': 'premise_latitude',
            'longitude': 'premise_longitude'
        }, inplace=True)
        parts = df['formatted_address'].str.split(',', n=3, expand=True)
        df['premise_street'] = parts[0]
        df['premise_city'] = parts[1]
        df['premise_state'] = STATE
        df['premise_zip_code'] = parts[2].str.replace(STATE, '').str.strip()
        drop_cols = ['address', 'formatted_address']
        df.drop(columns=drop_cols, inplace=True)
    
    raise NotImplementedError


#-----------------------------------------------------------------------
# Get Florida licenses.
#-----------------------------------------------------------------------

def get_licenses_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get licenses in Florida."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Get the licenses URL.
    url = FLORIDA['licenses_url']
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # Get the table data.
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    cells = table.text.split('\n')
    cells = [x for x in cells if x]
    columns = FLORIDA['columns']
    rows = cells[len(columns):]
    rows = [rows[i:i+len(columns)] for i in range(0, len(rows), len(columns))]

    # Convert the list of rows into a DataFrame.
    df = pd.DataFrame(rows)
    df.columns = list(columns.values())

    # Get the business website and license URLs from each row.
    business_websites, license_urls = [], []
    table_rows = table.find_all('tr')[1:]
    for row in table_rows:
        columns = row.find_all('td')
        business_link = columns[0].find('a')
        business_websites.append(business_link['href'] if business_link else None)
        license_link = columns[-1].find('a')
        license_urls.append(license_link['href'] if license_link else None)
    df['business_website'] = business_websites
    df['license_url'] = license_urls

    # TODO: Get issue date from the license PDF.
    # (Will need to apply OCR to get a PDF first.)
    df['issue_date'] = None

    # TODO: Get the business legal name from the license PDF.
    df['business_legal_name'] = df['business_dba_name']

    # Standardize the licenses data.
    df = df.assign(
        licensing_authority_id=FLORIDA['licensing_authority_id'],
        licensing_authority=FLORIDA['licensing_authority'],
        business_structure=None,
        business_owner_name=None,
        parcel_number=None,
        expiration_date=None,
        business_image_url=None,
        business_website=None,
        license_status='Active',
        license_status_date=None,
        license_type='Medical - Retailer',
        license_designation=None,
        activity=None,
    )

    # Set metadata.
    df['data_refreshed_date'] = datetime.now().isoformat()

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        df.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)

    # Return the data.
    return df


# === Tests ===
# [✓] Tested: 2023-08-14 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    data_dir = '../data/fl'
    env_file = '../../../.env'

    # [✓] TEST: Get Florida labs.
    labs = get_labs_fl(data_dir=data_dir, env_file=env_file)

    # [ ] TEST: Get Florida retailers.


    # [✓] TEST: Get Florida licenses.
    licenses = get_licenses_fl(data_dir=data_dir, env_file=env_file)
