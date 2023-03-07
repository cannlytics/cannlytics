"""
Change User Custom Claims
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/13/2021
Updated: 1/13/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

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
sys.path.append('../..')
from cannlytics import firebase


if __name__ == '__main__':

    # Initialize Firebase
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Specify a user's ID and their desired claims.
    # UID = sys.argv[1]
    # CLAIMS = json.loads(sys.argv[2])
    UID = 'QIxUQ6kO3ZcDIZceJHCl0e1ZaOS2'
    CLAIMS = {
        'owner': ['test-company'],
        'team': ['test-company', 'cannlytics-test']
    }
    firebase.update_custom_claims(UID, claims=CLAIMS)

    # Check the user's claims.
    claims = firebase.get_custom_claims(UID)
    print(claims)
