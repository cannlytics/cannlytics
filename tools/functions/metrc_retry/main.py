"""
Retry Metrc API Calls
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/14/2023
Updated: 1/15/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
import base64
import os
import requests

# External imports.
from cannlytics.firebase import (
    # initialize_firebase,
    get_collection,
    update_documents,
)
from firebase_admin import initialize_app, firestore


# TODO: Watch metrc logs.


# TODO: Get log data.


# TODO: Retry the specific Metrc request.


# TODO: Resolve the request or increment failure count.


# TODO: On 3rd failure, email admin.

