"""
Manage Sponsorships | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/26/2021
Updated: 1/3/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_sponsorships.py get_sponsorship_data
    ```

    Upload data.

    ```
    python tools/data/manage_sponsorships.py upload_sponsorship_data
    ```
"""
# Standard imports.
import os
import sys

# External imports.
from dotenv import dotenv_values

# Internal imports.
from data_management import get_data, upload_data

# Define references.
FILENAME = 'sponsorships.json'
DOC = 'public/subscriptions'
REF = f'{DOC}/sponsorships'


def get_sponsorship_data():
    """Get sponsorship data from Firestore."""
    try:
        return get_data(REF, datafile=f'.datasets/{FILENAME}')
    except FileNotFoundError:
        return get_data(REF, datafile=f'../../.datasets/{FILENAME}')


def upload_sponsorship_data():
    """Upload sponsorship data from local `.datasets`."""
    try:
        upload_data(f'.datasets/{FILENAME}', REF, stats_doc=DOC)
    except FileNotFoundError:
        upload_data(f'../../.datasets/{FILENAME}', REF, stats_doc=DOC)


if __name__ == '__main__':

    # Set credentials.
    try:
        config = dotenv_values('../../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    # Call function from the command line.
    globals()[sys.argv[1]]()
