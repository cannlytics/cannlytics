"""
Parse COA Jobs | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/25/2023
Updated: 8/28/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Perform COA parsing jobs in a cloud function upon job creation in
    Firestore. Outputs job data back to Firestore.

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from firebase_admin import initialize_app, firestore
import requests


# Define the API URL.
DEBUG = True
API_URL = 'https://cannlytics.com/api/data/coas'
if DEBUG:
    API_URL = 'http://127.0.0.1:8000//api/data/coas'

# Initialize Firebase.
try:
    initialize_app()
except ValueError:
    pass


def parse_coa_jobs(data, context) -> None:
    """Perform COA parsing jobs when a user's jobs changes."""

    # Initialization.
    start_time = datetime.now()

    # Get a dictionary representing the document
    uid = data.get('uid', 'cannlytics')
    job_id = data.get('job_id')
    print('User:', uid, 'Job:', job_id)

    # Get the COA URL.
    coa_url = data.get('job_file_url')
    print('COA URL:', coa_url)
    if coa_url is None:
        print('No COA URL provided')
        return
    
    # Read Cannlytics API key.
    cannlytics_api_key = os.getenv('CANNLYTICS_API_KEY')
    if cannlytics_api_key is not None:
        print('Found API key.')

    # Make a request to parse the COA.
    headers = {'Authorization': 'Bearer %s' % cannlytics_api_key}
    response = requests.post(API_URL, json={'urls': [coa_url]}, headers=headers)
    print('Response:', response.status_code)
    try:
        lab_result_data = response.json()
    except:
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
        print('Job finished successfully')
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
    ref = db.collection('users').document(uid).collection('parse_coa_jobs').document(job_id)
    ref.set(job_data, merge=True)


# === Test ===
if __name__ == '__main__':

    # Mock authentication sign up.
    data = {
        'uid': 'qXRaz2QQW8RwTlJjpP39c1I8xM03',
        'email': 'help@cannlytics.com',
        'job_id': 'qTgyQPGxuIob84hjoUKG',
        'job_file_url': 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/users%2FqXRaz2QQW8RwTlJjpP39c1I8xM03%2Fparse_coa_jobs%2FqTgyQPGxuIob84hjoUKG?alt=media&token=2c91bd89-d5d7-4c03-a313-dbb19ba876c2',
    }
    parse_coa_jobs(data, {})
