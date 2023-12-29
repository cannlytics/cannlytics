"""
Cannabis Licenses | Get Mississippi Licenses
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 12/27/2023
Updated: 12/28/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Mississippi cannabis license data.

Data Source:

    - Mississippi Medical Cannabis Program
    URL: <https://www.mmcp.ms.gov/search_business>

"""
# Standard imports:
from datetime import datetime
import glob
import os
from time import sleep
from typing import Optional

# External imports:
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


# Specify state-specific constants.
STATE = 'MS'
STATE_STATUS = 'Medical'
MISSISSIPPI = {
    'licensing_authority_id': 'MMCP',
    'licensing_authority': 'Mississippi Medical Cannabis Program',
    'licenses_url': 'https://www.mmcp.ms.gov/search_business',
}


def initialize_selenium(
        headless=True,
        download_dir=None
    ):
    """Initialize Selenium."""
    service = Service()
    if download_dir is not None:
        default_directory = os.path.join(os.getcwd(), download_dir)
        default_directory = os.path.normpath(default_directory)
    prefs = {
        'download.default_directory': default_directory,
        'profile.default_content_settings.popups': 0,
        'directory_upgrade': True,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True
    }
    try:
        options = EdgeOptions()
        options.add_experimental_option('prefs', prefs)
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Edge(options=options, service=service)
    except:
        options = Options()
        options.add_argument('--window-size=1920,1200')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('prefs', prefs)
        service = Service()
        driver = webdriver.Chrome(options=options, service=service)
    return driver


def find_most_recent_file(download_dir):
    """Find the most recent file in a directory."""
    files = glob.glob(os.path.join(download_dir, '*'))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        return None
    most_recent_file = max(files, key=os.path.getmtime)
    return most_recent_file


def get_licenses_ms(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
        headless: Optional[bool] = True,
    ):
    """Get Mississippi cannabis license data."""
    # Create directories if necessary.
    download_dir = os.path.join(data_dir, 'raw')
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(download_dir): os.makedirs(download_dir)

    # === Download the data. ===

    # Initialize selenium.
    driver = initialize_selenium(headless=headless, download_dir=download_dir)

    # Get the license page.
    url = 'https://www.mmcp.ms.gov/search_business'
    driver.get(url)
    sleep(4)

    # Download the .csv file.
    download_button = driver.find_element(by=By.CSS_SELECTOR, value="button.buttons-csv.buttons-html5")
    download_button.click()
    sleep(4)

    # Close the browser when done.
    driver.quit()

    # Read the .csv file.
    datafile = find_most_recent_file(download_dir)


    # === Clean the data. ===
    
    data = pd.read_csv(datafile)

    # Delete last column.
    data = data.iloc[:, :-1]

    # Rename columns.
    columns = {
        'License No.': 'license_number',
        'Business Name': 'business_legal_name',
        'Business Type': 'business_type',
        'County': 'county',
        'Expiration': 'expiration_date',
        'License Issue Date': 'issue_date',
        'Owner Name': 'business_owner_name',
        'Physical Address': 'premise_street_address',
        'Mailing Address': 'mailing_street_address',
        'Phone Number': 'business_phone',
        'Email Address': 'business_email',
    }
    data = data.rename(columns=columns)

    # Standardize the data.
    data = data.assign(
        business_structure=None,
        business_image_url=None,
        business_website=None,
        id=data.license_number,
        premise_state=STATE,
        licensing_authority_id=MISSISSIPPI['licensing_authority_id'],
        licensing_authority=MISSISSIPPI['licensing_authority'],
        license_designation=STATE_STATUS,
        license_status_date=None,
        license_term=None,
        issue_date=None,
        expiration_date=None,
        parcel_number=None,
        activity=None,
    )


    # === Geocode the data ===

    # Geocode the retailers.
    google_maps_api_key = dotenv_values(env_file)['GOOGLE_MAPS_API_KEY']
    retailers = data.loc[data['business_type'] == 'Dispensary']
    retailer_gis_data = geocode_addresses(
        retailers,
        api_key=google_maps_api_key,
        address_field='premise_street_address',
    )
    retailer_gis_data = retailer_gis_data.rename(columns={
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude',
        'county': 'premise_county',
    })
    retailer_gis_data.drop(columns=['state', 'state_name', 'formatted_address'], inplace=True)

    # Merge retailer GIS data back with the original data.
    merge_columns = [
        'license_number',
        'premise_latitude',
        'premise_longitude',
        'premise_county',
    ]
    data = pd.merge(
        data,
        retailer_gis_data[merge_columns],
        how='left',
        on='license_number',
    )    

    # === Save the data. ===

    # Save the retailers.
    date = datetime.now().strftime('%Y-%m-%d')
    retailer_gis_data.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{date}.csv', index=False)

    # Save the licenses.
    data.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
    return data


# === Test ===
# [✓] Tested: 2023-12-28 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '../data/ms'
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
    data = get_licenses_ms(data_dir, env_file=env_file)
