"""
Upload Cannlytics Data Archive
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/16/2023
Updated: 4/16/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python data/archive/upload_data.py

"""
# Standard imports:
import json
import os

# External imports:
from cannlytics import firebase
from dotenv import dotenv_values
import uuid

# Define datasets to upload.
DATASETS = [
    '.datasets/ai_models.json',
    '.datasets/datasets.json',
    '.datasets/datasources.json',
]

def upload_data_archive(
        col: str = 'data',
        doc_id: str = 'hex'
    ):
    """Upload datasets to Firestore.
    Args:
        col (str): The Firestore base collection where the data should be saved.
        doc_id (str): How to create a document ID, a `hex`, `uuid`, or
            the field of the document to use.
    """
    # Read the datasets metadata from their JSON files.
    metadata = []
    for dataset in DATASETS:
        with open(dataset, 'r') as file:
            metadata += json.load(file)

    # Compile the Firestore references and documents.
    refs, docs = [], []
    for doc in metadata:
        if doc_id == 'hex':
            _id = uuid.uuid4().hex
        elif doc_id == 'uuid':
            _id = str(uuid.uuid4())
        else:
            _id = doc[doc_id]
        doc_type = doc['type']
        ref = f'{col}/{doc_type}/{_id}'
        refs.append(ref)
        docs.append(doc)
    
    # Upload the data to Firestore.
    db = firebase.initialize_firebase()
    firebase.update_documents(refs, docs, database=db)


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

    # Upload datasets to Firestore.
    upload_data_archive(DATASETS)
    print('Uploaded data archive to Firestore.')
