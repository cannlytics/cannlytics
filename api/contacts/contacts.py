"""
Contacts Views | Cannlytics API
Created: 4/21/2021
Updated: 7/8/2021

API to interface with organization contacts and people associated with
the contact.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth import auth
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def contacts(request, format=None, contact_id=None):
    """Get, create, update, and delete organization contact information."""

    # Initialize and authenticate.
    model_id = contact_id
    model_type = 'contacts'
    model_type_singular = 'contact'
    claims = auth.verify_session(request)
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

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, authorized_ids, organization_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, organization_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE data.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, organization_id, owner, qa)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)


@api_view(['GET', 'POST', 'DELETE'])
def people(request, format=None):
    """Get, create, update, and delete information for people associated
    with a contact."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
