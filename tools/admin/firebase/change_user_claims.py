"""
Change User Custom Claims | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 6/13/2021
Updated: 3/25/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: Change a user's custom claims.

Command-line example:

    ```
    python admin/firebase/change_user_claims uid {"owner": [""]}
    ```
"""
# Standard imports.
import json
import os
import sys

# External packages.
from dotenv import dotenv_values

# Internal imports.
sys.path.append('../../..')
from cannlytics import firebase # pylint: disable=import-error


if __name__ == '__main__':

    # Initialize Firebase
    config = dotenv_values('../../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # TODO: Specify a user's ID and their desired claims.
    UID = sys.argv[1]
    CLAIMS = json.loads(sys.argv[2])
    firebase.update_custom_claims(UID, claims=CLAIMS)
