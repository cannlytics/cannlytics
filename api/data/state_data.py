"""
State Data Endpoints | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/9/2022
Updated: 1/9/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API endpoints to interface with datasets.
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
def state_data(request, state=None):
    """Get or update data for a given state."""
    # Optional: Allow authenticated users to edit state data?
    # claims = auth.authenticate_request(request)
    # if request.method == 'GET':
    # if request.method == 'POST':
    #     uid = claims['uid']
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)
