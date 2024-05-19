"""
Upload Cannabis Strains Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/26/2023
Updated: 9/22/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line Usage:

    python datasets/cannabis_strains/upload_strains.py all

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


#----------------------------------------------------------------------#
# Aggregate all strain data.
#----------------------------------------------------------------------#

# TODO: Get all results that contain strain names.
# - California
# - Washington

# TODO: Get all results with product names that contain those strains.
# - Connecticut
# - Florida
# - Massachusetts
# - Michigan

#----------------------------------------------------------------------#
# Use AI to identify all unique strain names.
#----------------------------------------------------------------------#

# Chunk by chunk:

# TODO: Use OpenAI GPT-4 model to predict a dictionary of `other_names`
# for strains with similar spellings.

# Save the `other_names` dictionary to a JSON file.

# TODO: Use OpenAI GPT-4 model to remove strain names that do not appear
# to be strain names.

# Save the `removed_names` dictionary to a JSON file.



#----------------------------------------------------------------------#
# Calculate statistics for each strain.
#----------------------------------------------------------------------#

# # DEV:
# datafiles = get_lab_result_datafiles(DATA_DIR)
# results = []
# for datafile in datafiles:
#     df = pd.read_excel(datafile)
#     results.append(df)

# FIXME: Calculate statistics for each strain.
# strain_data = results.groupby('strain_name').agg()
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

# # Create a strain ID for each strain.
# strain_data['strain_id'] = strain_data['strain_name'].apply(
#     create_hash,
#     private_key='',
# )

# # Get strain keywords.
# strain_data['keywords'] = strain_data['strain_name'].apply(
#     lambda x: str(x).lower().split()
# )


def upload_strains(
        strain_data: pd.DataFrame,
        collection: str = 'strains'
    ) -> list:
    """Upload strain data to Firestore."""
    db = firebase.initialize_firebase()
    refs, docs = [], []
    for _, row in strain_data.iterrows():
        doc = row.to_dict()
        _id = str(doc['strain_id'])
        doc['updated_at'] = datetime.now().isoformat()
        ref = f'{collection}/{_id}'
        refs.append(ref)
        docs.append(doc)
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

    # FIXME: Aggregate all strains.
    strain_data = pd.DataFrame()
    
    # Upload Firestore with cannabis license data.
    docs = upload_strains(subset=subset)
    print(f'Uploaded {len(docs)} strains to Firestore.')
