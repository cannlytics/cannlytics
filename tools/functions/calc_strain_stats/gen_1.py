"""
Calculate Strain Stats | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 7/4/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate statistics for strains and save them to a
    Firestore collection when a user's strain data changes.
    Firebase Functions for Firestore.

"""
from firebase_admin import initialize_app, firestore

# Initialize Firebase.
initialize_app()


def calc_strain_stats(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # Get the document and the user.
    document = event['value']['fields']
    uid = document.get('uid', {}).get('stringValue', None)
    print('user:', uid)

    # Return if the document was deleted.
    if document is None:
        print('User stain deleted.')
        return

    # Identify the strain.
    strain_name = document['name']['stringValue']
    print('Strain:', strain_name)

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

