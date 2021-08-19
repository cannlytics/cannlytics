"""
Regulation Data Endpoints | Cannlytics API
Created: 5/30/2021
Updated: 7/31/2021

API endpoints to interface with regulation data.
"""

# Standard imports
from datetime import datetime

# External imports
from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth import auth
from cannlytics.firebase import (
    get_collection,
    get_document,
    update_document,
)


# TODO: Given a sample type and state, return the required analyses.


@api_view(['GET'])
def regulations(request, format=None):
    """Get regulation information."""
    message = f'Get information about regulations on a state-by-state basis.'
    return Response({'message': message}, content_type='application/json')
