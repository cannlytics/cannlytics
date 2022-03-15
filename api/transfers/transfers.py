"""
Transfers Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory transfers, transporters, and vehicles.
"""
# Standard imports.
from typing import Any, Dict

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


def _post(
        request: Response,
        claims: Dict[str, Any],
        model_type: str,
        model_type_singular: str,
        model_id: str,
        org_id: str,
):
    """Extend post for transfers."""
    post(request, claims, model_type, model_type_singular, model_id, org_id)
    # TODO:
    # 1. Send transfer to the receiving organization.
        # - Populate the transfer data in the receiving organization's transfers
        # ensuring that no existing transfer is overwritten.
    # 2. Notify the receiving organization.
    # 3. Optional: Post transfer to Metrc if user has traceability set up.

@api_view(['GET', 'POST', 'DELETE'])
def transfers(request: Response, transfer_id: str = '') -> Response:
    """Get, create, or update information about cannabis analyses."""
    response, status_code = handle_request(
        request,
        actions={**ACTIONS, **{'POST': _post}},
        model_type='transfers',
        model_type_singular='transfer',
        model_id=transfer_id,
    )
    return Response(response, status=status_code)


@api_view(['POST'])
def receive_transfers(request):
    """Receive incoming transfers."""
    # TODO: Implement receive transfer through the API.
    return NotImplementedError


@api_view(['GET', 'POST', 'DELETE'])
def transporters(request: Response, transporter_id: str = '') -> Response:
    """Get, create, or update information about cannabis analyses."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='transporters',
        model_type_singular='transporter',
        model_id=transporter_id,
    )
    return Response(response, status=status_code)


@api_view(['GET', 'POST', 'DELETE'])
def vehicles(request: Response, vehicle_id: str = '') -> Response:
    """Get, create, or update information about cannabis analyses."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='vehicles',
        model_type_singular='vehicle',
        model_id=vehicle_id,
    )
    return Response(response, status=status_code)
