"""
Analytes Endpoint Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with analysis analytes.
"""
# External imports.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from typing import Any, Dict

# Internal imports.
from api.api import get, post, delete, handle_request

ACTIONS = {
    'GET': get,
    'POST': post,
    'DELETE': delete,
}


@api_view(['GET', 'POST', 'DELETE'])
def analytes(request: Dict[str, Any], analyte_id: str = '') -> Response:
    """Get, create, or update information about cannabis analyses."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='analytes',
        model_type_singular='analyte',
        model_id=analyte_id,
    )
    return Response(response, status=status_code)
