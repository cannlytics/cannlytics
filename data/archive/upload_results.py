"""
Upload Cannabis Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/22/2023
Updated: 5/22/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python data/archive/upload_results.py all

"""
# Standard imports:
import os
from typing import List

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values


DATAFILES = [

]


def upload_results(
        subset: str = 'all',
        collection: str = 'data/lab_results',
        repo: str = 'cannlytics/cannabis_tests',
        verbose: bool = True,
    ):
    """Upload archived lab results to Firestore."""

    # TODO: Read in all datafiles.


    # TODO: Upload to Firestore by state.


    raise NotImplementedError


# === Test ===
if __name__ == '__main__':
    

    # Set Firebase credentials.
    try:
        config = dotenv_values('../../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('./.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    # Get any subset specified from the command line.
    import sys
    try:
        subset = sys.argv[1]
        if subset.startswith('--ip'):
            subset = 'all'
    except KeyError:
        subset = 'all'
    
    # Upload Firestore with cannabis license data.
    # try:
    upload_results(subset=subset)
    print('Uploaded lab results data to Firestore.')
