"""
Strain Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 7/2/2023
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
# from cannlytics.data.strains_ai import StrainsParser
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

# Maximum number of files that can be parsed in one request.
MAX_NUMBER_OF_FILES = 10

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 200_000


# TODO: Get the strain ID.
strain_id = ''

# TODO: Create a strain edit log.
# create_log(
#     f'public/data/strains/{strain_id}/strain_logs',
#     claims=claims,
#     action='Parsed COAs.',
#     log_type='data',
#     key='api_data_coas',
#     changes=changes
# )
