"""
Waste Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/15/2021
Updated: 12/15/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory transfers, transporters, and vehicles.
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
def waste(request: Response, waste_item_id: str = '') -> Response:
    """Get, create, or update information about cannabis analyses."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='waste',
        model_type_singular='waste_item',
        model_id=waste_item_id,
    )
    return Response(response, status=status_code)
