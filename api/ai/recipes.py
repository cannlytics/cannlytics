"""
AI Views | BudderBaker | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/2/2023
Updated: 2/4/2023
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

        # TODO: Search for recipes (queries).

        # TODO: Get community-created recipes.

        data = []
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Create or update recipe(s).
    elif request.method == 'POST':

        # Get the data the user posted.
        data = loads(request.body.decode('utf-8'))

        # TODO: Create or update recipe with AI!
        # - Get lab results with CoADoc if possible.
        # - Pair terpenes with ingredients where possible.
        # - Get an image for the recipe.
        # - Ask GPT for the total weight in milligrams of the whole dish
        #   and per serving.
        # - Ask GPT for a fun title for the recipe (pun if possible)
        #   (use product name if possible).
        # - Ask GPT for a description of the recipe.
        # - Calculate:
        #   - mg/serving
        #   - mg/piece
        #   - total_servings
        #   - total_mg

        # TODO: When updating recipes, increment the version number.

        data = []
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Delete recipe(s).
    elif request.method == 'POST':
        
        # TODO: Remove recipe related data.
        response = {'success': True, 'data': None}
        return Response(response, status=200)
