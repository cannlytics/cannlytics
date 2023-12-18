"""
Cannabis Licenses | Get Colorado Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 9/20/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Colorado cannabis license data.

Data Source:

    - Colorado Department of Revenue | Marijuana Enforcement Division
    URL: <https://sbg.colorado.gov/med/licensed-facilities>

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports.
from bs4 import BeautifulSoup
from cannlytics.data.data import load_google_sheet
from cannlytics.data.gis import search_for_address
from dotenv import dotenv_values
import pandas as pd
import requests


# Specify state-specific constants.
STATE = 'CO'
COLORADO = {
    'licensing_authority_id': 'MED',
    'licensing_authority': 'Colorado Marijuana Enforcement Division',
    'licenses_url': 'https://sbg.colorado.gov/med/licensed-facilities',
    'licenses': {
        'columns': {
            'LicenseNumber': 'license_number',
            'FacilityName': 'business_legal_name',
            'DBA': 'business_dba_name',
            'City': 'premise_city',
            'ZipCode': 'premise_zip_code',
            'DateUpdated': 'data_refreshed_date',
            'Licensee Name ': 'business_legal_name',
            'License # ': 'license_number',
            'City ': 'premise_city',
            'Zip': 'premise_zip_code',
        },
        'drop_columns': [
            'FacilityType', # This causes an error with `license_type`.
            'Potency',
            'Solvents',
            'Microbial',
            'Pesticides',
            'Mycotoxin',
            'Elemental Impurities',
            'Water Activity'
        ]
    }
}


def get_licenses_co(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Colorado cannabis license data."""

    # Get the licenses webpage.
    url = COLORADO['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the Google Sheets for each license type.
    docs = {}
    links = soup.find_all('a')
    for link in links:
        try:
            href = link['href']
        except KeyError:
            pass
        if 'docs.google' in href:
            docs[link.text] = href

    # Download each "Medical" and "Retail" Google Sheet.
    licenses = pd.DataFrame()
    license_designations = ['Medical', 'Retail']
    columns=COLORADO['licenses']['columns']
    drop_columns=COLORADO['licenses']['drop_columns']
    for license_type, doc in docs.items():
        for license_designation in license_designations:
            license_data = load_google_sheet(doc, license_designation)
            license_data['license_type'] = license_type
            license_data['license_designation'] = license_designation
            license_data.rename(columns=columns, inplace=True)
            license_data.drop(columns=drop_columns, inplace=True, errors='ignore')
            licenses = pd.concat([licenses, license_data])
            sleep(0.22)

    # Standardize the license data.    
    licenses = licenses.assign(
        id=licenses['license_number'],
        license_status=None,
        licensing_authority_id=COLORADO['licensing_authority_id'],
        licensing_authority=COLORADO['licensing_authority'],
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
        business_phone=None,
        business_email=None,
        business_image_url=None,
    )

    # Fill empty DBA names and strip trailing whitespace.
    licenses.loc[licenses['business_dba_name'] == '', 'business_dba_name'] = licenses['business_legal_name']
    licenses.business_dba_name.fillna(licenses.business_legal_name, inplace=True)
    licenses.business_legal_name.fillna(licenses.business_dba_name, inplace=True)
    licenses = licenses.loc[~licenses.business_dba_name.isna()]
    licenses.business_dba_name = licenses.business_dba_name.apply(lambda x: x.strip())
    licenses.business_legal_name = licenses.business_legal_name.apply(lambda x: x.strip())

    # Optional: Turn all capital case to title case.

    # Clean zip code column.
    licenses['premise_zip_code'] = licenses['premise_zip_code'].apply(
        lambda x: str(round(x)) if pd.notnull(x) else x
    )
    licenses.loc[licenses['premise_zip_code'].isnull(), 'premise_zip_code'] = ''

    # Search for address for each retail license.
    # Only search for a query once, then re-use the response.
    # Note: There is probably a much, much more efficient way to do this!!!
    config = dotenv_values(env_file)
    api_key = config['GOOGLE_MAPS_API_KEY']
    cols = ['business_dba_name', 'premise_city', 'premise_state', 'premise_zip_code']
    retailers = licenses.loc[licenses['license_type'] == 'Stores'].copy()
    retailers['query'] = retailers.loc[:, cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    queries = {}
    fields = [
        'formatted_address',
        'formatted_phone_number',
        'geometry/location/lat',
        'geometry/location/lng',
        'website',
    ]
    retailers = retailers.reset_index(drop=True)
    retailers = retailers.assign(
        premise_street_address=None,
        premise_county=None,
        premise_latitude=None,
        premise_longitude=None,
        business_website=None,
        business_phone=None,
    )
    for index, row in retailers.iterrows():
        query = row['query']
        gis_data = queries.get(query)
        if gis_data is None:
            try:
                gis_data = search_for_address(query, api_key=api_key, fields=fields)
            except:
                gis_data = {}
            queries[query] = gis_data
        retailers.iat[index, retailers.columns.get_loc('premise_street_address')] = gis_data.get('street')
        retailers.iat[index, retailers.columns.get_loc('premise_county')] = gis_data.get('county')
        retailers.iat[index, retailers.columns.get_loc('premise_latitude')] = gis_data.get('latitude')
        retailers.iat[index, retailers.columns.get_loc('premise_longitude')] = gis_data.get('longitude')
        retailers.iat[index, retailers.columns.get_loc('business_website')] = gis_data.get('website')
        retailers.iat[index, retailers.columns.get_loc('business_phone')] = gis_data.get('formatted_phone_number')
    
    # Clean-up after getting GIS data.
    retailers.drop(columns=['query'], inplace=True)

    # TODO: Merge retailer fields with licenses.
    new_fields = [
        'license_number',
        'premise_street_address',
        'premise_county',
        'premise_latitude',
        'premise_longitude',
        'business_website',
        'business_phone'
    ]
    licenses = pd.merge(licenses, retailers[new_fields], how='left', on='license_number')
    licenses.loc[licenses['business_phone_y'].notna(), 'business_phone_x'] = licenses['business_phone_y']
    licenses.drop(columns=['business_phone_y'], inplace=True)
    licenses.rename(columns={'business_phone_x': 'business_phone'}, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().strftime('%Y-%m-%d')
        labs = licenses.loc[licenses['license_type'] == 'Testing Facilities']
        labs.to_csv(f'{data_dir}/labs-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
    return licenses


# === Test ===
# [✓] Tested: 2023-12-17 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':
    
    # Specify where your data lives.
    DATA_DIR = '../data/co'
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
    data = get_licenses_co(data_dir, env_file=env_file)
