"""
Manage Job Data | Cannlytics Website
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/28/2023
Updated: 5/28/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_jobs.py get_job_data
    ```

    Upload data.

    ```
    python tools/data/manage_jobs.py upload_job_data
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
FILENAME = 'jobs.json'
DOC = 'public/data'
REF = f'{DOC}/jobs'
ID = 'id'


def get_job_data():
    """Get job data from Firestore."""
    try:
        return get_data(REF, datafile=f'.datasets/{FILENAME}')
    except FileNotFoundError:
        return get_data(REF, datafile=f'../../.datasets/website/{FILENAME}')


def upload_job_data():
    """Upload job data from local `.datasets`."""
    try:
        upload_data(f'.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)
    except FileNotFoundError:
        upload_data(f'../../.datasets/website/{FILENAME}', REF, id_key=ID, stats_doc=DOC)


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
    try:
        globals()[sys.argv[1]]()
    except:

        # Upload job data.
        upload_job_data()

