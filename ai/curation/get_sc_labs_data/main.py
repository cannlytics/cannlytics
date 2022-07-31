"""
Get SC Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/8/2022
Updated: 7/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Periodically collect SC Labs' publicly published lab results.

Data Sources:
    
    - SC Labs Test Results
    URL: <https://client.sclabs.com/>

"""
# Internal imports.
import base64
from time import sleep

# External imports.
from firebase_admin import firestore, initialize_app

# Internal imports.
from cannlytics.firebase import get_document, update_documents
from cannlytics.data.coas.sclabs import (
    get_sc_labs_sample_details,
    get_sc_labs_test_results,
)
from sc_labs_producer_ids import PRODUCER_IDS


def get_sc_labs_data(event, context):
    """Archive SC Labs data on a periodic basis.
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
    
    # Future work: Discover any new SC Labs public clients.

    # Get the most recent samples for each client.
    data = []
    for producer_id in PRODUCER_IDS:
        try:
            results = get_sc_labs_test_results(
                producer_id,
                limit=25,
                page_limit=1,
            )
            if results:
                data += results
            sleep(0.2)
        except:
            print('Error getting results for producer:', producer_id)
    
    # See if the samples already exist, if not, then get their details.
    refs, updates = [], []
    for obs in data:
        sample_id = obs['sample_id']
        ref = f'public/data/lab_results/{sample_id}'
        doc = get_document(ref)
        if not doc:
            refs.append(ref)
            url = obs['lab_results_url']
            details = get_sc_labs_sample_details(url)
            updates.append({**obs, **details})

    # Save any new lab results.
    if updates:
        update_documents(refs, updates, database=database)
        print('Added %i lab results' % len(refs))


if __name__ == '__main__':

    # === Test ===

    # [ ] TEST: Mock the Google Cloud Function scheduled routine.
    event = {'data': base64.b64encode('success'.encode())}
    get_sc_labs_data(event, context={})
