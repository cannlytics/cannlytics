"""
Update Firestore Documents
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 8/21/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Update a given Firestore document given data as an object.

Command-line example:

    ```
    python admin/firebase/update_documents location destination
    ```
"""
# Standard imports.
from datetime import datetime
import os
import sys

# External packages.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
from cannlytics import firebase # pylint: disable=import-error


def set_updated_at(ref):
    """Set the `updated_at` field on all documents in a collection.
    Args:
        ref (str): The original collection.
        dest (str): The new collection.
        delete (bool): Wether or not to delete the original documents,
            `False` by default.
    """    
    updated_at = datetime.now().isoformat()
    docs = firebase.get_collection(ref)
    for doc in docs:
        entry = {'updated_at': updated_at}
        firebase.update_document(ref + '/' + doc['id'], entry)


# === Test ===
if __name__ == '__main__':

    # Initialize Firebase.
    key = 'GOOGLE_APPLICATION_CREDENTIALS'
    try:
        config = dotenv_values('../../.env')
        credentials = config[key]
    except KeyError:
        config = dotenv_values('.env')
    os.environ[key] = credentials
    db = firebase.initialize_firebase()
    
    # TODO: Implement useful logic here, such as allowing
    # the user to pass an object (or list?) of data.
    DOCUMENT = sys.argv[1]
    set_updated_at(DOCUMENT)
