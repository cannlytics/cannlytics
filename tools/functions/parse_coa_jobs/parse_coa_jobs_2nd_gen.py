"""
Parse COA Jobs | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/25/2023
Updated: 8/26/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Perform COA parsing jobs.

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cloudevents.http import CloudEvent
from firebase_admin import initialize_app, firestore
import functions_framework
from google.events.cloud import firestore
import requests

# Initialize Firebase.
initialize_app()


@functions_framework.cloud_event
def parse_coa_jobs(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document.
    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    # Extract the Firestore event data.
    firestore_payload = firestore.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    # Extract parameters from the resource name.
    # Assuming the document name format is: projects/{project_id}/databases/(default)/documents/users/{uid}/parse_coa_jobs/{job_id}
    resource_name = cloud_event['source'].split('/')
    uid = resource_name[-3]
    job_id = resource_name[-1]
    print('User:', uid, 'Job:', job_id)

    # Initialize Firestore DB.
    db = firestore.Client()

    # Read Cannlytics API key.
    cannlytics_api_key = os.getenv('CANNLYTICS_API_KEY')
    if cannlytics_api_key is not None:
        print('Found API key.')

    # Check if the document is new.
    # TODO: This part may need some refinement, because it's not clear how you determine a new job.
    print('New job being created')
    start_time = datetime.now()

    # Get the COA URL.
    job_information = firestore_payload.value.fields
    coa_url = job_information.get('job_file_url').string_value
    print('COA URL:', coa_url)
    if not coa_url:
        print('No COA URL provided')
        return

    # Make a request to parse the COA.
    api_url = 'https://cannlytics.com/api/data/coas'
    headers = {'Authorization': 'Bearer %s' % cannlytics_api_key}
    response = requests.post(api_url, data={'urls': [coa_url]}, headers=headers)
    print('Response:', response.status_code)

    try:
        lab_result_data = response.json()
    except:
        lab_result_data = {}

    # Once we have the response, update the job.
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
    ref = db.collection('users').document(uid).collection('parse_coa_jobs').document(job_id)
    ref.set(job_data, merge=True)
