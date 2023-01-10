"""
Manage Lab Data | Cannlytics Website
Copyright (c) 2022-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/9/2022
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_labs.py get_lab_data
    ```

    Upload data.

    ```
    python tools/data/manage_labs.py upload_lab_data
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
FILENAME = 'labs.json'
DOC = 'public/data'
REF = f'{DOC}/labs'
ID = 'license'


def get_lab_data():
    """Get lab data from Firestore."""
    try:
        return get_data(REF, datafile=f'.datasets/{FILENAME}')
    except FileNotFoundError:
        return get_data(REF, datafile=f'../../.datasets/{FILENAME}')


def upload_lab_data():
    """Upload lab data from local `.datasets`."""
    try:
        upload_data(f'.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)
    except FileNotFoundError:
        upload_data(f'../../.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)


# === Test ===
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
