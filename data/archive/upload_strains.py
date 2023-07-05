"""
Upload Cannabis Strains Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2023
Updated: 7/2/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python data/archive/upload_strains.py all

"""
# Standard imports:
from datetime import datetime
import glob
import os
from typing import List

# External imports:
from cannlytics import firebase
from cannlytics.data import create_hash
from datasets import load_dataset
from dotenv import dotenv_values
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D://data'

# Specify data files.
LAB_RESULT_DATASETS = [
    {
        "title": "California Lab Results",
        "state": "CA",
        "state_name": "California",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fcalifornia-flag.png?alt=media&token=f64aaaba-d9cf-4e6f-9f06-4d431cb01d31",
        "description": "",
        "tier": "Premium",
        "path": "/results/ca",
        "observations": 1202,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/ca/.csv",
        "url": "",
    },
    {
        "title": "Connecticut Lab Results",
        "state": "CT",
        "state_name": "Connecticut",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fconnecticut-flag.png?alt=media&token=bdac5bd6-4d1e-4652-aa39-55b247ed0a4b",
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
        "state": "FL",
        "state_name": "Florida",
        "data_dir": "florida\lab_results\.datasets",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fflorida-flag.png?alt=media&token=f7129c6b-a2cf-4e21-9c0d-a060eb5a372d",
        "description": "",
        "tier": "Premium",
        "path": "/results/fl",
        "observations": 16167,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/fl/fl-lab-results-latest.csv",
        "url": "",
    },
    {
        "title": "Massachusetts Lab Results",
        "state": "MA",
        "state_name": "Massachusetts",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fmassachusetts-flag.png?alt=media&token=d500905e-522a-4577-bc9d-0e6f5534831c",
        "description": "",
        "tier": "Premium",
        "path": "/results/ma",
        "observations": 0,
        "fields": 0,
        "type": "results",
        "file_ref": "data/lab_results/ma/.csv",
        "url": "",
    },
    # {
    #     "title": "Michigan Lab Results",
    #     "state": "MI",
    #     "state_name": "Michigan",
    #     "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fmichigan-flag.png?alt=media&token=f8884f41-47cc-4883-88dd-18442518608a",
    #     "description": "",
    #     "tier": "Premium",
    #     "path": "/results/mi",
    #     "observations": 0,
    #     "fields": 0,
    #     "type": "results",
    #     "file_ref": "data/lab_results/mi/.csv",
    #     "url": "",
    # },
    {
        "title": "Washington Lab Results",
        "state": "WA",
        "state_name": "Washington",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Femojies%2Fstate-flags%2Fwashington-flag.png?alt=media&token=0df433c2-e3b2-419f-b4ce-b999f961ad62",
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


#----------------------------------------------------------------------#
# Compile lab results to obtain strain data.
#----------------------------------------------------------------------#

def get_lab_result_datafiles(data_dir: str):
    """Get the most recent lab result datafiles for each state."""
    datafiles = []
    for dataset in LAB_RESULT_DATASETS:
        state_name = dataset['state_name'].lower()
        folder_path = os.path.join(data_dir, state_name, 'lab_results/*.xlsx')
        files = glob.glob(folder_path)
        if files:
            most_recent_file = max(files, key=lambda f: f[-14:-5])
            datafiles.append(most_recent_file)
            print('Most recent file:', most_recent_file)
        else:
            print('No .xlsx files found in the folder.')


def compile_strain_data(datafiles: list) -> pd.DataFrame:
    """Compile strain data from lab results."""

    # Read all lab results.
    results = []
    for datafile in datafiles:
        df = pd.read_excel(datafile)
        results.append(df)

    # Aggregate all lab results.
    results = pd.concat(results, ignore_index=True)

    # TODO: Standardize the data!

    # TODO: First, get all known strain names.

    # TODO: Second, get all products that contain those strains.

    # TODO: Third, calculate summary statistics for each strain.
    strain_data = pd.DataFrame()
    return strain_data


#----------------------------------------------------------------------#
# Begin to identify unique strain names.
#----------------------------------------------------------------------#

# TODO: Identify all unique known strains in the lab results.
# - Washington
# - California


#----------------------------------------------------------------------#
# Use NLP to help identify unique strain names.
#----------------------------------------------------------------------#

# TODO: Identify common unigrams, bigrams, and trigram from product names
# of lab results that do not have strain names.
# - Connecticut
# - Florida
# - Massachusetts
# - Michigan

# # Create natural language processing client.
# # Use `en_core_web_sm` for speed and `en_core_web_lg` or `en_core_web_trf`
# # for accuracy. For a blank model, use spacy.blank('en')
# # Compile all of the product names into a single corpus.
# # Handle strange characters, for example replace "_" with " ".
# # Convert the corpus to a SpaCy document.
# corpus = '. '.join([str(x) for x in strain_names])
# corpus = corpus.replace('_', ' ')
# nlp = spacy.load('en_core_web_lg')
# doc = nlp(corpus)

# # Identify unique unigrams, bi-grams, trigrams to use as strain names.
# unigrams = list(set([x.text for x in ngrams(doc, 1, min_freq=1)]))
# bigrams = list(set([x.text for x in ngrams(doc, 2, min_freq=1)]))
# trigrams = list(set([x.text for x in ngrams(doc, 3, min_freq=1)]))
# print('Unique unigrams:', len(unigrams))
# print('Unique bigrams:', len(bigrams))
# print('Unique trigrams:', len(trigrams))


#----------------------------------------------------------------------#
# Use AI to help identify unique strain names.
#----------------------------------------------------------------------#

# Chunk by chunk:

# TODO: Use OpenAI GPT-4 model to predict a dictionary of `other_names`
# for strains with similar spellings.

# Save the `other_names` dictionary to a JSON file.

# TODO: Use OpenAI GPT-4 model to remove strain names that do not appear
# to be strain names.

# Save the `removed_names` dictionary to a JSON file.



#----------------------------------------------------------------------#
# Aggregate strain data.
#----------------------------------------------------------------------#

# TODO: Get all results that contain strain names.
# - California
# - Washington

# TODO: Get all results with product names that contain those strains.
# - Connecticut
# - Florida
# - Massachusetts
# - Michigan

# TODO: From WA traceability data, estimate:
# - avg. yield per plant
# - avg. growing time
# - avg. price per gram


#----------------------------------------------------------------------#
# Calculate statistics for each strain.
#----------------------------------------------------------------------#

# DEV:
datafiles = get_lab_result_datafiles(DATA_DIR)
results = []
for datafile in datafiles:
    df = pd.read_excel(datafile)
    results.append(df)

# FIXME: Calculate statistics for each strain.
strain_data = results.groupby('strain_name').agg()
# ✓ strain_id
# - strain_name
# - other_names
# - description (optional)
# - first_observed_at
# - first_observed_county
# - first_observed_state
# - first_observed_zipcode
# - first_observed_producer_license_number
# - first_observed_retailer_license_number
# ✓ keywords
# - lineage
# - patent_number
# - mean_concentrations (thc, cbd, terpenes, etc.)
# - std_concentrations
# - mean_ratios
# - updated_at
# - number_of_lab_results
# - lab_result_ids
# - strain_image_url (create an image?)

# Create a strain ID for each strain.
strain_data['strain_id'] = strain_data['strain_name'].apply(
    create_hash,
    private_key='',
)

# Get strain keywords.
strain_data['keywords'] = strain_data['strain_name'].apply(
    lambda x: str(x).lower().split()
)


def upload_strains(collection: str = 'public/data/strains') -> list:
    """Upload strain data to Firestore."""

    # FIXME: Compile the strain data.
    # strain_data = compile_strain_data()
    strain_data = pd.DataFrame()

    # Initialize Firebase.
    db = firebase.initialize_firebase()

    # Compile the references and documents.
    refs, docs = [], []
    for _, row in strain_data.iterrows():
        doc = row.to_dict()
        _id = str(doc['strain_id'])
        doc['updated_at'] = datetime.now().isoformat()
        ref = f'{collection}/{_id}'
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
    all_results = upload_strains(subset=subset)
    print('Uploaded strains data to Firestore.')
