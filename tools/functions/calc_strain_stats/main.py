"""
Calculate Strain Stats | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 7/5/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate statistics for strains and save them to a
    Firestore collection when a user's strain data changes.
    Firebase Functions for Firestore.

"""
from firebase_functions import firestore_fn, options
from firebase_admin import initialize_app, firestore

# Initialize Firebase.
initialize_app()


# Set the region.
options.set_global_options(region=options.SupportedRegion.US_CENTRAL1)


@firestore_fn.on_document_written(
    document='users/{uid}/strains/{strain_id}',
    timeout_sec=300,
    memory=options.MemoryOption.MB_512,
)
def calc_strain_stats(
        event: firestore_fn.Event[firestore_fn.Change],
    ) -> None:
    """Calculate statistics for a strain and save them to a
    Firestore collection when a user's strain data changes."""

    # Get an object with the current document values.
    # If the document does not exist, it was deleted.
    document = (event.data.after.to_dict()
                if event.data.after is not None else None)

    # Get an object with the previous document values.
    # If the document does not exist, it was newly created.
    previous_values = (event.data.before.to_dict()
                        if event.data.before is not None else None)


    # Get the user's ID.
    uid = cloud_event.params['uid']

    # Return if the document was deleted.
    if document is None:
        print('User stain deleted.')
        return

    # Identify the strain.
    # strain_id = event.params['strain_id']
    strain_name = document['strain_name']
    favorite = document['favorite']
    print('User:', uid, 'changed strain data:', strain_name)
    print('Favorite:', favorite)

    # Initialize Firestore.
    db = firestore.client()

    # Calculate the total number of users who have that strain as a favorite.
    total_favorites = 0
    strains = db.collection_group('strains').where('name', '==', strain_name)
    docs = strains.stream()
    for doc in docs:
        data = doc.to_dict()
        if data.get('favorite'):
            total_favorites += 1

    # Format stats.
    stats = {'total_favorites': total_favorites}
    
    # Update the strain's statistics.
    ref = db.collection('public').document('data').collection('strains').document(strain_name)
    ref.update(stats)
    print('Updated strain statistics.')
