"""
Manage Partners | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 9/10/2021
Updated: 12/27/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_partners.py get_partner_data
    ```

    Upload data.

    ```
    python tools/data/manage_partners.py upload_partner_data
    ```
"""
# Standard imports
import os
import sys

# External imports
from dotenv import dotenv_values

# Internal imports
from data_management import get_data, upload_data

# Set credentials.
try:
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    config = dotenv_values('.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


def get_partner_data():
    """Get partner data from Firestore."""
    ref = 'public/partners/partner_data'
    try:
        return get_data(REF, datafile='.datasets/partners.json')
    except FileNotFoundError:
        return get_data(REF, datafile='../../.datasets/partners.json')


def upload_partner_data():
    """Upload partner data from local `.datasets`."""
    ref = 'public/partners/partner_data'
    stats_doc = 'public/partners'
    try:
        upload_data('.datasets/partners.json', ref, stats_doc=stats_doc)
    except FileNotFoundError:
        upload_data('../../.datasets/partners.json', ref, stats_doc=stats_doc)


if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
