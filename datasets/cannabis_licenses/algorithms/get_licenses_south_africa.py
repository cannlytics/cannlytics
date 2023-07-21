"""
Get South Africa cannabis license data.
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/10/2023
Updated: 5/15/2023
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>

Data Source:

    - [South Africa Cannabis Licenses](https://www.sahpra.org.za/approved-licences/)

Resources:

    - [South Africa Cannabis Licensing Press Release](https://www.sahpra.org.za/press-releases/cannabis-licensing/)
    - [First-level Administrative Divisions, South Africa, 2015](https://earthworks.stanford.edu/catalog/stanford-js788dt6134)

"""
# Standard imports:
from datetime import datetime
from time import sleep
from typing import Optional

# External imports:
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


# Specify where your data lives.
DATA_DIR = '../data/south-africa'
ENV_FILE = '../../../../.env'


def get_licenses_south_africa(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get South Africa cannabis license data."""

    # Open the licenses webpage.
    url = 'http://www.sahpra.org.za/approved-licences/'
    driver = webdriver.Edge()
    driver.get(url)

    # Click on the cultivations tab.
    sleep(3)
    link = driver.find_element(By.ID, 'ui-id-5')
    link.click()

    # Iterate over all of the pages.
    data = []
    iterate = True
    while iterate:

        # Find the table.
        table = driver.find_element(By.CSS_SELECTOR, '[aria-label="Cannabis Cultivation licences"]')

        # Get all the rows from the table.
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Extract the data from each cell.
        for row in rows[3:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = {
                'business_legal_name': cells[0].text,
                'license_number': cells[1].text,
                'business_owner_name': cells[2].text,
                'premise_state': cells[3].text,
                'issue_date': cells[4].text,
                'expiration_date': cells[5].text,
            }
            data.append(row_data)

        # Click the next button, if not disabled.
        li = driver.find_element(By.CSS_SELECTOR, '[aria-label="next"]')
        action = li.find_element(By.TAG_NAME, 'a')
        style = li.get_attribute('class')
        if 'disabled' in style.split():
            iterate = False
        action.click()
        sleep(3)
    
    # Standardize the license data.
    df = pd.DataFrame(data)
    df['id'] = df['license_number']
    df['licensing_authority_id'] = 'SAHPRA'
    df['licensing_authority'] = 'South African Health Products Regulatory Authority'
    df['license_type'] = 'Medical - Cultivator'
    df['license_status'] = 'Active'
    df['license_status_date'] = None
    df['license_term'] = None
    df['business_structure'] = None
    df['business_email'] = None
    df['activity'] = None
    df['parcel_number'] = None
    df['business_image_url'] = None

    # TODO: Get `data_refreshed_at` from the webpage.

    # TODO: Geocode licenses.

    # Close the browser.
    driver.close()

    # Save the data.
    date = datetime.now().strftime('%Y-%m-%d')
    df.to_csv(f'{data_dir}/licenses-south-africa-{date}.csv', index=False)
    df.to_csv(f'{data_dir}/licenses-south-africa-latest.csv', index=False)

    # Return the licenses.
    return df


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
    data = get_licenses_south_africa(data_dir, env_file=env_file)
