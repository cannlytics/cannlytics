"""
Upload Cannabis License Data
Copyright (c) 2023 Cannlytics
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/29/2022
Updated: 5/15/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Cannabis Licenses
    URL: <https://huggingface.co/datasets/cannlytics/cannabis_licenses>

Command-line Usage:

    python data/archive/upload_licenses.py all

"""
# Standard imports:
import math
import os
from typing import List

import pandas as pd

# External imports:
from cannlytics.data import create_hash
from cannlytics import firebase
from cannlytics.utils.constants import states
from datasets import load_dataset
from dotenv import dotenv_values


def replace_nan_with_none(data):
    """Replace NaN values with None values in a dictionary."""
    for dict_item in data:
        for key, value in dict_item.items():
            if isinstance(value, float) and math.isnan(value):
                dict_item[key] = None
    return data


def upload_cannabis_licenses_datafiles(
        bucket_name,
        storage_ref: str = 'data/licenses',
        verbose: bool = True,
    ) -> List[str]:
    """Upload cannabis license datafiles to Firebase Storage.
    Args:
        storage_ref (str): The Firebase Storage reference for the datafiles.
    """

    # Initialize Firebase.
    firebase.initialize_firebase()

    # Get datafiles.
    datafiles = []
    for root, _, files in os.walk('./cannabis_licenses/'):
        for file in files:
            if file.endswith('latest.csv'):
                datafiles.append(os.path.join(root, file))

    # Format the references.
    refs = [storage_ref + x.split('./cannabis_licenses/data')[-1] for x in datafiles]
    refs = [x.replace('\\', '/') for x in refs]
    
    # Upload datafiles to Firebase Storage.
    for i, datafile in enumerate(datafiles):
        ref = refs[i]
        firebase.upload_file(ref, datafile, bucket_name=bucket_name)
        if verbose:
            print(f'Uploaded latest: {ref}')

    # Return the references.
    return refs


def upload_cannabis_licenses(
        subset: str = 'all',
        col: str = 'data/licenses',
        repo: str = 'cannlytics/cannabis_licenses',
        verbose: bool = True,
    ):
    """Get cannabis license data from Hugging Face and upload the data
    to Firestore.
    Args:
        subset (str): The subset of the Hugging Face data, `all` by default.
        col (str): The Firestore base document where the data should be saved.
        repo (str): The Hugging Face dataset repository.
        doc_id (str): How to create a document ID, a `hex`, `uuid`, or
            the field of the document to use.
        verbose (bool): Whether to print out progress.
    """

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Get the data from local storage.
    try:
        data = pd.read_csv('./cannabis_licenses/data/all/licenses-all-latest.csv')

    # Otherwise get the data from Hugging Face.
    except:
        dataset = load_dataset(repo, subset)
        data = dataset['data'].to_pandas()

    # Compile the references and documents.
    refs, docs = [], []
    data['id'] = data['license_number'].fillna(data['id']).apply(str)
    data = data.loc[data['id'].notnull()]
    state_names = [x.lower() for x in states.keys()]
    for index, row in data.iterrows():

        # Format the document and collection IDs
        doc_id = row['id']
        collection_id = row['premise_state'].lower()

        # FIXME: Not all states are parsed correctly.
        if collection_id not in state_names:
            print('Invalid state:', index, row.to_dict())
            continue

        # Handle NaN values.
        obs = replace_nan_with_none(row.to_dict())

        # Create an entry for each state.
        refs.append(f'{col}/{collection_id}/{doc_id}')
        docs.append(obs)

        # Create a second entry for aggregate queries.
        uid = create_hash(doc_id, collection_id)
        refs.append(f'{col}/all/{uid}')
        docs.append(obs)

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
    try:
        all_licenses = upload_cannabis_licenses(subset=subset)
        print('Uploaded %i license data to Firestore.' % len(all_licenses))
    except:
        print('Failed to upload license data to Firestore.')

    # Upload datafiles to Firebase Storage.
    # try:
    #     bucket_name = config['FIREBASE_STORAGE_BUCKET']
    #     upload_cannabis_licenses_datafiles(bucket_name)
    #     print('Uploaded license datafiles to Firebase Storage.')
    # except:
    #     print('Failed to upload datafiles to Firebase Storage.')
