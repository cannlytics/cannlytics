"""
Upload Cannabis License Data
Copyright (c) 2023 Cannlytics
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/29/2022
Updated: 4/2/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Cannabis Licenses
    URL: <https://huggingface.co/datasets/cannlytics/cannabis_licenses>

Command-line Usage:

    python tools/upload_licenses.py all

"""
# Standard imports:
import os
import sys

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values
import uuid


# Define the dataset.
DATASET = 'cannlytics/cannabis_licenses'


def upload_cannabis_licenses(
        subset: str = 'all',
        collection: str = 'licenses',
        doc_id: str = 'hex'
    ):
    """Get cannabis license data from Hugging Face and upload the data
    to Firestore.
    Args:
        subset (str): The subset of the Hugging Face data, `all` by default.
        collection (str): The Firestore collection where the data should be saved.
        doc_id (str): How to create a document ID, a `hex`, `uuid`, or
            the field of the document to use.
    """
    
    # Get the data from Hugging Face.
    dataset = load_dataset(DATASET, subset)
    data = dataset['data'].to_pandas()

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in data.iterrows():
        doc = row.to_dict()
        if doc_id == 'hex':
            _id = uuid.uuid4().hex
        elif doc_id == 'uuid':
            _id = str(uuid.uuid4())
        else:
            _id = doc[doc_id]
        ref = f'{collection}/{_id}'
        refs.append(ref)
        docs.append(doc)
    
    # Upload the data to Firestore.
    db = firebase.initialize_firebase()
    firebase.update_documents(refs, docs, database=db)


# === Test ===
if __name__ == '__main__':

    # Set Firebase credentials.
    try:
        config = dotenv_values('../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('./.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    # Get any subset specified from the command line.
    try:
        subset = sys.argv[1]
    except KeyError:
        subset = 'all'

    # Upload Firestore with cannabis license data.
    upload_cannabis_licenses(subset=subset)
    print('Uploaded license data to Firestore.')
