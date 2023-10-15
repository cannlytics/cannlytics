"""
Upload Cannabis Analytes
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/10/2023
Updated: 10/10/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Data Source:

    - [Cannabis Licenses](https://huggingface.co/datasets/cannlytics/cannabis_analytes)

Command-line Usage:

    python datasets/cannabis_analytes/upload_cannabis_analytes.py all

"""
# Standard imports:
import os

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values
import pandas as pd


def upload_cannabis_analytes(
        subset: str = 'all',
        col: str = 'public/data/analytes',
        repo: str = 'cannlytics/cannabis_analytes',
        doc_id_key: str = 'key',
        verbose: bool = True,
    ):
    """Upload cannabis analytes data to Firestore.
    Args:
        subset (str): The subset of the Hugging Face data, `all` by default.
        col (str): The Firestore base document where the data should be saved.
        repo (str): The Hugging Face dataset repository.
        doc_id_key (str): The field of the document to use as a document ID.
        verbose (bool): Whether to print out progress.
    """

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Get the data from local storage.
    try:
        if subset == 'all':
            subset = 'analytes'
        data = pd.read_json(f'data/{subset}.json')
        if verbose:
            print('Loaded %i documents from local storage.' % len(data))

    # Get the data from Hugging Face.
    except:
        dataset = load_dataset(repo, subset)
        data = dataset['data'].to_pandas()
        if verbose:
            print('Loaded %i documents from Hugging Face.' % len(data))

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in data.iterrows():
        doc_id = row[doc_id_key]
        obs = row.to_dict()
        refs.append(f'{col}/{doc_id}')
        docs.append(obs)

    # Upload the data to Firestore.
    firebase.update_documents(refs, docs, database=db)
    if verbose:
        print('Uploaded %i documents to Firestore.' % len(docs))
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
    analytes = upload_cannabis_analytes(subset=subset, verbose=True)
    print('Uploaded %i analyte data to Firestore.' % len(analytes))
