"""
Add Partner | Cannlytics Website

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 9/10/2021
Updated: 9/10/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports
from datetime import datetime
import json
import environ
import os

# Internal imports
import sys
root = '../../'
sys.path.append(root)
from cannlytics import firebase # pylint: disable=import-error


def upload_archived_data(
    datafile,
    collection,
    id_key='id',
    stats_doc=''
):
    """ Upload all video data.
    Args:
        datafile (str): The path to a .json file containing the video data.
        collection (str): The path of the collection where data will be stored.
        id_key (str): The key of the ID.
        stats_doc (str): An optional document to store statistics about the data.
    Returns:
        data (list): A list of partner data (dict).
    """
    # Read in the data.
    with open(datafile) as f:
        data = json.load(f)

    # Upload the data to Firestore.
    for item in data:
        item['updated_at'] = datetime.now().isoformat()
        doc_id = item[id_key]
        ref = f'{collection}/{doc_id}'
        firebase.update_document(ref, item)
    
    # Update video statistics.
    if stats_doc:
        firebase.update_document(stats_doc, {'total': len(data)})
    return data


if __name__ == '__main__':

    # Initialize Firebase.
    env = environ.Env()
    env.read_env(f'{root}.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Specify the JSON data file and upload the archived data.
    print('Uploading partner data...')
    datafile = f'../../.datasets/partners.json'
    data = upload_archived_data(
        datafile,
        collection='public/partners/partner_data',
        id_key='partner_id',
        stats_doc='public/partners',
    )
    print('Uploaded data for all partners. Total:', len(data))
