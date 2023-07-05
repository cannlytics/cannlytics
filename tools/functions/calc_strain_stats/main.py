from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore
from firebase_admin import initialize_app, firestore

# Initialize Firebase.
initialize_app()


@functions_framework.cloud_event
def calc_strain_stats(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document.
    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    firestore_payload = firestore.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    print(f"Function triggered by change to: {cloud_event['source']}")

    print("\nOld value:")
    print(firestore_payload.old_value)

    print("\nNew value:")
    print(firestore_payload.value)

    document = firestore_payload.value

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
    strains = db.collection_group('strains').where('strain_name', '==', strain_name)
    docs = strains.stream()
    for doc in docs:
        data = doc.to_dict()
        if data.get('favorite'):
            total_favorites += 1
    
    # Update the strain's statistics.
    ref = f'public/data/strains/{strain_name}'
    data = {'total_favorites': total_favorites}
    ref = db.collection('public').document('data').collection('strains').document(strain_name)
    ref.update(data)
    print('Updated strain statistics.')
