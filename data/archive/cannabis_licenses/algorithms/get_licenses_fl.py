"""
Florida cannabis licenses and lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 5/18/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis license data.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)

Resources:

    - 'https://www.reddit.com/r/FLMedicalTrees/search/?q=COA'
    - https://www.reddit.com/r/FLMedicalTrees/comments/1272per/anyone_have_batch_s_they_can_share_for_our/
    - https://www.reddit.com/r/FLMedicalTrees/comments/vdnpqf/coa_accumulation/

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

# Specify where your data lives.
DATA_DIR = '../data/fl'
ENV_FILE = '../../../../.env'


# Specify state-specific constants.
STATE = 'FL'
FLORIDA = {
    'licensing_authority_id': 'CRA',
    'licensing_authority': 'Michigan Cannabis Regulatory Agency',
    'licenses_url': 'https://knowthefactsmmj.com/mmtc/',
    'labs_url': 'https://knowthefactsmmj.com/cmtl/',
    'columns': {
        'Name': 'business_dba_name',
        'Phone': 'business_phone',
        'Email': 'business_email',
        'Authorization Status': 'license_status',
        'License Number': 'license_number',
    }
}


#-----------------------------------------------------------------------
# Get Florida licenses.
#-----------------------------------------------------------------------


def get_labs_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get labs in Florida."""

    raise NotImplementedError


def get_retailers_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get retailers in Florida."""

    # Get the licenses URL.
    url = FLORIDA['licenses_url']
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # TODO: Get the retailers from each page!
    
    raise NotImplementedError


def get_licenses_fl(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get licenses in Florida."""

    # Get the licenses URL.
    url = FLORIDA['licenses_url']
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # Get the table data.
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    cells = table.text.split('\n')
    cells = [x for x in cells if x]
    columns = FLORIDA['columns']
    headers = cells[:len(columns)]
    rows = cells[len(columns):]
    rows = [rows[i:i+len(columns)] for i in range(0, len(rows), len(columns))]

    # Convert the list of rows into a DataFrame.
    df = pd.DataFrame(rows)
    df.columns = list(columns.values())
    print(df)

    # Get business websites and license URLs.
    links = table.find_all('a')
    hrefs = [x['href'] for x in links]
    hrefs = [x for x in hrefs if 'http' in x]
    pairs = [hrefs[i:i+2] for i in range(0, len(hrefs), 2)]
    df['business_website'] = [x[0] for x in pairs]
    df['license_url'] = [x[1] for x in pairs]


    # TODO: Get issue date from the license PDF.
    # (Will need to apply OCR to get a PDF first.)

    # TODO: Get the business legal name from the license PDF.

    # TODO: Augment license data.


    return df


# === Test ===
if __name__ == '__main__':
    print('Getting licenses...')
