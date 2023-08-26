"""
Parse COA Jobs | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/25/2023
Updated: 8/25/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Perform COA parsing jobs.

"""
# External imports:
from datetime import datetime
from firebase_admin import initialize_app, firestore
from firebase_functions import options
from firebase_functions.firestore_fn import (
  on_document_created,
  Event,
  Change,
  DocumentSnapshot,
)
import requests


# Initialize Firebase.
initialize_app()

# Set the region.
options.set_global_options(region=options.SupportedRegion.US_CENTRAL1)


@on_document_created(
    document='users/{uid}/parse_coa_jobs/{job_id}',
    timeout_sec=900,
    memory=options.MemoryOption.MB_512,
)
def parse_coa_jobs(event: Event[Change[DocumentSnapshot]]) -> None:
    """Perform COA parsing jobs when a user's jobs changes."""

    # Initialize Firestore DB.
    db = firestore.client()

    # Get a dictionary representing the document
    uid = event.params['uid']
    job_id = event.params['job_id']
    job_information = event.data.to_dict()

    # Access a particular field as you would any dictionary
    name = new_value["name"]

    # TODO: Read Cannlytics API key?

    # Get job and user details.
    uid = event.params['uid']
    job_id = event.params['job_id']
    print('User:', uid, 'Job:', job_id)

    # If the document is new, it's a new job being created.
    print("New job being created")
    start_time = datetime.now()

    # Make a request to parse the COA.
    coa_file_path = document.get('coa_file_path')  # Assuming this is in the document.
    # TODO: Implement logic to request the parsing service.
    response = requests.post("YOUR_PARSING_ENDPOINT_URL", data={"file_path": coa_file_path})
    
    end_time = datetime.now()

    # Once we have the response, update the job.
    if response.status_code == 200:  # Assuming 200 means success.
        lab_result_data = response.json()
        db.collection('users').document(uid).collection('parse_coa_jobs').document(job_id).update({
            "job_finished_at": end_time.isoformat(),
            "job_error": False,
            "job_finished": True,
            "job_duration_seconds": (end_time - start_time).seconds,
            **lab_result_data
        })
        print("Job finished successfully")
    else:
        error_message = response.text
        db.collection('users').document(uid).collection('parse_coa_jobs').document(job_id).update({
            "job_finished_at": end_time.isoformat(),
            "job_error": True,
            "job_error_message": error_message,
            "job_finished": True,
            "job_duration_seconds": (end_time - start_time).seconds
        })
        print(f"Job failed with error: {error_message}")
     