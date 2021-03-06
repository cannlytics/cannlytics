"""
Create API Key Secret | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 6/13/2021
Updated: 6/13/2021
License: MIT License <https://opensource.org/licenses/MIT>
Description:
    Save sensitive API keys as secrets.
"""
import os
import environ

import sys
sys.path.append('../..')
from cannlytics import firebase # pylint: disable=import-error


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

if __name__ == '__main__':

    # Initialize Firebase
    env = environ.Env()
    env.read_env('../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Create Metrc vendor API key secret.
    PROJECT_ID = env('FIREBASE_PROJECT_ID')
    SECRET = env('METRC_VENDOR_API_KEY')
    secret_data = create_project_secret(
        PROJECT_ID,
        secret_id='metrc_vendor_api_key',
        secret=SECRET,
        ref='admin/metrc',
        field='vendor_api_key_secret'
    )
