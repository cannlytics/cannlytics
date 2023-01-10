"""
Manage Datasets | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/26/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_datasets.py get_dataset_data
    ```

    Upload data.

    ```
    python tools/data/manage_datasets.py upload_dataset_data
    ```
"""
# Standard imports
from datetime import datetime
import json
import os
import sys
from typing import Optional

# External imports
from dotenv import dotenv_values

# Internal imports
from data_management import get_data, upload_data
sys.path.append('../../')
sys.path.append('./')
from cannlytics.firebase import ( # pylint: disable=import-error, wrong-import-position
    get_file_url,
    update_document,
    upload_file,
)

# Define references.
DATAFILES = 'datafiles.json'
FILENAME = 'datasets.json'
DOC = 'public/data'
REF = f'{DOC}/datasets'
ID = 'id'


def get_dataset_data():
    """Get dataset data from Firestore."""
    try:
        return get_data(REF, datafile=f'.datasets/{FILENAME}')
    except FileNotFoundError:
        return get_data(REF, datafile=f'../../.datasets/{FILENAME}')


def upload_dataset_data():
    """Upload dataset data from local `.datasets`."""
    try:
        upload_data(f'.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)
        # upload_dataset_files('.datasets')
    except FileNotFoundError:
        upload_data(f'../../.datasets/{FILENAME}', REF, id_key=ID, stats_doc=DOC)
        # upload_dataset_files('../../.datasets')


def upload_dataset_files(root: Optional[str] = '.datasets'):
    """Upload files accompanying each dataset.
    Args:
        root (str): The root folder of the datasets JSON (optional).
    """
    bucket = os.environ['FIREBASE_STORAGE_BUCKET']
    with open(f'{root}/{FILENAME}') as datasets:
        data = json.load(datasets)
    with open(f'{root}/{DATAFILES}') as datafiles:
        files = json.load(datafiles)
    for item in data:
        datafile = files[item['id']]
        ref = datafile['ref']
        file_name = datafile['file_name']
        upload_file(ref, file_name, bucket_name=bucket)
        file_url = get_file_url(ref, bucket_name=bucket)
        datafile['url'] = file_url
        datafile['updated_at'] = datetime.now().isoformat()
        update_document(datafile['doc'], datafile)


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
    os.environ['FIREBASE_STORAGE_BUCKET'] = config['FIREBASE_STORAGE_BUCKET']

    # Call the function from the command line.
    globals()[sys.argv[1]]()
