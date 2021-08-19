"""
Calculate Statistics for Organizations | Cannlyitcs

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/24/2021
Updated: 7/24/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

# External imports
# from firebase_admin import firestore, initialize_app
import pandas as pd

# TODO: Publish cannlytics to PyPi and import the following:
# - create_reference

# Internal imports
import sys
sys.path.append('../../')
from cannlytics.firebase import (
    create_reference,
    get_collection,
    get_document,
    initialize_firebase,
)

# TODO: Import from cannlytics.firebase
def create_reference(database, path):
    """Create a database reference for a given path.
    Args:
        database (Firestore Client): The Firestore Client.
        path (str): The path to the document or collection.
    Returns:
        (ref): Either a document or collection reference.
    """
    ref = database
    parts = path.split('/')
    for i in range(len(parts)):
        part = parts[i]
        if i % 2:
            ref = ref.document(part)
        else:
            ref = ref.collection(part)
    return ref


def calc_org_statistics(organization_id, data_models):
    """Calculate statistics for a given organization.
    Args:
        organization_id (str): The ID for a given organization.
        data_models (list): A list of data models for which to calculate statistics.
    Returns:
        (dict): A dictionary of statistics of an organization.        
    """

    # TODO: Daily stats

    # TODO: Weekly stats

    # TODO: Monthly stats

    # TODO: Summary stats (total, mean, max, min, std. dev)

    # Highlights:
        # Total samples, projects, clients
        # Turnaround time
        # Measurement trending

    return {}


def get_data_models(organization_id):
    """Get the data models for a given organization.
    Args:
        organization_id (str): The ID for a given organization.
    Returns:
        (list): A list of an organization's data models.
    """

    return []


def calculate_stats(request):
    """Calculate statistics for a given organization.
    Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    
    print('Calculating statistics...')

    # Set CORS headers for the preflight request
    # https://cloud.google.com/functions/docs/writing/http#handling_cors_requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    # TODO: Authenticate the user. (Allow session cookie or API key)
    token = request.headers['Authorization'].split(' ').pop()
    request_json = request.get_json()
    # request.args
    try:
        initialize_app()
    except ValueError:
        pass
    db = firestore.client()
    organization_id = ''
    print('Calculating organization stats:', organization_id)

    # Get the organization's data model data.
    data_models = get_data_models(organization_id)

    # Calculate statistics for the organization.
    stats = calc_org_statistics(organization_id, data_models)

    # Save the statistics to the organizations stats collection in Firestore.
    for key, values in stats.items():
        print('Saving stats:', key)
        ref = create_reference(key)
        ref.set(values, merge=True)

    # Return a success message.
    data = {'success': True, 'message': 'Organization statistics updated.'}
    return (data, 200, headers)

if __name__ == '__main__':
    
    print('Testing...')
    import os
    import environ
    
    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = initialize_firebase()
    
    # Get parameters.
    org_id = 'test-company'
    
    # For each data model, calculate stats
    ref = f'organizations/{org_id}/data_models'
    data_models = get_collection(ref)
    for data_model in data_models[:1]:
        
        # Calculate stats for given data model.
        key = data_model['key']
        data_ref = f'organizations/{org_id}/{key}'
        data = get_collection(data_ref)
        
        # TODO: Daily stats
    
        # TODO: Weekly stats
    
        # TODO: Monthly stats
    
        # TODO: Summary stats (total, mean, max, min, std. dev)
    
        # Highlights:
            # Total samples, projects, clients
            # Turnaround time
            # Measurement trending
