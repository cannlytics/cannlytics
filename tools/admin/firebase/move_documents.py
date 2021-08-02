"""
Move Firestore Documents | Cannlytics Console

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/1/2021
Updated: 8/1/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

import os
import environ

import sys
sys.path.append('../../../')
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
    env = environ.Env()
    env.read_env('../../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # Move document(s).
    move_collection('events', 'public/events/event_data')
    move_collection('partners', 'public/partners/partner_data')
    move_collection('team', 'public/team/team_members')
    move_collection('whitepapers', 'public/whitepapers/whitepaper_data')
    move_collection('contributors', 'public/contributors/contributor_data')
