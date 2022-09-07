"""
Inventory Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 8/30/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with inventory.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def inventory(request, inventory_id=None):
    """Get, create, or update inventory."""

    # Initialize.
    model_id = inventory_id
    model_type = 'inventory'
    model_type_singular = 'item'

    # Authenticate the user.
    claims = authenticate_request(request)
    # FIXME: Get `org_id`
    org_id = None
    if claims.get('user') is None:
        message = 'Authentication failed.'
        return Response({'success': False, 'data': message}, status=401)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, claims, org_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, org_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE data.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, org_id)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)
