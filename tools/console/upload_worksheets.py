"""
Upload Data Model Worksheets | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/6/2021
Updated: 3/25/2022
License: MIT License <https://opensource.org/licenses/MIT>

Command-line example:

    ```
    python tools/console/upload_worksheets
    ```
"""
# Standard imports.
import os
from datetime import datetime
import sys

# External packages.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../')
from cannlytics import firebase # pylint: disable=import-error
from console import state # pylint: disable=import-error

if __name__ == '__main__':

    # Initialize Firebase.
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    api_key = firebase.get_document('admin/firebase')['web_api_key']
    bucket_name = config['FIREBASE_STORAGE_BUCKET']
    
    # Upload worksheets to Firebase Storage and update model data in Firestore.
    for key, data_model in state.material['data_models'].items():
        try:
            destination = f'public/state/data_models/{key}_worksheet.xlsm'
            file_name = f'../../console/static/console/worksheets/{key}_worksheet.xlsm'
            firebase.upload_file(bucket_name, destination, file_name)
            data_model['worksheet_url'] = firebase.get_file_url(destination, bucket_name)
            data_model['worksheet_short_link'] = firebase.create_short_url(api_key, data_model['worksheet_url'])
            data_model['worksheet_uploaded_at'] = datetime.now().isoformat()
            firebase.update_document(f'public/state/data_models/{key}', data_model)
            firebase.update_document(f'organizations/test-company/data_models/{key}', data_model)
        except FileNotFoundError:
            print('No worksheet for %s data model.' % data_model['key'])
