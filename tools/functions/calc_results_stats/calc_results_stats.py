"""
Calculate Results Stats | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 6/28/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate statistics for all lab results and save them to a
    Firestore collection when a user's lab results changes.
    Firebase Functions for Firestore.

"""
# External imports:
from firebase_functions import firestore_fn, options
from firebase_admin import initialize_app


# Initialize Firebase.
initialize_app()

# Set the region.
options.set_global_options(region=options.SupportedRegion.US_CENTRAL1)


@firestore_fn.on_document_written(
    document='users/{uid}/lab_results/{lab_result_id}',
    timeout_sec=300,
    memory=options.MemoryOption.MB_512,
    # min_instances=5,
    # cpu=2
)
def calc_results_stats(
        event: firestore_fn.Event[firestore_fn.Change],
    ) -> None:
    """Calculate statistics for all lab results and save them to a
    Firestore collection when a user's lab results changes."""

    # Get an object with the current document values.
    # If the document does not exist, it was deleted.
    document = (event.data.after.to_dict()
                if event.data.after is not None else None)

    # Get an object with the previous document values.
    # If the document does not exist, it was newly created.
    previous_values = (event.data.before.to_dict()
                        if event.data.before is not None else None)

    # Get the changed lab result details.
    uid = event.params['uid']
    lab_result_id = event.params['lab_result_id']
    print('User:', uid, 'changed lab result:', lab_result_id)

    # TODO: Remove lab result from `public/data/lab_results` if it was deleted.


    # TODO: Update `public/data/lab_results` if there are new lab results.
    

    # TODO: See if the data exists in 'public/data/lab_results',
    # if so, then update it, otherwise create it.


    # TODO: Calculate lab results statistics (once per day?).
