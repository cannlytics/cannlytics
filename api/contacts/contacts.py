"""
Contacts Views | Cannlytics API
Created: 4/21/2021
Updated: 8/30/2021

API to interface with organization contacts and people associated with
the contact.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authorize_user
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def contacts(request, contact_id=None):
    """Get, create, update, and delete organization contact information."""

    # Initialize.
    model_id = contact_id
    model_type = 'contacts'
    model_type_singular = 'contact'
    
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


@api_view(['GET', 'POST', 'DELETE'])
def people(request, person_id=None):
    """Get, create, update, and delete information for people associated
    with a contact."""

    # Initialize and authenticate.
    model_id = person_id
    model_type = 'people'
    model_type_singular = 'person'
    
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
