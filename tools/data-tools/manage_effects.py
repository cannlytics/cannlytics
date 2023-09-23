"""
Manage Effects and Aromas | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/3/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_effects.py get_effects_data
    ```

    Upload data.

    ```
    python tools/data/manage_effects.py upload_effects_data
    ```
"""
# Standard imports.
import json
import os
import sys

# External imports.
from dotenv import dotenv_values
from cannlytics.firebase.firebase import (
    get_document,
    initialize_firebase,
    update_document,
)

# The effects and aromas document.
REF = 'public/data/variables/effects_and_aromas'


def get_effects_data(ref=REF):
    """Get effects and aromas data from Firestore."""
    database = initialize_firebase()
    data = get_document(ref, database=database)
    return data


def upload_effects_data(data_dir='.datasets/website/models/', ref=REF):
    """Upload effects and aromas data from local `.datasets`."""
    database = initialize_firebase()
    with open(f'{data_dir}/aromas.json') as datafile:
        aromas = json.load(datafile)
    with open(f'{data_dir}/effects.json') as datafile:
        effects = json.load(datafile)
    with open(f'{data_dir}/effects_models.json') as datafile:
        variables = json.load(datafile)
    aromas = sorted(aromas, key=lambda d: d['name'])
    effects = sorted(effects, key=lambda d: d['name'])
    entry = {
        'aromas': {x['key']: x for x in aromas},
        'effects': {x['key']: x for x in effects},
        'variables': variables,
    }
    update_document(ref, entry, database=database)


# === Test ===
if __name__ == '__main__':

    # Set credentials.
    try:
        config = dotenv_values('../../../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
        data_dir = '../../../.datasets/website/models/'
    except KeyError:
        config = dotenv_values('.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
        data_dir = '.datasets/website/models/'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    # Call function from the command line.
    try:
        globals()[sys.argv[1]]()
    except:

        # Upload effects data.
        upload_effects_data(data_dir)

        # Get effects data.
        outcomes = get_effects_data()
