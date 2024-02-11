"""
Periodically Update the Admin | Cannlytics Website
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/10/2024
Updated: 2/10/2024
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
import base64
import os
import requests

# External imports.
from cannlytics.firebase import (
    get_collection,
    update_documents,
)
from firebase_admin import initialize_app, firestore


def admin_update(event, context):
    """Update the admin with the latest happenings.

    Triggered from a message on a Cloud Pub/Sub topic.

    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'success':
        return

    # Initialize Firebase.
    try:
        initialize_app()
    except ValueError:
        pass
    database = firestore.client()

    # TODO: Find any new users.


    # TODO: Find any new organizations.


    # TODO: Get the recent logs.


    # TODO: Perform statistics on the logs.


    # TODO: Ask ChatGPT to summarize the logs.


    # TODO: Count how many documents were created, updated, and deleted.


    # TODO: Get the number of Cloud Run requests.


    # TODO: Count the number of website page visits (for the top 10 visited). 

    
    # TODO: Summarize the data in Firestore:
    # - Number of new results
    # - Number of new strains
    # - Number of new producers
    # - Number of new labs
    # - If any lab result is in the 99th percentile for any cannabinoid or terpene
    # - Any new plant patents
    # - Any new licenses


    # Optional: Any new research articles about cannabis.
