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
import json
import math
import numpy as np
import os
from typing import List

# External imports:
from cannlytics import firebase
from datasets import load_dataset
from dotenv import dotenv_values
import pandas as pd


def replace_nan_with_none(data):
    """Replace NaN values with None values in a dictionary."""
    for dict_item in data:
        for key, value in dict_item.items():
            if isinstance(value, float) and math.isnan(value):
                dict_item[key] = None
    return data


def aggregate_lab_results(metadata, sheet_name='Details'):
    """Aggregate all lab results into a single dataset."""

    # Find datafiles.
    with open(metadata, 'r') as f:
        datafiles = json.load(f)

    # Read all datafiles, except the aggregate.
    # FIXME: Standardize all lab result files in their algorithms!
    results = []
    for name, datafile in datafiles.items():
        if name == 'all':
            continue

        # Read a datafile.
        try:
            file_path = os.path.join(f'./data/{name}/{name}-lab-results-latest.xlsx')
            results.append(pd.read_excel(file_path, sheet_name=sheet_name))
        except:
            try:
                results.append(pd.read_excel(file_path))
            except:
                print('ERROR READING:', name)

    # Aggregate all lab results.
    df = pd.concat(results, ignore_index=True)
    df = df.drop_duplicates()
    # df.dropna(subset=['download_url'], inplace=True)

    # Add keywords.
    keywords = df['product_name'].apply(lambda x: str(x).lower().split())
    df = df.assign(keywords=keywords)

    # Replace NaN with None
    df = df.replace(np.nan, None)

    print('AGGREGATED %i LAB RESULTS' % len(df))

    # Save the aggregated lab results.
    date = datetime.now().strftime('%Y-%m-%d')
    df.to_excel(f'./data/all/all-lab-results-{date}.xlsx', sheet_name='Data')
    df.to_excel('./data/all/all-lab-results-latest.xlsx', sheet_name='Data')

    # Return the data.
    return df


aggregate_lab_results('cannabis_results.json')


def upload_results(
        subset: str = 'all',
        col: str = 'data/lab_results',
        repo: str = 'cannlytics/cannabis_tests',
        verbose: bool = True,
    ):
    """Upload archived lab results to Firestore."""

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Read datasets.
    with open('./cannabis_tests/cannabis_results.json', 'r') as f:
        datafiles = json.load(f)

    # Read all lab results.
    results = []
    for dataset in datafiles:
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

    # Add keywords.
    data['keywords'] = data['product_name'].apply(lambda x: str(x).lower().split())

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in data[1000:].iterrows():

        # Handle NaN values.
        doc = row.to_dict()
        doc['updated_at'] = datetime.now().isoformat()
        doc = replace_nan_with_none(doc)

        # Format the document and collection IDs
        doc_id = str(doc['lab_id'])
        collection_id = doc['lab_state'].lower()

        # Create an entry for each state.
        refs.append(f'{col}/{collection_id}/{doc_id}')
        docs.append(doc)

        # Create a second entry for aggregate queries.
        refs.append(f'{col}/all/{doc_id}')
        docs.append(doc)

    # Upload the data to Firestore.
    firebase.update_documents(refs, docs, database=db)
    return docs


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = 'D://data'
    
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
