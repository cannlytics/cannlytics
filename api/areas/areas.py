"""
Areas Endpoint Views | Cannlytics API
Created: 5/8/2021
Updated: 7/7/2021

API to interface with organization areas.
"""
# pylint:disable=line-too-long

# Internal imports
from json import loads

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authenticate_request
from api.api import get_objects, update_object, delete_object

@api_view(['GET', 'POST', 'DELETE'])
def areas(request, format=None, area_id=None):
    """Get, create, or update information about organization areas."""

    # Initialize and authenticate.
    model_id = area_id
    model_type = 'areas'
    model_type_singular = 'area'
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        owner = claims.get('owner', [])
        team = claims.get('team', [])
        qa = claims.get('qa', [])
        authorized_ids = owner + team + qa
    except KeyError:
        message = 'Your request was not authenticated. Ensure that you have a valid session or API key.'
        return Response({'error': True, 'message': message}, status=401)

    # Authorize that the user can work with the data.
    organization_id = request.query_params.get('organization_id')
    if organization_id not in authorized_ids:
        message = f'Your must be an owner, quality assurance, or a team member of this organization to manage {model_type}.'
        return Response({'error': True, 'message': message}, status=403)

    # GET objects.
    if request.method == 'GET':
        docs = get_objects(request, authorized_ids, organization_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST objects.
    elif request.method == 'POST':

        data = update_object(request, claims, model_type, model_type_singular, organization_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE objects.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, organization_id, owner, qa)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)
