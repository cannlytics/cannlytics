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
import os
from typing import List

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values


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
        collection: str = 'data/licenses',
        repo: str = 'cannlytics/cannabis_licenses',
        verbose: bool = True,
    ):
    """Get cannabis license data from Hugging Face and upload the data
    to Firestore.
    Args:
        subset (str): The subset of the Hugging Face data, `all` by default.
        collection (str): The Firestore collection where the data should be saved.
        repo (str): The Hugging Face dataset repository.
        doc_id (str): How to create a document ID, a `hex`, `uuid`, or
            the field of the document to use.
        verbose (bool): Whether to print out progress.
    """

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Get the data from Hugging Face.
    dataset = load_dataset(repo, subset)
    data = dataset['data'].to_pandas()
    if verbose:
        print(f'Uploading {len(data)} licenses ({subset}).')

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in data.iterrows():
        doc = row.to_dict()
        _id = str(doc['id'])
        # FIXME: Not all stats are parsed correctly.
        state = doc['premise_state'].lower()
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
    # try:
    upload_cannabis_licenses(subset=subset)
    print('Uploaded license data to Firestore.')
    # except:
    #     print('Failed to upload license data to Firestore.')

    # Upload datafiles to Firebase Storage.
    # try:
    #     bucket_name = config['FIREBASE_STORAGE_BUCKET']
    #     upload_cannabis_licenses_datafiles(bucket_name)
    #     print('Uploaded license datafiles to Firebase Storage.')
    # except:
    #     print('Failed to upload datafiles to Firebase Storage.')
