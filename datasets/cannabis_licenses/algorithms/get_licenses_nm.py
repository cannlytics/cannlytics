"""
Cannabis Licenses | Get New Mexico Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect New Mexico cannabis license data.

Data Source:

    - New Mexico Regulation and Licensing Department | Cannabis Control Division
    URL: <https://nmrldlpi.force.com/bcd/s/public-search-license?division=CCD&language=en_US>

TODO:
    - [ ] Also collect:
        * "Cannabis Manufacturer"
        * "Cannabis Producer"
        * "Cannabis Producer Microbusiness"
    - [ ] Replace `sleep` with `WebDriverWait` where possible.
    - [ ] Handle multiple search results for a single address.
    - [ ] Ensure geocoding is working correctly.

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports.
from cannlytics.data.gis import geocode_addresses, search_for_address
from dotenv import dotenv_values
import pandas as pd

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
DATA_DIR = '../data/nm'
ENV_FILE = '../../../.env'

# Specify state-specific constants.
STATE = 'NM'
NEW_MEXICO = {
    'licensing_authority_id': 'NMCCD',
    'licensing_authority': 'New Mexico Cannabis Control Division',
    'licenses_url': 'https://nmrldlpi.force.com/bcd/s/public-search-license?division=CCD&language=en_US',
}


def get_licenses_nm(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
        verbose: Optional[bool] = True,
    ):
    """Get New Mexico cannabis license data."""

    # Load environment variables.
    geocode = False
    try:
        config = dotenv_values(env_file)
        api_key = config['GOOGLE_MAPS_API_KEY']
        geocode = True
        if verbose:
            print('Retrieved Google Maps API key for geocoding addresses.')
    except:
        print('Proceeding without geocoding. Set `GOOGLE_MAPS_API_KEY` in your `env_file` to enable the geocoding of addresses.')

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
    if verbose:
        print('Driver initialized. Loading license page...')
    driver.get(NEW_MEXICO['licenses_url'])

    # FIXME: Wait for the page to load by waiting to detect the image.
    # try:
    #     el = (By.CLASS_NAME, 'slds-radio--faux')
    #     WebDriverWait(driver, 15).until(EC.presence_of_element_located(el))
    # except TimeoutException:
    #     print('Failed to load page within %i seconds.' % (30))
    sleep(5)

    # Get the main content and click "License Type" radio.
    content = driver.find_element(by=By.CLASS_NAME, value='siteforceContentArea')
    radio = content.find_element(by=By.CLASS_NAME, value='slds-radio--faux')
    radio.click()
    sleep(2)

    # Select retailers.
    # TODO: Also get "Cannabis Manufacturer", "Cannabis Producer", and
    # "Cannabis Producer Microbusiness".
    search = content.find_element(by=By.ID, value='comboboxId-40')
    search.click()
    choices = content.find_elements(by=By.CLASS_NAME, value='slds-listbox__item')
    for choice in choices:
        if choice.text == 'Cannabis Retailer':
            if verbose:
                print('Searching cannabis retailers...')
            choice.click()
            sleep(2)
            break

    # Click the search button.
    search = content.find_element(by=By.CLASS_NAME, value='vlocity-btn')
    search.click()
    sleep(2)

    # Iterate over all of the pages.
    # Wait for the table to load, then iterate over the pages.
    sleep(5)
    data = []
    iterate = True
    if verbose:
        print('Getting all licenses...')
    while(iterate):

        # Get all of the licenses.
        items = content.find_elements(by=By.CLASS_NAME, value='block-container')
        for item in items[3:]:
            text = item.text
            if not text:
                continue
            values = text.split('\n')
            data.append({
                'license_type': values[0],
                'license_status': values[1],
                'business_legal_name': values[2],
                'address': values[-1],
                'details_url': '',
            })

        # Get the page number and stop at the last page.
        par = content.find_elements(by=By.TAG_NAME, value='p')[-1].text
        page_number = int(par.split(' ')[2])
        total_pages = int(par.split(' ')[-2])
        if verbose:
            print('Retrieved licenses from page %i/%i' % (page_number, total_pages))
        if page_number == total_pages:
            iterate = False

        # Otherwise, click the next button.
        buttons = content.find_elements(by=By.TAG_NAME, value='button')
        for button in buttons:
            if button.text == 'Next Page':
                try:
                    button.click()
                except:
                    break
                sleep(5)
                break

    # Search for each license name, 1 by 1, to get details.
    retailers = pd.DataFrame(columns=['business_legal_name'])
    if verbose:
        print('Getting details for %i licenses...' % len(data))
    for i, licensee in enumerate(data):

        # Skip recorded rows.
        if len(retailers.loc[retailers['business_legal_name'] == licensee['business_legal_name']]):
            continue

        # Click the "Business Name" search field.
        sleep(2)
        content = driver.find_element(by=By.CLASS_NAME, value='siteforceContentArea')
        radio = content.find_elements(by=By.CLASS_NAME, value='slds-radio--faux')[1]
        radio.click()
        sleep(1)

        # Enter the `business_legal_name` into the search.
        search_field = content.find_element(by=By.CLASS_NAME, value='vlocity-input')
        search_field.clear()
        search_field.send_keys(licensee['business_legal_name'])

        # Click the search button.
        search = content.find_element(by=By.CLASS_NAME, value='vlocity-btn')
        search.click()

        # Wait for the table to load.
        # TODO: Prefer to use WebDriverWait over sleep.
        # WebDriverWait(content, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'slds-button_icon')))
        sleep(3)

        # Click the "Action" button to get to the details page.
        # FIXME: There can be multiple search candidates! How to handle this?
        action = content.find_element(by=By.CLASS_NAME, value='slds-button_icon')
        try:
            action.click()
        except:
            # TODO: Formally check if "No record found!".
            continue

        # Wait for the details page to load.
        # TODO: Prefer to use WebDriverWait over sleep.
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'body')))
        sleep(5)

        # Get the page
        page = driver.find_element(by=By.CLASS_NAME, value='body')

        # Get all of the details!
        fields = [
            'license_number',
            'license_status',
            'issue_date',
            'expiration_date',
            'business_owner_name',
        ]
        values = page.find_elements(by=By.CLASS_NAME, value='field-value')
        if len(values) > 5:
            for j, value in enumerate(values[:5]):
                data[i][fields[j]] = value.text
            for value in values[5:]:
                data[i]['business_owner_name'] += f', {value.text}'
        else:
            for j, value in enumerate(values):
                data[i][fields[j]] = value.text

        # Create multiple entries for each address.
        premises = page.find_elements(by=By.CLASS_NAME, value='block-header')
        for premise in premises:
            values = premise.text.split('\n')
            licensee['address'] = values[0].replace(',', ', ')
            licensee['license_number'] = values[2]
            retailers = pd.concat([retailers, pd.DataFrame([licensee])])

        # Scroll to the bottom of the page.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

        # Click the "Back to Search" button.
        if verbose:
            print('%i. Details collected for %s' % (i + 1, licensee['business_legal_name']))
        try:
            back_button = page.find_element(by=By.CLASS_NAME, value='vlocity-btn')
            back_button.click()
        except:
            driver.get(NEW_MEXICO['licenses_url']) # FIXME: Hot-fix.

    # End the browser session.
    try:
        driver.close()
    except:
        pass

    # Standardize the data, restricting to "Approved" retailers.
    retailers = retailers.loc[retailers['license_status'] == 'Active']
    retailers = retailers.assign(
        business_email=None,
        business_structure=None,
        licensing_authority_id=NEW_MEXICO['licensing_authority_id'],
        licensing_authority=NEW_MEXICO['licensing_authority'],
        license_designation='Adult-Use',
        license_status_date=None,
        license_term=None,
        premise_state=STATE,
        parcel_number=None,
        activity=None,
        business_image_url=None,
        business_website=None,
        business_phone=None,
        id=retailers['license_number'],
        business_dba_name=retailers['business_legal_name'],
    )

    # Get the refreshed date.
    retailers['data_refreshed_date'] = datetime.now().isoformat()

    # Geocode licenses.
    if geocode:

        # FIXME: This is not working as intended.
        # Perhaps try `search_for_address`?
        retailers = geocode_addresses(retailers, api_key=api_key, address_field='address')
        retailers['premise_street_address'] = retailers['formatted_address'].apply(
            lambda x: x.split(',')[0] if STATE in str(x) else x
        )
        retailers['premise_city'] = retailers['formatted_address'].apply(
            lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
        )
        retailers['premise_zip_code'] = retailers['formatted_address'].apply(
            lambda x: x.split(', ')[2].split(',')[0].split(' ')[-1] if STATE in str(x) else x
        )
        drop_cols = ['state', 'state_name', 'address', 'formatted_address',
            'details_url']
        gis_cols = {
            'county': 'premise_county',
            'latitude': 'premise_latitude',
            'longitude': 'premise_longitude'
        }
        retailers.drop(columns=drop_cols, inplace=True)
        retailers.rename(columns=gis_cols, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        date = datetime.now().isoformat()[:10]
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-latest.csv', index=False)

    # Return the licenses.
    return retailers


# === Test ===
# [✓] Tested: 2023-08-14 by Keegan Skeate <keegan@cannlytics>
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
    data = get_licenses_nm(data_dir, env_file=env_file)
