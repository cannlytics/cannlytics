"""
Cannabis Licenses | Get Alaska Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/6/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Alaska cannabis license data.

Data Source:

    - Department of Commerce, Community, and Economic Development
    Alcohol and Marijuana Control Office
    URL: <https://www.commerce.alaska.gov/abc/marijuana/Home/licensesearch>

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports.
from cannlytics.data.gis import search_for_address
from dotenv import dotenv_values
import pandas as pd

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
try:
    import chromedriver_binary  # Adds chromedriver binary to path.
except ImportError:
    pass # Otherwise, ChromeDriver should be in your path.


# Specify where your data lives.
DATA_DIR = '../data/ak'
ENV_FILE = '../.env'

# Specify state-specific constants.
STATE = 'AK'
ALASKA = {
    'licensing_authority_id': 'AAMCO',
    'licensing_authority': 'Alaska Alcohol and Marijuana Control Office',
    'licenses_url': 'https://www.commerce.alaska.gov/abc/marijuana/Home/licensesearch',
    'licenses': {
        'columns': {
            'License #': 'license_number',
            'Business License #': 'id',
            'Doing Business As': 'business_dba_name',
            'License Type': 'license_type',
            'License Status': 'license_status',
            'Physical Address': 'address',
        },
    },
}


def get_licenses_ak(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Alaska cannabis license data."""

    # Initialize Selenium and specify options.
    service = Service()
    options = Options()
    options.add_argument('--window-size=1920,1200')

    # DEV: Run with the browser open.
    # options.headless = False

    # PRODUCTION: Run with the browser closed.
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Initiate a Selenium driver.
    driver = webdriver.Chrome(options=options, service=service)

    # Load the license page.
    driver.get(ALASKA['licenses_url'])

    # Get the license type select.
    license_types = []
    options = driver.find_elements(by=By.TAG_NAME, value='option')
    for option in options:
        text = option.text
        if text:
            license_types.append(text)

    # Iterate over all of the license types.
    data = []
    columns = list(ALASKA['licenses']['columns'].values())
    for license_type in license_types:

        # Set the text into the select.
        select = driver.find_element(by=By.ID, value='SearchLicenseTypeID')
        select.send_keys(license_type)

        # Click search.
        # TODO: There is probably an elegant way to wait for the table to load.
        search_button = driver.find_element(by=By.ID, value='mariSearchBtn')
        search_button.click()
        sleep(2)

        # Extract the table data.
        table = driver.find_element(by=By.TAG_NAME, value='tbody')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        for row in rows:
            obs = {}
            cells = row.find_elements(by=By.TAG_NAME, value='td')
            for i, cell in enumerate(cells):
                column = columns[i]
                obs[column] = cell.text.replace('\n', ', ')
            data.append(obs)

    # End the browser session.
    service.stop()

    # Standardize the license data.
    licenses = pd.DataFrame(data)
    licenses = licenses.assign(
        business_legal_name=licenses['business_dba_name'],
        business_owner_name=None,
        business_structure=None,
        licensing_authority_id=ALASKA['licensing_authority_id'],
        licensing_authority=ALASKA['licensing_authority'],
        license_designation='Adult-Use',
        license_status_date=None,
        license_term=None,
        premise_state=STATE,
        parcel_number=None,
        activity=None,
        issue_date=None,
        expiration_date=None,
    )

    # Restrict the license status to active.
    active_license_types = [
        'Active-Operating',
        'Active-Pending Inspection',
        'Delegated',
        'Complete',
    ]
    licenses = licenses.loc[licenses['license_status'].isin(active_license_types)]

    # Assign the city and zip code.
    licenses['premise_city'] = licenses['address'].apply(
        lambda x: x.split(', ')[1]
    )
    licenses['premise_zip_code'] = licenses['address'].apply(
        lambda x: x.split(', ')[2].replace(STATE, '').strip()
    )

    # Search for address for each retail license.
    # Only search for a query once, then re-use the response.
    # Note: There is probably a much, much more efficient way to do this!!!
    config = dotenv_values(env_file)
    api_key = config['GOOGLE_MAPS_API_KEY']
    queries = {}
    fields = [
        'formatted_address',
        'formatted_phone_number',
        'geometry/location/lat',
        'geometry/location/lng',
        'website',
    ]
    licenses = licenses.reset_index(drop=True)
    licenses = licenses.assign(
        premise_street_address=None,
        premise_county=None,
        premise_latitude=None,
        premise_longitude=None,
        business_phone=None,
        business_website=None,
    )
    for index, row in licenses.iterrows():

        # Query Google Place API, if necessary.
        query = ', '.join([row['business_dba_name'], row['address']])
        gis_data = queries.get(query)
        if gis_data is None:
            try:
                gis_data = search_for_address(query, api_key=api_key, fields=fields)
            except:
                gis_data = {}
            queries[query] = gis_data

        # Record the query.
        licenses.iat[index, licenses.columns.get_loc('premise_street_address')] = gis_data.get('street')
        licenses.iat[index, licenses.columns.get_loc('premise_county')] = gis_data.get('county')
        licenses.iat[index, licenses.columns.get_loc('premise_latitude')] = gis_data.get('latitude')
        licenses.iat[index, licenses.columns.get_loc('premise_longitude')] = gis_data.get('longitude')
        licenses.iat[index, licenses.columns.get_loc('business_phone')] = gis_data.get('formatted_phone_number')
        licenses.iat[index, licenses.columns.get_loc('business_website')] = gis_data.get('website')

    # Clean-up after GIS.
    licenses.drop(columns=['address'], inplace=True)

    # Optional: Search for business website for email and a photo.
    licenses['business_email'] = None
    licenses['business_image_url'] = None

    # Get the refreshed date.
    licenses['data_refreshed_date'] = datetime.now().isoformat()

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers = licenses.loc[licenses['license_type'] == 'Retail Marijuana Store']
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
    return licenses


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
    data = get_licenses_ak(data_dir, env_file=env_file)
