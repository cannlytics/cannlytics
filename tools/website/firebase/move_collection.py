"""
Move Firestore Collection | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 8/1/2021
Updated: 12/30/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line example:

    ```
    python tools/firebase/move_collection.py labs public/data/labs
    ```

"""
# Standard imports.
import os
import sys
from typing import Optional

# External imports.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
sys.path.append('./')
from cannlytics.firebase import ( # pylint: disable=import-error, wrong-import-position
    delete_document,
    get_collection,
    initialize_firebase,
    update_document,
)


def move_collection(ref: str, dest: str, delete: Optional[bool] = False):
    """Move one collection to another collection.
    Args:
        ref (str): The original collection.
        dest (str): The new collection.
        delete (bool): Wether or not to delete the original documents,
            `False` by default.
    """
    print(f'Moving documents from {ref} to {dest}...')
    docs = get_collection(ref)
    for doc in docs:
        update_document(dest + '/' + doc['id'], doc)
        if delete:
            delete_document(ref + '/' + doc['id'])
    print(f'Moved all documents in {ref} to {dest}.')


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

    # Read arguments from the command line.
    original_ref = sys.argv[1]
    destination_ref = sys.argv[2]

    # Move the collection.
    move_collection(original_ref, destination_ref)
