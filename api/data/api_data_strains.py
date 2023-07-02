"""
Strain Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 6/24/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with strain data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
import google.auth
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.sales.receipts_ai import ReceiptsParser
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    create_short_url,
    get_collection,
    get_document,
    get_file_url,
    increment_value,
    update_documents,
    upload_file,
    delete_document,
    delete_file,
)
from website.settings import FIREBASE_API_KEY, STORAGE_BUCKET


# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['png', 'jpg', 'jpeg']

