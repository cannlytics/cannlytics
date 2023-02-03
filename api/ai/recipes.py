"""
AI Views | BudderBaker | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/2/2023
Updated: 2/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with AI-generated recipes.
"""
# Standard imports.
from datetime import datetime
from json import loads

# External imports.
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ulid

# Internal imports.
from cannlytics.firebase import (
    get_document,
    update_documents,
)


@api_view(['GET', 'POST'])
def recipes_api(request, strain=None):
    """Get, create, update, and delete AI-generated recipes."""

    # TODO: Require the user to pass a CANNLYTICS_API_KEY.

    # Get the parameters.
    params = request.query_params

    # Get recipe(s).
    if request.method == 'GET':

        # TODO: Get recipes the user has created.
        data = []
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Create or update recipe(s).
    elif request.method == 'POST':

        # Get the data the user posted.
        data = loads(request.body.decode('utf-8'))

        # TODO: Create or update recipe with AI!
        data = []
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Delete recipe(s).
    elif request.method == 'POST':
        
        # TODO: Remove recipe related data.
        response = {'success': True, 'data': None}
        return Response(response, status=200)
