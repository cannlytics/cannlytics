"""
Cannabis Licenses | Get Montana Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/27/2022
Updated: 10/5/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Montana cannabis license data.

Data Source:

    - Montana Department of Revenue | Cannabis Control Division
    URL: <https://mtrevenue.gov/cannabis/#CannabisLicenses>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
from cannlytics.data.gis import search_for_address
from cannlytics.utils.constants import DEFAULT_HEADERS
from dotenv import dotenv_values
import pandas as pd
import pdfplumber
import requests


# Specify where your data lives.
DATA_DIR = '../data/mt'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'MT'
MONTANA = {
    'licensing_authority_id': 'MTCCD',
    'licensing_authority': 'Montana Cannabis Control Division',
    'licenses': {
        'columns': [
            {
                'key': 'premise_city',
                'name': 'City',
                'area': [0, 0.25, 0.2, 0.95],
            },
            {
                'key': 'business_legal_name',
                'name': 'Location Name',
                'area': [0.2, 0.25, 0.6, 0.95],
            },
            {
                'key': 'license_designation',
                'name': 'Sales Type',
                'area': [0.6, 0.25, 0.75, 0.95],
            },
            {
                'key': 'business_phone',
                'name': 'Phone Number',
                'area': [0.75, 0.25, 1, 0.95],
            },
        ]
    },
    'retailers': {
        'url': 'https://mtrevenue.gov/?mdocs-file=60245',
        'columns': ['city', 'dba', 'license_type', 'phone']
    },
    'processors': {'url': 'https://mtrevenue.gov/?mdocs-file=60250'},
    'cultivators': {'url': 'https://mtrevenue.gov/?mdocs-file=60252'},
    'labs': {'url': 'https://mtrevenue.gov/?mdocs-file=60248'},
    'transporters': {'url': 'https://mtrevenue.gov/?mdocs-file=72489'},
}


def get_licenses_mt(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Montana cannabis license data."""

    # Create directories if necessary.
    pdf_dir = f'{data_dir}/pdfs'
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)

    # Download the retailers PDF.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    outfile = f'{pdf_dir}/mt-retailers-{timestamp}.pdf'
    response = requests.get(MONTANA['retailers']['url'], headers=DEFAULT_HEADERS)
    with open(outfile, 'wb') as pdf:
        pdf.write(response.content)

    # Read the PDF.
    doc = pdfplumber.open(outfile)

    # Get the table rows.
    rows = []
    front_page = doc.pages[0]
    width, height = front_page.width, front_page.height
    x0, y0, x1, y1 = tuple([0, 0.25, 1, 0.95])
    page_area = (x0 * width, y0 * height, x1 * width, y1 * height)
    for page in doc.pages:
        crop = page.within_bbox(page_area)
        text = crop.extract_text()
        lines = text.split('\n')
        for line in lines:
            rows.append(line)

    # Get cities from the first column, used to identify the city for each line.
    cities = []
    city_area = MONTANA['licenses']['columns'][0]['area']
    x0, y0, x1, y1 = tuple(city_area)
    column_area = (x0 * width, y0 * height, x1 * width, y1 * height)
    for page in doc.pages:
        crop = page.within_bbox(column_area)
        text = crop.extract_text()
        lines = text.split('\n')
        for line in lines:
            cities.append(line)

    # Find all of the unique cities.
    cities = list(set(cities))
    cities = [x for x in cities if x != 'City']

    # Get all of the license data.
    data = []
    rows = [x for x in rows if not x.startswith('City')]
    for row in rows:

        # Get all of the license observation data.
        obs = {}
        text = str(row)

        # Identify the city and remove the city from the name (only once b/c of DBAs!).
        for city in cities:
            if city in row:
                obs['premise_city'] = city.title()
                text = text.replace(city, '', 1).strip()
                break

        # Identify the license designation.
        if 'Adult Use' in row:
            parts = text.split('Adult Use')
            obs['license_designation'] = 'Adult Use'
        else:
            parts = text.split('Medical Only')
            obs['license_designation'] = 'Medical Only'
        
        # Skip rows with double-row text.
        if len(row) == 1: continue

        # Record the name.
        obs['business_legal_name'] = name = parts[0]

        # Record the phone number.
        if '(' in text:
            obs['business_phone'] = parts[-1].strip()

        # Record the observation.
        data.append(obs)

    # Aggregate the data.
    retailers = pd.DataFrame(data)
    retailers = retailers.loc[~retailers['premise_city'].isna()]

    # Convert certain columns from upper case title case.
    cols = ['business_legal_name', 'premise_city']
    for col in cols:
        retailers[col] = retailers[col].apply(
            lambda x: x.title().replace('Llc', 'LLC').replace("'S", "'s").strip()
        )

    # Standardize the data.
    retailers['id'] = retailers.index
    retailers['license_number'] = None # FIXME: It would be awesome to find these!
    retailers['licensing_authority_id'] = MONTANA['licensing_authority_id']
    retailers['licensing_authority'] = MONTANA['licensing_authority']
    retailers['premise_state'] = STATE
    retailers['license_status'] = 'Active'
    retailers['license_status_date'] = None
    retailers['license_type'] = 'Commercial - Retailer'
    retailers['license_term'] = None
    retailers['issue_date'] = None
    retailers['expiration_date'] = None
    retailers['business_owner_name'] = None
    retailers['business_structure'] = None
    retailers['activity'] = None
    retailers['parcel_number'] = None
    retailers['business_email'] = None
    retailers['business_image_url'] = None

    # Separate any `business_dba_name` from `business_legal_name`.
    retailers['business_dba_name'] = retailers['business_legal_name']
    criterion = retailers['business_legal_name'].str.contains('Dba')
    retailers.loc[criterion, 'business_dba_name'] = retailers.loc[criterion] \
        ['business_legal_name'].apply(lambda x: x.split('Dba')[-1].strip())
    retailers.loc[criterion, 'business_legal_name'] = retailers.loc[criterion] \
        ['business_legal_name'].apply(lambda x: x.split('Dba')[0].strip())

    # Search for address for each retail license.
    # Only search for a query once, then re-use the response.
    # Note: There is probably a much, much more efficient way to do this!!!
    config = dotenv_values(env_file)
    api_key = config['GOOGLE_MAPS_API_KEY']
    cols = ['business_dba_name', 'premise_city', 'premise_state']
    retailers['query'] = retailers[cols].apply(
        lambda row: ', '.join(row.values.astype(str)),
        axis=1,
    )
    queries = {}
    fields = [
        'formatted_address',
        'geometry/location/lat',
        'geometry/location/lng',
        'website',
    ]
    retailers = retailers.reset_index(drop=True)
    retailers = retailers.assign(
        premise_street_address=None,
        premise_county=None,
        premise_zip_code=None,
        premise_latitude=None,
        premise_longitude=None,
        business_website=None,
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
        retailers.iat[index, retailers.columns.get_loc('premise_zip_code')] = gis_data.get('zipcode')
        retailers.iat[index, retailers.columns.get_loc('premise_latitude')] = gis_data.get('latitude')
        retailers.iat[index, retailers.columns.get_loc('premise_longitude')] = gis_data.get('longitude')
        retailers.iat[index, retailers.columns.get_loc('business_website')] = gis_data.get('website')
        
    # Clean-up after getting GIS data.
    retailers.drop(columns=['query'], inplace=True)

    # Get the refreshed date.
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
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
    data = get_licenses_mt(data_dir, env_file=env_file)
