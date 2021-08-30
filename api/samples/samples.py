"""
Samples Views | Cannlytics API
Created: 4/21/2021
Updated: 8/30/2021

API to interface with laboratory samples.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authorize_user
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def samples(request, sample_id=None):
    """Get, create, or update laboratory samples."""

    # Initialize.
    model_id = sample_id
    model_type = 'samples'
    model_type_singular = 'sample'
    
    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

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
