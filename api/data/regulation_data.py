"""
Regulation Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 1/9/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with cannabis regulation data.
"""
# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    get_collection,
    get_document,
)


@api_view(['GET'])
def regulation_data(request, state=None):
    """Get data about cannabis regulations (public API endpoint)."""
    data = []
    collection = 'public/data/regulations'
    if request.method == 'GET':

        # Get a specific observation.
        if state is not None:
            data = get_document(f'{collection}/{state}')

        # Otherwise query observations.
        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'state')
            limit = request.query_params.get('limit')

            # Optional: Implement more queries the user can use.
            # Apply user-specified filters.
            # param = request.query_params.get('param')
            # if param:
            #     filters.append({'key': 'param', 'operation': '==', 'value': param})

            # Query and return the docs.
            data = get_collection(
                collection,
                desc=False,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)
