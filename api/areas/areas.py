"""
Areas Endpoint Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 5/8/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with organization areas.
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
def areas(request: Response, area_id: str = '') -> Response:
    """Get, create, or update information about organization areas."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='areas',
        model_type_singular='area',
        model_id=area_id,
    )
    return Response(response, status=status_code)
