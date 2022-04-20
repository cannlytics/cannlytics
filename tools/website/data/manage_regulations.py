"""
Manage Regulations | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/26/2021
Updated: 1/9/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_regulations.py get_regulation_data
    ```

    Upload data.

    ```
    python tools/data/manage_regulations.py upload_regulation_data
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
FILENAME = 'regulations.json'
DOC = 'public/data'
REF = f'{DOC}/regulations'
ID = 'state'


def get_regulation_data():
    """Get regulation data from Firestore."""
    try:
        return get_data(REF, datafile=f'.datasets/{FILENAME}')
    except FileNotFoundError:
        return get_data(REF, datafile=f'../../.datasets/{FILENAME}')


def upload_regulation_data():
    """Upload regulation data from local `.datasets`."""
    try:
        upload_data(f'.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)
    except FileNotFoundError:
        upload_data(f'../../.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)


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
