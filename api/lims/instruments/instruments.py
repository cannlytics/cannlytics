"""
Instruments Endpoint Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with scientific instruments.
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
def instruments(request: Response, instrument_id: str = '') -> Response:
    """Get, create, or update instrument information."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='instruments',
        model_type_singular='instrument',
        model_id=instrument_id,
    )
    return Response(response, status=status_code)
