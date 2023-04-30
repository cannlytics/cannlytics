"""
Cannabis Licenses | Get New York Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 4/30/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect New York cannabis license data.

Data Source:

    - New York Medical Dispensaries
    URL: <https://cannabis.ny.gov/dispensing-facilities>

"""
# Standard imports:
from datetime import datetime
import os
import re
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
import pdfplumber
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import numpy as np
import pandas as pd
import requests
import zipcodes


# Specify where your data lives.
DATA_DIR = '../data/ny'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'NY'
NEW_YORK = {
    'licensing_authority_id': 'OCM',
    'licensing_authority': 'New York State Office of Cannabis Management',
    # 'medical_url': 'https://cannabis.ny.gov/dispensing-facilities',
    # 'retailers_url': 'https://cannabis.ny.gov/conditional-adult-use-retail-dispensary',
    # 'active_retailers_url': 'https://cannabis.ny.gov/dispensary-location-verification',
    # 'processors_url': 'https://cannabis.ny.gov/adult-use-conditional-processor',
    # 'cultivators_url': '',
    # 'labs_url': 'https://cannabis.ny.gov/cannabis-laboratories',
    'cultivators': {
        'source': 'https://cannabis.ny.gov/adult-use-conditional-cultivator',
        'url': 'https://cannabis.ny.gov/list-aucc-licenses',
    },
    'retailers': {
        'source': 'https://cannabis.ny.gov/conditional-adult-use-retail-dispensary',
        'url': 'https://cannabis.ny.gov/caurd-licenses',
    },
    'processors': {
        'source': 'https://cannabis.ny.gov/adult-use-conditional-processor',
        'url': 'https://cannabis.ny.gov/list-aucp-licenses',
    },
    'labs': {
        'source': 'https://cannabis.ny.gov/cannabis-laboratories',
        'url': '',
    },
}


def get_retailers_ny(data_dir):
    """Get New York cannabis retailers."""

    # Create a dataset directory.
    dataset_dir = os.path.join(data_dir, '.datasets')
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    # Get the licenses website content.
    # url = NEW_YORK['retailers_url']
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')

    # Download the licenses document.
    url = NEW_YORK['retailers']['url']
    response = requests.get(url)
    pdf_file = os.path.join(dataset_dir, 'ny-retailers.pdf')
    with open(pdf_file, 'wb') as f:
        f.write(response.content)

    # Read the PDF.
    doc = pdfplumber.open(pdf_file)
    data = []
    for page in doc.pages:
        table = page.extract_table()
        rows = [x for x in table if x[0] and x[0] != 'License Number' and x[0] != 'Application ID']
        data.extend(rows)

    # Close the PDF.
    doc.close()

    # Create a dataframe.
    columns = [
        'License Number',
        'business_legal_name',
        'county',
        'business_email',
        'business_phone',
    ]
    licenses = pd.DataFrame(data, columns=columns)



def get_processors_ny():
    """Get New York cannabis processors."""
    raise NotImplementedError


def get_cultivators_ny():
    """Get New York cannabis cultivators."""
    raise NotImplementedError


def get_labs_ny():
    """Get New York cannabis labs."""
    raise NotImplementedError


def get_medical_ny():
    """Get New York medical cannabis dispensaries."""
    raise NotImplementedError


def get_licenses_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get New York cannabis license data."""
    

    # TODO: Get the various license files / HTML.

    # TODO: Parse the data.

    # TODO: Standardize the data.

    # Return the licenses.
    raise NotImplementedError


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
    data = get_licenses_ny(data_dir, env_file=env_file)
