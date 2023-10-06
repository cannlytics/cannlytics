"""
Parse Receipt Jobs | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/3/2023
Updated: 9/4/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Perform receipt parsing jobs in a cloud function upon job creation
    in Firestore. Outputs job data back to Firestore.

Note:

    This function is written for Gen 1 Google Cloud Functions.
    In the future, it may be necessary to migrate the code to Gen 2.

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics import firebase
from firebase_admin import auth, initialize_app, firestore
import requests


# Define the API URL.
DEBUG = False
API_URL = 'https://cannlytics.com/api/data/receipts'
if DEBUG:
    API_URL = 'http://127.0.0.1:8000//api/data/receipts'

# Initialize Firebase.
try:
    initialize_app()
except ValueError:
    pass

# Define the URL to verify a custom token.
_verify_token_url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken'


def _sign_in(custom_token, api_key):
    """Sign in a user with a custom token."""
    body = {'token' : custom_token.decode(), 'returnSecureToken' : True}
    params = {'key' : api_key}
    resp = requests.request('post', _verify_token_url, params=params, json=body)
    resp.raise_for_status()
    return resp.json().get('idToken')


def parse_receipt_jobs(event, context) -> None:
    """Perform receipt parsing jobs when a user's jobs changes."""

    # Initialization.
    start_time = datetime.now()

    # Get the user's UID from the path.
    # Note: This is important because Firestore rules only allows
    # users to write to their own collection.
    path_parts = context.resource.split('/documents/')[1].split('/')
    uid = path_parts[1]
    print('USER:', uid)

    # Get the necessary data.
    data = event['value']['fields']
    job_id = data['job_id']['stringValue']
    print('JOB ID:', job_id)

    # Ensure the user passed a COA URL.
    job_file_url = data['job_file_url']['stringValue']
    print('JOB FILE URL:', job_file_url)
    if job_file_url is None:
        print('No job file URL provided.')
        return
    
    # Get an ID token through the Identity Toolkit API.
    # FIXME: Service account does not have permission to create custom tokens.
    credit = False
    try:
        api_key = os.getenv('IDENTITY_TOOLKIT_API_KEY')
        if api_key:
            print('API key found.')
        user = auth.get_user(uid)
        if user.custom_claims:
            print('Custom claims found.')
        custom_token = auth.create_custom_token(uid, user.custom_claims)
        if custom_token:
            print('Custom token created.')
        id_token = _sign_in(custom_token, api_key)
        if id_token:
            print('ID token created.')
    except:
        credit = True
        id_token = os.getenv('CANNLYTICS_API_KEY')
        print('Proceeding with Cannlytics API key.')
        ref = f'subscribers/{uid}'
        user_subscription = firebase.get_document(ref)
        current_tokens = user_subscription.get('tokens', 0) if user_subscription else 0
        if current_tokens < 1:
            raise Exception('User does not have enough tokens to perform this action.')

    # Make a request to parse the receipt.
    headers = {'Authorization': 'Bearer %s' % id_token}
    body = {'urls': [job_file_url]}
    response = requests.post(API_URL, json=body, headers=headers)
    print('Response status code:', response.status_code)
    try:
        lab_result_data = response.json()['data'][0]
    except Exception as e:
        print('Failed to parse response:', e)
        lab_result_data = {}

    # Once the request is complete, update the job.
    end_time = datetime.now()
    if response.status_code == 200:
        job_data = {
            'job_finished_at': end_time.isoformat(),
            'job_error': False,
            'job_finished': True,
            'job_duration_seconds': (end_time - start_time).seconds,
            **lab_result_data
        }
        print('Job finished successfully.')
        if credit:
            current_tokens -= 1
            firebase.increment_value(ref=ref, field='tokens', amount=-1)
    else:
        error_message = response.text
        job_data = {
            'job_finished_at': end_time.isoformat(),
            'job_error': True,
            'job_error_message': error_message,
            'job_finished': True,
            'job_duration_seconds': (end_time - start_time).seconds
        }
        print(f'Job failed with error: {error_message}')

    # Save the data to Firestore.
    db = firestore.client()
    ref = db.collection('users').document(uid).collection('parse_receipt_jobs').document(job_id)
    ref.set(job_data, merge=True)


# === Test ===
# [ ] TESTED: 2023-09-04 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    import yaml

    class MockContext:
        def __init__(self, resource):
            self.resource = resource


    def load_env_from_yaml(file_path):
        with open(file_path, 'r') as file:
            env_vars = yaml.safe_load(file)
        for key, value in env_vars.items():
            os.environ[key] = str(value)


    # Load environment variables.
    load_env_from_yaml('./env.yaml')

    # Mock document and context.
    event = {'value': {'fields': {
        'uid': {'stringValue': 'qXRaz2QQW8RwTlJjpP39c1I8xM03',},
        'email': {'stringValue': 'help@cannlytics.com',},
        'job_id': {'stringValue': 'ZqFVb7REkXmrrTlhr3N1',},
        'job_file_url': {'stringValue': 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/users%2FqXRaz2QQW8RwTlJjpP39c1I8xM03%2Fparse_receipt_jobs%2FZqFVb7REkXmrrTlhr3N1?alt=media&token=e6dadca9-69d4-47fd-b128-5ebcefffe9fd',},
    }}}
    context = MockContext('/documents/users/qXRaz2QQW8RwTlJjpP39c1I8xM03/parse_receipt_jobs/ZqFVb7REkXmrrTlhr3N1')

    # Execute the function.
    parse_receipt_jobs(event, context)
