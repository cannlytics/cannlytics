"""
Cannabis Licenses | Get Michigan Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/8/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Michigan cannabis license data.

Data Source:

    - Michigan Cannabis Regulatory Agency
    URL: <https://michigan.maps.arcgis.com/apps/webappviewer/index.html?id=cd5a1a76daaf470b823a382691c0ff60>

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports.
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
try:
    import chromedriver_binary  # Adds chromedriver binary to path.
except ImportError:
    pass # Otherwise, ChromeDriver should be in your path.


# Specify where your data lives.
DATA_DIR = '../data/mi'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'MI'
MICHIGAN = {
    'licensing_authority_id': 'CRA',
    'licensing_authority': 'Michigan Cannabis Regulatory Agency',
    'licenses_url': 'https://aca-prod.accela.com/MIMM/Cap/CapHome.aspx?module=Adult_Use&TabName=Adult_Use',
    'medicinal_url': 'https://aca-prod.accela.com/MIMM/Cap/CapHome.aspx?module=Licenses&TabName=Licenses&TabList=Home%7C0%7CLicenses%7C1%7CAdult_Use%7C2%7CEnforcement%7C3%7CRegistryCards%7C4%7CCurrentTabIndex%7C1',
    'licenses': {
        'columns': {
            'Record Number': 'license_number',
            'Record Type': 'license_type',
            'License Name': 'business_legal_name',
            'Address': 'address',
            'Expiration Date': 'expiration_date',
            'Status': 'license_status',
            'Action': 'activity',
            'Notes': 'license_designation',
            'Disciplinary Action': 'license_term',
        },
    },
}


def wait_for_id_invisible(driver, value, seconds=30):
    """Wait for a given value to be invisible."""
    WebDriverWait(driver, seconds).until(
        EC.invisibility_of_element((By.ID, value))
    )


def get_licenses_mi(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Michigan cannabis license data."""

    # Initialize Selenium.
    try:
        service = Service()
        options = Options()
        options.add_argument('--window-size=1920,1200')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options, service=service)
    except:
        driver = webdriver.Edge()

    # Load the license page.
    url = MICHIGAN['licenses_url']
    driver.get(url)

    # Get the various license types, excluding certain types without addresses.
    select = Select(driver.find_element(by=By.TAG_NAME, value='select'))
    license_types = []
    options = driver.find_elements(by=By.TAG_NAME, value='option')
    for option in options:
        text = option.text
        if text and '--' not in text:
            license_types.append(text)
    
    # Restrict certain license types.
    license_types = license_types[1:-2]

    # FIXME: Iterate over license types.
    data = []
    columns = list(MICHIGAN['licenses']['columns'].values())
    for license_type in license_types:

        # Select the various license types.
        try:
            select.select_by_visible_text(license_type)
        except:
            pass
        wait_for_id_invisible(driver, 'divGlobalLoading')

        # Click the search button.
        search_button = driver.find_element(by=By.ID, value='ctl00_PlaceHolderMain_btnNewSearch')
        search_button.click()
        wait_for_id_invisible(driver, 'divGlobalLoading')

        # Iterate over all of the pages.
        iterate = True
        while iterate:

            # Get all of the license data.
            grid = driver.find_element(by=By.ID, value='ctl00_PlaceHolderMain_dvSearchList')
            rows = grid.find_elements(by=By.TAG_NAME, value='tr')
            rows = [x.text for x in rows]
            rows = [x for x in rows if 'Download results' not in x and not x.startswith('< Prev')]
            cells = []
            for row in rows[1:]: # Skip the header.
                obs = {}
                cells = row.split('\n')
                for i, cell in enumerate(cells):
                    column = columns[i]
                    obs[column] = cell
                data.append(obs)

            # Keep clicking the next button until the next button is disabled.
            next_button = driver.find_elements(by=By.CLASS_NAME, value='aca_pagination_PrevNext')[-1]
            current_page = driver.find_element(by=By.CLASS_NAME, value='SelectedPageButton').text
            next_button.click()
            wait_for_id_invisible(driver, 'divGlobalLoading')
            next_page = driver.find_element(by=By.CLASS_NAME, value='SelectedPageButton').text
            if current_page == next_page:
                iterate = False

    # TODO: Also get all of the medical licenses!
    # https://aca-prod.accela.com/MIMM/Cap/CapHome.aspx?module=Licenses&TabName=Licenses&TabList=Home%7C0%7CLicenses%7C1%7CAdult_Use%7C2%7CEnforcement%7C3%7CRegistryCards%7C4%7CCurrentTabIndex%7C1

    # End the browser session.
    service.stop()

    # Standardize the data.
    licenses = pd.DataFrame(data)
    licenses = licenses.assign(
        id=licenses.index,
        licensing_authority_id=MICHIGAN['licensing_authority_id'],
        licensing_authority=MICHIGAN['licensing_authority'],
        premise_state=STATE,
        license_status_date=None,
        issue_date=None,
        business_owner_name=None,
        business_structure=None,
        parcel_number=None,
        business_phone=None,
        business_email=None,
        business_image_url=None,
        license_designation=None,
        business_website=None,
        business_dba_name=licenses['business_legal_name'],
    )

    # Assign `license_term` if necessary.
    try:
        licenses['license_term']
    except KeyError:
        licenses['license_term'] = None

    # Clean `license_type`.
    licenses['license_type'] = licenses['license_type'].apply(
        lambda x: x.replace(' - License', '')
    )

    # Format expiration date as an ISO formatted date.
    licenses['expiration_date'] = licenses['expiration_date'].apply(
        lambda x: pd.to_datetime(x).isoformat()
    )

    # Geocode the licenses.
    config = dotenv_values(env_file)
    google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    licenses = geocode_addresses(
        licenses,
        api_key=google_maps_api_key,
        address_field='address',
    )
    licenses['premise_street_address'] = licenses['formatted_address'].apply(
        lambda x: x.split(',')[0] if STATE in str(x) else x
    )
    licenses['premise_city'] = licenses['formatted_address'].apply(
        lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    )
    licenses['premise_zip_code'] = licenses['formatted_address'].apply(
        lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1] if STATE in str(x) else x
    )
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    gis_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    licenses.drop(columns=drop_cols, inplace=True)
    licenses.rename(columns=gis_cols, inplace=True)

    # Get the refreshed date.
    licenses['data_refreshed_date'] = datetime.now().isoformat()

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
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
    data = get_licenses_mi(data_dir, env_file=env_file)
