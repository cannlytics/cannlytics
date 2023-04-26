"""
Cannabis Licenses | Get Maryland Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 4/25/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Maryland cannabis license data.

Data Source:

    - Maryland Medical Cannabis Commission
    URL: <https://mmcc.maryland.gov/Pages/Dispensaries.aspx>

"""
# Standard imports:
from datetime import datetime
import os
import re
from typing import Optional
from urllib.parse import urlparse

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/md'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'MD'
MARYLAND = {
    'licensing_authority_id': 'MMCC',
    'licensing_authority': 'Maryland Medical Cannabis Commission',
    'licenses_url': 'https://mmcc.maryland.gov/Pages/Dispensaries.aspx',
}


def get_gis_data(df, api_key):
    """Get GIS data."""
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    rename_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    df = geocode_addresses(
        df,
        api_key=api_key,
        address_field='address',
    )
    df['premise_city'] = df['formatted_address'].apply(
        lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    )
    df.drop(columns=drop_cols, inplace=True)
    return df.rename(columns=rename_cols)


def get_licenses_md(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Maryland cannabis license data."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Get the license webpage.
    url = MARYLAND['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #  Extract the license data.
    data = []
    for td in soup.find_all('td'):
        entry = {}

        # Record license data if there is an image.
        img = td.find('img')
        if img:

            # TODO: Record the image.
            # entry['image'] = img['src']

            # Record the email and website.
            entry['business_website'] = None
            links = td.find_all('a')
            for link in links:
                if 'mailto' in link['href']:
                    entry['business_email'] = link['href'][7:]
                elif 'http' in link['href']:
                    entry['business_website'] = link['href']

            # Handle plain text websites.
            if entry['business_website'] is None and entry['business_email']:
                domain = entry['business_email'].split('@')[1]
                entry['business_website'] = 'https://www.' + domain

            # FIXME: This is a hack to get the business name.
            entry['business_legal_name'] = img['alt']
            if not entry['business_legal_name']:
                parsed_url = urlparse(url)
                entry['business_legal_name'] = parsed_url.netloc.split('.')[0].title()

            # Find phone numbers in text.
            # Uses regular expression to match: xxx-xxx-xxxx
            text = td.text.strip()
            phone_number_pattern = re.compile(r'\d{3}-\d{3}-\d{4}')
            phone_numbers = phone_number_pattern.findall(text)
            if phone_numbers:
                entry['business_phone'] = phone_numbers[0]
            else:
                entry['business_phone'] = None

            # Find address in the text.
            # Uses regular expression to match "City, State Zip" pattern.
            # Assumes the previous lines contains the street address.
            lines = text.replace('\u200b', '').split('\n')
            lines = [x for x in lines if x]
            city_state_zip_pattern = re.compile(r'\b[A-Za-z\s]+,\s[A-Z]{2}\s\d{5}\b')
            for i in range(len(lines)):
                line = lines[i].strip()
                if city_state_zip_pattern.search(line):
                    index = i - 1
                    if index > 0:
                        street = lines[:index].join().strip()
                    else:
                        street = lines[index].strip()
                    entry['premise_street_address'] = f'{street} {line}'
        
        # Otherwise record just the name and address.
        else:
            lines = [x.text.replace('\u200b', '') for x in td.contents]
            lines = [x for x in lines if x]
            if not lines:
                continue
            entry['business_legal_name'] = lines[0].strip()
            address = ', '.join(line.strip() for line in lines[1:])
            address = address.replace('\xa0', '')
            entry['premise_street_address'] = address

            # Look for phone number below address.
            phone_number_pattern = re.compile(r'\d{3}-\d{3}-\d{4}')
            phone_numbers = phone_number_pattern.findall(address)
            if phone_numbers:
                entry['business_phone'] = phone_numbers[0]
                entry['premise_street_address'] = address.replace(phone_numbers[0], '').strip()
            else:
                entry['business_phone'] = None

        # Add the entry to the data.
        data.append(entry)

    # Standardize the license data.
    retailers = pd.DataFrame(data)
    retailers = retailers.assign(
        id=retailers.index,
        license_status=None,
        business_dba_name=retailers['business_legal_name'],
        license_number=None,
        licensing_authority_id=MARYLAND['licensing_authority_id'],
        licensing_authority=MARYLAND['licensing_authority'],
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

    # # FIXME: Format street, city, state, and zip code.
    # pattern = r'^(.*),\s*([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})$'
    # addresses = retailers['premise_street_address'].str.extract(pattern)
    # retailers[['premise_street_address', 'street', 'city', 'state', 'zip_code']] = addresses

    # # FIXME: Get GIS data.
    # if google_maps_api_key:
    #     retailers = get_gis_data(retailers, google_maps_api_key)

    # Define metadata.
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)

    # Return the licenses.
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
    data = get_licenses_md(data_dir, env_file=env_file)
