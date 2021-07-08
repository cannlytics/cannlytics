"""
Data Endpoints | Cannlytics API
Created: 5/30/2021
Updated: 7/8/2021

API endpoints to interface with datasets.
"""

# Standard imports
from datetime import datetime

# External imports
from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth import auth
from cannlytics.firebase import (
    get_collection,
    get_document,
    update_document,
)


@api_view(['GET', 'POST'])
def data(request, format=None):
    """Get or update information about datasets."""

    # Authenticate the user.
    claims = auth.verify_session(request)
    uid = claims['uid']

    if request.method == 'GET':

        org_id = ''
        ref = '/organizations/%s/areas'

        # TODO: If no organization is specified, get the user's
        # organizations and get all areas for all licenses.

        # IF the organization is specified, get all areas for all
        # licenses of the organization.

        # If the organization and license is specified, get all areas
        # for the given organization's license.

        # If a specific area ID is given, get only that area.

        # If a filter parameter is given, then return only the areas
        # that match the query.
        # limit = request.query_params.get('limit', None)
        # order_by = request.query_params.get('order_by', 'state')
        # data = get_collection(ref, order_by=order_by, limit=limit, filters=[])

        # Optional: If a user is using traceability, then is there any
        # need to get location data from the API, or is the data in
        # Firestore sufficient (given Firestore is syncing with Metrc).
        # Otherwise, initialize a Metrc client and get areas from Metrc.
        # traced_location = cultivator.get_locations(uid=cultivation_uid)  

        # # Optional: Get any filters from dict(request.query_params)
        
        return Response([{'make': "Subaru", 'model': "WRX", 'price': 21000}])
    
    elif request.method == 'POST':

        # TODO: Either create or update the area.

            # # Create a new location using: POST /locations/v1/create
            # cultivation_name = 'MediGrow'
            # cultivation_original_name = 'medi grow'
            # cultivator.create_locations([
            #     cultivation_original_name,
            #     'Harvest Location',
            #     'Plant Location',
            #     'Warehouse',
            # ])
            
            # # Get created location
            # cultivation= None
            # locations = track.get_locations(action='active', license_number=cultivator.license_number)
            # for location in locations:
            #     if location.name == cultivation_original_name:
            #         cultivation = location

            # # Update the name of the location using: POST /locations/v1/update
            # cultivator.update_locations([cultivation.uid], [cultivation_name])

        return Response({'data': []})

    elif request.method == 'Delete':

        # TODO: Archive the area data and delete from Metrc.

        return Response({'data': []})


#----------------------------------------------#
# Informational Endpoints
#----------------------------------------------#

@api_view(['GET'])
def regulations(request, format=None):
    """Get regulation information."""
    message = f'Get information about regulations on a state-by-state basis.'
    return Response({'message': message}, content_type='application/json')


#----------------------------------------------#
# Lab endpoints
#----------------------------------------------#

@api_view(['GET'])
def lab(request, format=None):
    """Get or update information about a lab."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get('limit', None)
        order_by = request.query_params.get('order_by', 'state')
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ 'data': labs}, content_type='application/json')


@api_view(['GET', 'POST'])
def labs(request, format=None):
    """Get or update information about labs."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get('limit', None)
        order_by = request.query_params.get('order_by', 'state')
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ 'data': labs}, content_type='application/json')

    # Update a lab given a valid Firebase token.
    elif request.method == 'POST':

        # Check token.
        try:
            claims = auth.authenticate(request)
        except:
            return Response({'error': 'Could not auth.authenticate.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the posted lab data.
        lab = request.data
        org_id = lab['id']
        lab['slug'] = slugify(lab['name'])

        # TODO: Handle adding labs.
        # Create uuid, latitude, and longitude, other fields?

        # Determine any changes.
        existing_data = get_document(f'labs/{org_id}')
        changes = []
        for key, after in lab:
            before = existing_data[key]
            if before != after:
                changes.append({'key': key, 'before': before, 'after': after})

        # Get a timestamp.
        timestamp = datetime.now().isoformat()
        lab['updated_at'] = timestamp

        # Create a change log.
        log_entry = {
            'action': 'Updated lab data.',
            'type': 'change',
            'created_at': lab['updated_at'],
            'user': claims['uid'],
            'user_name': claims['display_name'],
            'user_email': claims['email'],
            'photo_url': claims['photo_url'],
            'changes': changes,
        }
        update_document(f'labs/{org_id}/logs/{timestamp}', log_entry)

        # Update the lab.
        update_document(f'labs/{org_id}', lab)

        return Response(log_entry, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def lab_logs(request, org_id, format=None):
    """Get or create lab logs."""

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/logs')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create a log.
        return Response({ 'data': 'Under construction'}, content_type='application/json')


@api_view(['GET', 'POST'])
def lab_analyses(request, org_id, format=None):
    """
    Get or update (TODO) lab analyses.
    """

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/analyses')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create an analysis.
        return Response({ 'data': 'Under construction'}, content_type='application/json')
