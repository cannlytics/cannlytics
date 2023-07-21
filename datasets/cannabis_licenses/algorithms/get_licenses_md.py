"""
Cannabis Licenses | Get Maryland Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 4/30/2023
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
    df = geocode_addresses(df, api_key=api_key, address_field='address')
    get_city = lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    get_street = lambda x: str(x).split(', ')[0]
    df['premise_city'] = df['formatted_address'].apply(get_city)
    df['premise_street_address'] = df['formatted_address'].apply(get_street)
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

    # Extract the license data.
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

            # Get the business name.
            entry['business_legal_name'] = img['alt']
            if not entry['business_legal_name']:
                parsed_url = urlparse(url)
                entry['business_legal_name'] = parsed_url.netloc.split('.')[0].title()

            # Hot-fix: Get the business name from the website.
            # FIXME: This is sub-perfect.
            if entry['business_legal_name'] == 'Mmcc':
                website = entry['business_website']
                if 'www' in website:
                    entry['business_legal_name'] =  \
                        website \
                        .split('www.')[1] \
                        .split('.')[0] \
                        .title()
                else:
                    entry['business_legal_name'] =  \
                        website \
                        .split('//')[1] \
                        .split('.')[0] \
                        .title()

            # Find phone numbers in text.
            # Note: Uses regular expression to match: xxx-xxx-xxxx
            text = td.text.strip()
            phone_number_pattern = re.compile(r'\d{3}-\d{3}-\d{4}')
            phone_numbers = phone_number_pattern.findall(text)
            if phone_numbers:
                entry['business_phone'] = phone_numbers[0]
            else:
                entry['business_phone'] = None

        # Otherwise record just the name and address.
        else:
            lines = [x.text.replace('\u200b', '') for x in td.contents]
            lines = [x for x in lines if x]
            if not lines:
                continue
            entry['business_legal_name'] = lines[0].strip()

            # Get the street address.
            address = ', '.join(line.strip() for line in lines[1:])
            address = address.replace('\xa0', ' ')
            entry['address'] = address

            # Look for phone number below address.
            phone_number_pattern = re.compile(r'\d{3}-\d{3}-\d{4}')
            phone_numbers = phone_number_pattern.findall(address)
            if phone_numbers:
                entry['business_phone'] = phone_numbers[0]
                entry['address'] = address.split(phone_numbers[0])[0].strip()
            else:
                entry['business_phone'] = None
        
        # Handle missed addresses.
        if not entry.get('address'):
            address = td.text.split(', MD ')[0] \
                .replace('\u200b', ' ') \
                .replace('\n', ' ') \
                .replace('\xa0', ' ') \
                .replace('  ', ' ') \
                .strip()
            zip_code = re.findall(r'MD \b\d{5}\b', td.text)
            if zip_code:
                zip_code = zip_code[0].split('MD ')[-1]
            else:
                zip_code = ''
            address = f'{address}, MD {zip_code}'.strip()

            # Clean address.
            address = address.split('http')[0].strip()
            if entry.get('business_phone'):
                address = address.split(entry['business_phone'])[0].strip()
            if entry.get('business_email'):
                address = address.split(entry['business_email'])[0].strip()
            entry['address'] = address

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

    # Get GIS data.
    if google_maps_api_key:
        retailers = get_gis_data(retailers, google_maps_api_key)

    # Define metadata.
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        date = datetime.now().isoformat()[:10]
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)

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
