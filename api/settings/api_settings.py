"""
Settings | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/22/2021
Updated: 12/28/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with a user's or organization's settings.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from api.api import get_objects, update_object


@api_view(['GET', 'POST'])
def logs(request, log_id=None):
    """Get and create logs."""

    # Initialize and authenticate.
    model_id = log_id
    model_type = 'logs'
    model_type_singular = 'log'
    claims = authenticate_request(request)
    try:
        claims['uid'] #pylint: disable=pointless-statement
        owner = claims.get('owner', [])
        team = claims.get('team', [])
        quality_control = claims.get('qc', [])
        authorized_ids = owner + team + quality_control
    except KeyError:
        message = 'Your request was not authenticated. Ensure that you have a valid session or API key.'
        return Response({'error': True, 'message': message}, status=401)

    # Authorize that the user can work with the data.
    organization_id = request.query_params.get('organization_id')
    if organization_id not in authorized_ids:
        message = f'Your must be an owner, quality assurance, or a team member of this organization to manage {model_type}.'
        return Response({'error': True, 'message': message}, status=403)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, authorized_ids, organization_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, organization_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)

    # Return an error message if post fails.
    message = 'Data not recognized. Please post either a singular object or an array of objects.'
    return Response({'error': True, 'message': message}, status=400)
