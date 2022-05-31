"""
Strain Data Endpoints | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/17/2022
Updated: 5/27/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with cannabis strain data.
"""
# External imports.
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports.
from cannlytics.firebase import (
    get_collection,
    get_document,
)
from cannlytics.utils.utils import kebab_case


# https://github.com/TracyRenee61/House-Prices/blob/master/Boston_Housing_SelectKBest_.ipynb

# Option 1: User searches for a known strain name

    # A list of strains and their potential effects / aromas are returned.




@api_view(['GET', 'POST'])
def strain_data(request, strain_name=None):
    """Get data about cannabis strains (public API endpoint)."""
    data = []
    collection = 'public/data/strains'
    if request.method == 'GET':

        # Get a specific observation.
        if strain_name is not None:
            strain_id = kebab_case(strain_name)
            data = get_document(f'{collection}/{strain_id}')

        # Otherwise query observations.
        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'state')
            limit = request.query_params.get('limit')

            # Allow user to query by effect / aroma.

            # Allow user to query by cannabinoid / terpene concentrations.

            # Allow user to query by 

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
