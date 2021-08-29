"""
Update Firestore Documents | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/21/2021
Updated: 8/21/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
from datetime import datetime
import os
import environ

import sys
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
    env = environ.Env()
    env.read_env('../../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # Update all docs in a given collection.
    set_updated_at('organizations/test-company/analytes')
