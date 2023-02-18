"""
Move Firestore Documents
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Move a Firestore collection from a location to a destination.

Command-line example:

    ```
    python tools/admin/firebase/move_documents location destination
    ```
"""
# Standard imports.
import os
import sys

# External imports.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
from cannlytics import firebase # pylint: disable=import-error


def move_collection(ref, dest, delete=False):
    """Move one collection to another collection.
    Args:
        ref (str): The original collection.
        dest (str): The new collection.
        delete (bool): Wether or not to delete the original documents,
            `False` by default.
    """    
    docs = firebase.get_collection(ref)
    for doc in docs:
        firebase.update_document(dest + '/' + doc['id'], doc)
        if delete:
            firebase.delete_document(ref + '/' + doc['id'])


if __name__ == '__main__':

    # Initialize Firebase.
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Move document(s).
    LOCATION = sys.argv[1]
    DESTINATION = sys.argv[2]
    # TODO: Allow the user to specify `delete` from the command line.
    move_collection(LOCATION, DESTINATION)
