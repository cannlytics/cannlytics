"""
Contacts Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 8/30/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with organization contacts and people associated with
the contact.
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
def contacts(request: Response, contact_id: str = '') -> Response:
    """Get, create, or update information about organization contacts."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='contacts',
        model_type_singular='contact',
        model_id=contact_id,
    )
    return Response(response, status=status_code)


@api_view(['GET', 'POST', 'DELETE'])
def people(request: Response, person_id: str = '') -> Response:
    """Get, create, update, and delete information for people associated
    with a contact."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='people',
        model_type_singular='person',
        model_id=person_id,
    )
    return Response(response, status=status_code)
