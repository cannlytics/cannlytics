"""
Get MCR Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 7/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Periodically collect MCR Labs' publicly published lab results.

Data Points:

        ✓ analyses
        ✓ {analysis}_method
        ✓ date_tested
        ✓ image
        ✓ lab
        ✓ lab_website
        ✓ lab_results_url
        ✓ product_name
        ✓ product_type
        ✓ producer
        ✓ results
            - analysis
            ✓ key
            ✓ name
            ✓ units
            ✓ value
        ✓ sample_id (generated)
        ✓ total_cannabinoids
        ✓ total_terpenes

Data Sources:
    
    - MCR Labs Test Results
    URL: <https://reports.mcrlabs.com>

Future development:

    - Implement the function to get all of a given client's lab results.
    - Optional: Create necessary data dirs automatically.
    - Optional: Function to download any pre-existing results.

"""
# Internal imports.
import base64

# External imports.
from firebase_admin import firestore, initialize_app

# Internal imports.
from cannlytics.firebase import get_document, update_documents
from cannlytics.data.coas.mcrlabs import get_mcr_labs_test_results


def get_mcr_labs_data(event, context):
    """Archive MCR Labs data on a periodic basis.
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

    # Get the most recent lab results.
    data = get_mcr_labs_test_results(ending_page=1, verbose=False)

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
    get_mcr_labs_data(event, context={})
