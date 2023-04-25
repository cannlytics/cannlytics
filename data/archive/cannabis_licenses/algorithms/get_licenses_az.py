"""
Cannabis Licenses | Get Arizona Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/27/2022
Updated: 4/24/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Arizona cannabis license data.

Data Source:

    - Arizona Department of Health Services | Division of Licensing
    URL: <https://azcarecheck.azdhs.gov/s/?licenseType=null>

"""
# Standard imports.
from datetime import datetime
# from dotenv import dotenv_values
import os
from time import sleep
from typing import Optional

# External imports.
# from cannlytics.data.gis import geocode_addresses
import pandas as pd
import zipcodes

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# try:
#     import chromedriver_binary  # Adds chromedriver binary to path.
# except ImportError:
#     pass # Otherwise, ChromeDriver should be in your path.


# Specify where your data lives.
DATA_DIR = '../data/az'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'AZ'
ARIZONA = {
    'licensing_authority_id': 'ADHS',
    'licensing_authority': 'Arizona Department of Health Services',
    'licenses_url': 'https://azcarecheck.azdhs.gov/s/?licenseType=null',
}


def county_from_zip(x):
    """Find a county given a zip code. Returns `None` if no match."""
    try:
        return zipcodes.matching(x)[0]['county']
    except KeyError:
        return None


def get_licenses_az(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Arizona cannabis license data."""

    # Create directories if necessary.
    if not os.path.exists(data_dir): os.makedirs(data_dir)

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
    driver.get(ARIZONA['licenses_url'])
    detect = (By.CLASS_NAME, 'slds-container_center')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(detect))

    # Get the map container.
    container = driver.find_element(by=By.CLASS_NAME, value='slds-container_center')

    # Click "Load more" until all of the licenses are visible.
    more = True
    while(more):
        button = container.find_element(by=By.TAG_NAME, value='button')
        driver.execute_script('arguments[0].scrollIntoView(true);', button)
        button.click()
        counter = container.find_element(by=By.CLASS_NAME, value='count-text')
        more = int(counter.text.replace(' more', ''))

    # Get license data for each retailer.
    data = []
    els = container.find_elements(by=By.CLASS_NAME, value='map-list__item')
    for i, el in enumerate(els):

        # Get a retailer's data.
        count = i + 1
        xpath = f'/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div/c-azcc-portal-home/c-azcc-map/div/div[2]/div[2]/div[2]/div[{count}]/c-azcc-map-list-item/div'
        list_item = el.find_element(by=By.XPATH, value=xpath)
        body = list_item.find_element(by=By.CLASS_NAME, value='slds-media__body')
        divs = body.find_elements(by=By.TAG_NAME, value='div')
        name = divs[0].text
        legal_name = divs[1].text
        if not name:
            name = legal_name
        address = divs[3].text
        address_parts = address.split(',')
        parts = divs[2].text.split(' · ')

        # Get the retailer's link to get more details.
        link = divs[-1].find_element(by=By.TAG_NAME, value='a')
        href = link.get_attribute('href')

        # Record the retailer's data.
        obs = {
            'address': address,
            'details_url': href,
            'business_legal_name': legal_name,
            'business_dba_name': name,
            'business_phone': parts[-1],
            'license_status': parts[0],
            'license_type': parts[1],
            'premise_street_address': address_parts[0].strip(),
            'premise_city': address_parts[1].strip(),
            'premise_zip_code': address_parts[-1].replace('AZ ', '').strip(),
        }
        data.append(obs)

    # Standardize the retailer data.
    retailers = pd.DataFrame(data)
    retailers = retailers.assign(
        business_email=None,
        business_owner_name=None,
        business_structure=None,
        business_image_url=None,
        business_website=None,
        id=retailers.index,
        licensing_authority_id=ARIZONA['licensing_authority_id'],
        licensing_authority=ARIZONA['licensing_authority'],
        license_designation='Adult-Use',
        license_number=None,
        license_status_date=None,
        license_term=None,
        premise_latitude=None,
        premise_longitude=None,
        premise_state=STATE,
        issue_date=None,
        expiration_date=None,
        parcel_number=None,
        activity=None,
    )

    # Get each retailer's details.
    cultivators = pd.DataFrame(columns=retailers.columns)
    manufacturers = pd.DataFrame(columns=retailers.columns)
    for index, row in retailers.iterrows():

        # Load the licenses's details webpage.
        driver.get(row['details_url'])
        detect = (By.CLASS_NAME, 'slds-container_center')
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(detect))
        container = driver.find_element(by=By.CLASS_NAME, value='slds-container_center')
        sleep(4)

        # Get the `business_email`.
        links = container.find_elements(by=By.TAG_NAME, value='a')
        for link in links:
            href = link.get_attribute('href')
            if href is None: continue
            if href.startswith('mailto'):
                business_email = href.replace('mailto:', '')
                col = retailers.columns.get_loc('business_email')
                retailers.iat[index, col] = business_email
                break

        # Get the `license_number`
        for link in links:
            href = link.get_attribute('href')
            if href is None: continue
            if href.startswith('https://azdhs-licensing'):
                col = retailers.columns.get_loc('license_number')
                retailers.iat[index, col] = link.text
                break

        # Get the `premise_latitude` and `premise_longitude`.
        for link in links:
            href = link.get_attribute('href')
            if href is None: continue
            if href.startswith('https://maps.google.com/'):
                coords = href.split('=')[1].split('&')[0].split(',')
                lat_col = retailers.columns.get_loc('premise_latitude')
                long_col = retailers.columns.get_loc('premise_longitude')
                retailers.iat[index, lat_col] = float(coords[0])
                retailers.iat[index, long_col] = float(coords[1])
                break

        # Get the `issue_date`.
        key = 'License Effective'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-text")
        col = retailers.columns.get_loc('issue_date')
        retailers.iat[index, col] = el.text

        # Get the `expiration_date`.
        key = 'License Expires'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-text")
        col = retailers.columns.get_loc('expiration_date')
        retailers.iat[index, col] = el.text

        # Get the `business_owner_name`.
        key = 'Owner / License'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-text")
        col = retailers.columns.get_loc('expiration_date')
        retailers.iat[index, col] = el.text

        # Get the `license_designation` ("Services").
        key = 'Services'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-rich-text")
        col = retailers.columns.get_loc('license_designation')
        retailers.iat[index, col] = el.text

        # Create entries for cultivations.
        cultivator = retailers.iloc[index].copy()
        key = 'Offsite Cultivation Address'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-text")
        address = el.text
        if address:
            parts = address.split(',')
            cultivator['address'] = address
            cultivator['premise_street_address'] = parts[0]
            cultivator['premise_city'] = parts[1].strip()
            cultivator['premise_zip_code'] = parts[-1].replace(STATE, '').strip()
            cultivator['license_type'] = 'Offsite Cultivation'
            cultivators.append(cultivator, ignore_index=True)

        # Create entries for manufacturers.
        manufacturer = retailers.iloc[index].copy()
        key = 'Manufacture Address'
        el = container.find_element_by_xpath(f"//p[contains(text(),'{key}')]/following-sibling::lightning-formatted-text")
        address = el.text
        if address:
            parts = address.split(',')
            manufacturer['address'] = address
            manufacturer['premise_street_address'] = parts[0]
            manufacturer['premise_city'] = parts[1].strip()
            manufacturer['premise_zip_code'] = parts[-1].replace(STATE, '').strip()
            manufacturer['license_type'] = 'Offsite Cultivation'
            manufacturers.append(manufacturer, ignore_index=True)

    # End the browser session.
    service.stop()
    retailers.drop(column=['address', 'details_url'], inplace=True)

    # Lookup counties by zip code.
    retailers['premise_county'] = retailers['premise_zip_code'].apply(county_from_zip)
    cultivators['premise_county'] = cultivators['premise_zip_code'].apply(county_from_zip)
    manufacturers['premise_county'] = manufacturers['premise_zip_code'].apply(county_from_zip)

    # Setup geocoding
    # config = dotenv_values(env_file)
    # api_key = config['GOOGLE_MAPS_API_KEY']
    # drop_cols = ['state', 'state_name', 'county', 'address', 'formatted_address']
    # gis_cols = {'latitude': 'premise_latitude', 'longitude': 'premise_longitude'}

    # # Geocode cultivators.
    # cultivators = geocode_addresses(cultivators, api_key=api_key, address_field='address')
    # cultivators.drop(columns=drop_cols, inplace=True)
    # cultivators.rename(columns=gis_cols, inplace=True)

    # # Geocode manufacturers.
    # manufacturers = geocode_addresses(manufacturers, api_key=api_key, address_field='address')
    # manufacturers.drop(columns=drop_cols, inplace=True)
    # manufacturers.rename(columns=gis_cols, inplace=True)

    # TODO: Lookup business website and image.

    # Aggregate all licenses.
    licenses = pd.concat([retailers, cultivators, manufacturers])

    # Get the refreshed date.
    timestamp = datetime.now().isoformat()
    licenses['data_refreshed_date'] = timestamp
    retailers['data_refreshed_date'] = timestamp
    # cultivators['data_refreshed_date'] = timestamp
    # manufacturers['data_refreshed_date'] = timestamp

    # Save and return the data.
    if data_dir is not None:
        timestamp = timestamp[:19].replace(':', '-')
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        # cultivators.to_csv(f'{data_dir}/cultivators-{STATE.lower()}-{timestamp}.csv', index=False)
        # manufacturers.to_csv(f'{data_dir}/manufacturers-{STATE.lower()}-{timestamp}.csv', index=False)
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
    data = get_licenses_az(data_dir, env_file=env_file)
