"""
Measurements Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 6/22/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with analysis measurements.
"""
# External imports.
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports.
from api.api import get, post, delete, handle_request

ACTIONS = {
    'GET': get,
    'POST': post,
    'DELETE': delete,
}


@api_view(['GET', 'POST', 'DELETE'])
def measurements(request: Response, measurement_id: str = '') -> Response:
    """Get, create, or update measurements taken during an analysis."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='measurements',
        model_type_singular='measurement',
        model_id=measurement_id,
    )
    return Response(response, status=status_code)
