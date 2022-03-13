"""
Projects Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory projects.
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
def projects(request: Response, project_id: str = '') -> Response:
    """Get, create, or update laboratory projects, a group of samples
#     submitted at the same time by a given organization."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='projects',
        model_type_singular='project',
        model_id=project_id,
    )
    return Response(response, status=status_code)
