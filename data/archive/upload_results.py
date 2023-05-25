"""
Upload Cannabis Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/22/2023
Updated: 5/23/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python data/archive/upload_results.py all

"""
# Standard imports:
from datetime import datetime
import os
from typing import List

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D://data'

# Lab result data files.
DATASETS = [
    {
        "title": "California Lab Results",
        "image_url": "",
        "description": "",
        "tier": "Premium",
        "path": "/results/ca",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/ca/.csv",
        "url": "",
    },
    {
        "title": "Connecticut Lab Results",
        "image_url": "",
        "description": "",
        "tier": "Premium",
        "path": "/results/ct",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/ct/.csv",
        "url": "",
    },
    {
        "title": "Florida Lab Results",
        "data_dir": "florida\lab_results\.datasets",
        "image_url": "",
        "description": "",
        "tier": "Premium",
        "path": "/results/fl",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/fl/fl-lab-results-latest.csv",
        "url": "",
    },
    {
        "title": "Massachusetts Lab Results",
        "image_url": "",
        "description": "",
        "tier": "Premium",
        "path": "/results/ma",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/ma/.csv",
        "url": "",
    },
    {
        "title": "Michigan Lab Results",
        "image_url": "",
        "description": "",
        "tier": "Premium",
        "path": "/results/mi",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/mi/.csv",
        "url": "",
    },
    {
        "title": "Washington Lab Results",
        "image_url": "",
        "description": "Curated cannabis traceability lab tests from Washington State from 2021 to 2023.",
        "tier": "Premium",
        "path": "/results/wa",
        "observations": 59501,
        "fields": 53,
        "type": "results",
        "file_ref": "data/lab_results/washington/ccrs-inventory-lab-results-2023-03-07.xlsx",
        "url": "",
    },
]

# Lab result constants.
CONSTANTS = {
    'lims': 'Kaycha Labs',
    'lab': 'Kaycha Labs',
    'lab_image_url': 'https://www.kaychalabs.com/wp-content/uploads/2020/06/newlogo-2.png',
    'lab_address': '4101 SW 47th Ave, Suite 105, Davie, FL 33314',
    'lab_street': '4101 SW 47th Ave, Suite 105',
    'lab_city': 'Davie',
    'lab_county': 'Broward',
    'lab_state': 'FL',
    'lab_zipcode': '33314',
    'lab_phone': '833-465-8378',
    'lab_email': 'info@kaychalabs.com',
    'lab_website': 'https://www.kaychalabs.com/',
    'lab_latitude': 26.071350,
    'lab_longitude': -80.210750,
    'licensing_authority_id': 'OMMU',
    'licensing_authority': 'Florida Office of Medical Marijuana Use',
}


def upload_results(
        subset: str = 'all',
        collection: str = 'data/lab_results',
        repo: str = 'cannlytics/cannabis_tests',
        verbose: bool = True,
    ):
    """Upload archived lab results to Firestore."""

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Read all lab results.
    # TODO: Generalize to all states / labs.
    results = []
    for dataset in DATASETS:
        folder_path = os.path.join(DATA_DIR, dataset.get('data_dir', './datasets'))
        if not os.path.exists(folder_path):
            continue
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.xlsx'):
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_excel(file_path)
                results.append(df)

    # Aggregate all lab results.
    data = pd.concat(results, ignore_index=True)
    data = data.drop_duplicates()
    data.dropna(subset=['download_url'], inplace=True)
    data.drop(columns=[0], inplace=True)
    if verbose:
        print('Aggregated %i lab results.' % len(data))

    # Standardize the data.
    # FIXME: Generalize to all states / labs.
    for constant, value in CONSTANTS.items():
        data[constant] = value

    # FIXME: Augment license data.
    # This is a hot-fix.
    from cannabis_licenses.algorithms.get_licenses_fl import get_licenses_fl
    licenses = get_licenses_fl()
    licenses['license_type'] = 'Medical - Retailer'
    data = pd.merge(
        data,
        licenses,
        suffixes=['', '_copy'],
        left_on='producer_license_number',
        right_on='license_number',
    )
    data = data.filter(regex='^(?!.*_copy$)')

    # Add keywords.
    data['keywords'] = data['product_name'].apply(lambda x: str(x).lower().split())

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in data[1000:].iterrows():
        doc = row.to_dict()
        _id = str(doc['lab_id'])
        state = doc['lab_state'].lower()
        doc['updated_at'] = datetime.now().isoformat()
        ref = f'{collection}/{state}/{_id}'
        refs.append(ref)
        docs.append(doc)

    # Upload the data to Firestore.
    firebase.update_documents(refs, docs, database=db)
    return docs


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
    all_results = upload_results(subset=subset)
    print('Uploaded lab results data to Firestore.')
