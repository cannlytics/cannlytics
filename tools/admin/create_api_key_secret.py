"""
Create API Key Secret
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/13/2021
Updated: 1/31/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Save sensitive API keys as secrets.
"""
# Standard imports.
import os
import sys

# External imports.
from cannlytics import firebase
from dotenv import dotenv_values


def create_project_secret(project_id, secret_id, secret, ref, field):
    """Create a secret for the project.
    Args:
        project_id (str): The Firebase project ID.
        secret_id (str): A unique ID for the secret.
        secret (str): The secret message.
        ref (str): The document to store the secret ID and version ID.
        field (str): The field in the document for the secret IDs.
    Returns:
        (dict): A dictionary with the `project_id`, `secret_id`, and
            `version_id`.
    """

    # Create a secret.
    try:
        firebase.create_secret(project_id, secret_id, secret)
    except:
        pass # Secret may already be created (AlreadyExists).

    # Add the secret's secret data.
    secret = firebase.add_secret_version(project_id, secret_id, secret)
    version_id = secret.split('/')[-1]

    # Save the project ID, secret ID, version ID in Firestore.
    data = {field: {
        'project_id': project_id,
        'secret_id': secret_id,
        'version_id': version_id,
    }}
    firebase.update_document(ref, data)
    return data


# === Test ===
if __name__ == '__main__':

    # Initialize Firebase
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Create Metrc vendor API key secret.
    # TODO: Allow secret_id, ref, and field to be dynamic.
    PROJECT_ID = config['FIREBASE_PROJECT_ID']
    SECRET = config['METRC_VENDOR_API_KEY']
    STATE = config.get('METRC_STATE', 'ok')
    TEST = config.get('METRC_TEST', False)
    if TEST:
        secret_id = f'metrc_test_vendor_api_key_{STATE}'
        SECRET = config['METRC_TEST_VENDOR_API_KEY']
    else:
        secret_id = f'metrc_vendor_api_key_{STATE}'
    secret_data = create_project_secret(
        PROJECT_ID,
        secret_id=secret_id,
        secret=SECRET,
        ref='admin/metrc',
        field='vendor_api_key_secret'
    )
