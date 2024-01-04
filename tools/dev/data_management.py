"""
Data Interface for Tools | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/26/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports.
from datetime import datetime
from typing import List, Optional
import json
import sys

# External imports.
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

# Internal imports.
sys.path.append('./')
sys.path.append('../../')
from cannlytics.firebase import ( # pylint: disable=import-error, wrong-import-position
    get_collection,
    initialize_firebase,
    update_document,
)


def clean_obs(obs: dict) -> dict:
    """Cleans an observation for saving to JSON.
    Args:
        obs (dict): An observation to clean.
    Returns:
        (dict): Returns the cleaned observation.
    """
    item = {}
    for key, value in obs.items():
        if isinstance(value, DatetimeWithNanoseconds):
            item[key] = value.isoformat()
        else:
            item[key] = value
    return item


def get_data(
        ref: str,
        datafile: Optional[str] = '',
        order_by: Optional[str] = '',
    ) -> List[dict]:
    """Get a dataset saved in Firestore.
    Args:
        ref (str): The reference to a collection.
        datafile (str): Save the data locally to the project's `.datasets`
            if a data file is given.
        order_by (str): An optional field to order the results by.
    Returns:
        (list): Returns a list of data (dict).
    """
    print('Getting data...')
    database = initialize_firebase()
    data = get_collection(ref, database=database, order_by=order_by)
    print('Found {} observations.'.format(len(data)))
    if datafile:
        print('Saving data...')
        save_data(data, datafile)
        print('Saved data to', datafile)
    return data


def upload_data(
        file_name: str,
        collection: str,
        id_key: Optional[str] = 'id',
        stats_doc: Optional[str] = '',
    ):
    """ Upload a dataset to Firestore.
    Args:
        datafile (str): The path to a .json file containing the data.
        collection (str): The path of the collection where data will be stored.
        id_key (str): The key of the ID.
        stats_doc (str): An optional document to store statistics about the data.
    Returns:
        data (list): A list of partner data (dict).
    """
    database = initialize_firebase()
    with open(file_name) as datafile:
        data = json.load(datafile)
    print('Uploading dataset...')
    for item in data:
        item['updated_at'] = datetime.now().isoformat()
        doc_id = item[id_key]
        ref = f'{collection}/{doc_id}'
        update_document(ref, item, database=database)
        print('Updated:', ref)
    if stats_doc:
        update_document(stats_doc, {'total': len(data)}, database=database)
        print('Updated:', stats_doc)
    print('Finished uploading data.')
    return data


def save_data(data, file_name):
    """Save a dataset locally."""
    output = [clean_obs(x) for x in data]
    with open(file_name, 'w+') as datafile:
        json.dump(output, datafile, indent=4, sort_keys=True)
