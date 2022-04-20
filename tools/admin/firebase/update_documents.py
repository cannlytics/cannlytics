"""
Update Firestore Documents | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/21/2021
Updated: 3/25/2022
License: MIT License <https://opensource.org/licenses/MIT>

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
sys.path.append('../../../')
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

if __name__ == '__main__':

    # Initialize Firebase.
    config = dotenv_values('../../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # TODO: Implement useful logic here, such as allowing
    # the user to pass an object (or list?) of data.
    DOCUMENT = sys.argv[1]
    set_updated_at(DOCUMENT)
