"""
Get Raw Garden Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/23/2022
Updated: 9/4/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Periodically collect Raw Garden's publicly published lab results.

Data Sources:
    
    - Raw Garden Lab Results
    URL: <https://rawgarden.farm/lab-results/>

"""
# Standard imports.
import base64
from datetime import datetime
import os
from time import sleep

# External imports.
from firebase_admin import firestore, initialize_app
import pandas as pd
import requests

# Internal imports.
from cannlytics.firebase import get_document, update_documents
from cannlytics.data.coas import CoADoc
from cannlytics.utils.constants import DEFAULT_HEADERS


def get_rawgarden_data(event, context):
    """Archive Raw Garden data on a periodic basis.
    Triggered from a message on a Cloud Pub/Sub topic.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """

    # Check that the PubSub message is valid.
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'success':
        return

    # Initialize Firebase.
    try:
        initialize_app()
    except ValueError:
        pass
    database = firestore.client()

    # TODO: Create temporary directories.
    # DATA_DIR = '../../../.datasets'
    # COA_DATA_DIR = f'{DATA_DIR}/lab_results/raw_garden'
    # COA_PDF_DIR = f'{COA_DATA_DIR}/pdfs'
    # if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    # if not os.path.exists(COA_DATA_DIR): os.makedirs(COA_DATA_DIR)
    # if not os.path.exists(COA_PDF_DIR): os.makedirs(COA_PDF_DIR)

    # TODO: Get the most recent lab results.
    data = None
    raise NotImplementedError

    # Read lab results to see if any are missing.
    refs, updates = [], []
    for obs in data:
        sample_id = obs['sample_id']
        ref = f'public/data/lab_results/{sample_id}'
        doc = get_document(ref)
        if not doc:
            refs.append(ref)
            updates.append(obs)

    # Save any new lab results.
    if updates:
        update_documents(refs, updates, database=database)
        print('Added %i lab results' % len(refs))


if __name__ == '__main__':

    # === Test ===

    # [✓] TEST: Mock the Google Cloud Function scheduled routine.
    event = {'data': base64.b64encode('success'.encode())}
    get_rawgarden_data(event, context={})
