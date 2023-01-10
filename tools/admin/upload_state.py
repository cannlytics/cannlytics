"""
Upload State
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/5/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line example:

    ```
    python tools/console/upload_state
    ```
"""
# Standard imports.
import os
import sys

# External imports.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
from cannlytics import firebase # pylint: disable=import-error
from console.state import data_models # pylint: disable=import-error


# === Test ===
if __name__ == '__main__':

    # Initialize Firebase.
    config = dotenv_values('../../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # Upload state data to Firestore.
    for data_model in data_models:
        key = data_model['key']
        if key:
            firebase.update_document(f'public/state/data_models/{key}', data_model)
            firebase.update_document(f'organizations/test-company/data_models/{key}', data_model)
            firebase.update_document(f'organizations/test-processor/data_models/{key}', data_model)

    # Save all data models, excluding fields, to one document.

    # Upload traceability settings to Firestore.
    # traceability = state.material['traceability']
    # firebase.update_document('public/state/traceability/traceability_settings', traceability)
    # firebase.update_document('organizations/test-company/organization_settings/traceability_settings', traceability)
