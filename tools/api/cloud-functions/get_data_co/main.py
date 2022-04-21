"""
Get Data - Colorado | Cannlytics Website
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2022
Updated: 4/21/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
import base64
import os
import requests

# External imports.
from cannlytics.firebase import (
    initialize_firebase,
    get_collection,
    update_documents,
)
from firebase_admin import initialize_app, firestore


def get_data_co(event, context):
    """
    Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'success':
        return

    # Initialize Firebase.
    print('Initializing Firebase')
    database = initialize_firebase()
    # try:
    #     initialize_app()
    # except ValueError:
    #     pass
    # database = firestore.client()
    print('Initialized Firebase')
