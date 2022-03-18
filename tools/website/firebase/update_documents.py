"""
Update Firestore Documents | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 8/21/2021
Updated: 12/30/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line example:

    ```
    python tools/firebase/update_documents.py organizations/test-company/analytes
    ```

"""
# Standard imports.
from datetime import datetime
import os
import sys

# External imports.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
sys.path.append('./')
from cannlytics.firebase import ( # pylint: disable=import-error, wrong-import-position
    get_collection,
    initialize_firebase,
    update_document,
)


def set_updated_at(ref: str):
    """Set the `updated_at` field on all documents in a collection.
    Args:
        ref (str): The original collection.
    """
    print(f'Setting `updated_at` for all documents in {ref}...')
    updated_at = datetime.now().isoformat()
    docs = get_collection(ref)
    for doc in docs:
        entry = {'updated_at': updated_at}
        update_document(ref + '/' + doc['id'], entry)
    print(f'Finished setting `updated_at` for all documents in {ref}.')


if __name__ == '__main__':

    # Initialize Firebase.
    try:
        config = dotenv_values('../../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    initialize_firebase()

    # Update all docs in a given collection.
    collection_ref = sys.argv[1]
    set_updated_at(collection_ref)
