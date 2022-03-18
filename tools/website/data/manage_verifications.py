"""
Manage Verifications | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/15/2021
Updated: 12/26/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_verifications.py get_verification_data
    ```

    Upload data.

    ```
    python tools/data/manage_verifications.py upload_verification_data
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


def get_verification_data():
    """Get verification data from Firestore."""
    ref = 'public/verifications/verification_data'
    try:
        return get_data(REF, datafile='.datasets/verifications.json')
    except FileNotFoundError:
        return get_data(REF, datafile='../../.datasets/verifications.json')


def upload_verification_data():
    """Upload verification data from local `.datasets`."""
    ref = 'public/verifications/verification_data'
    stats_doc = 'public/verifications'
    try:
        upload_data('.datasets/verifications.json', ref, stats_doc=stats_doc)
    except FileNotFoundError:
        upload_data('../../.datasets/verifications.json', ref, stats_doc=stats_doc)


if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
