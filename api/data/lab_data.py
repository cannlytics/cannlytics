"""
Lab Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 5/30/2021
Updated: 12/31/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API endpoints to interface with lab data, data about labs and data
that labs provide.
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


@api_view(['GET'])
def lab_data(request, license_number=None):
    """Get laboratory information (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Get a specific organization.
        organization_id = request.query_params.get('organization_id')
        if organization_id and organization_id != 'undefined':
            data = get_document(f'public/data/labs/{organization_id}')

        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'name')
            limit = request.query_params.get('limit')
            state = request.query_params.get('state')
            # Optional: Implement more queries the user can use.
            # - name
            # - analyses?

            # Apply user-specified filters.
            if license_number:
                filters.append({'key': 'license', 'operation': '==', 'value': license_number})
            elif state:
                filters.append({'key': 'state', 'operation': '==', 'value': state})

            # Query and return the docs.
            data = get_collection(
                'public/data/labs',
                desc=False,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET', 'POST'])
def lab_logs(request, org_id, format=None):
    """Get or create lab logs."""

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/logs')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create a log.
        return Response({'success': True, 'data': 'Under construction'}, content_type='application/json')


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
        return Response({'success': True, 'data': 'Under construction'}, content_type='application/json')


#------------------------------------------------------------------------------
# SCRAP
#------------------------------------------------------------------------------

# @api_view(['GET'])
# def lab(request, format=None):
#     """Get or update information about a lab."""

#     # Query labs.
#     if request.method == 'GET':
#         limit = request.query_params.get('limit', None)
#         order_by = request.query_params.get('order_by', 'state')
#         # OLDTODO: Get any filters from dict(request.query_params)
#         labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
#         return Response({'success': True, 'data': labs}, content_type='application/json')

# @api_view(['GET', 'POST'])
# def labs(request, format=None):
#     """Get or update information about labs."""

#     # Query labs.
#     if request.method == 'GET':
#         limit = request.query_params.get('limit', None)
#         order_by = request.query_params.get('order_by', 'state')
#         # OLDTODO: Get any filters from dict(request.query_params)
#         labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
#         return Response({'success': True, 'data': labs}, content_type='application/json')

#     # Update a lab given a valid Firebase token.
#     elif request.method == 'POST':

#         # Check token.
#         try:
#             claims = auth.authenticate_request(request)
#             uid = claims['uid']
#         except KeyError:
#             response = {'success': False, 'message': 'Invalid authentication.'}
#             return Response(response, content_type='application/json')

#         # OLDFIXME: Ensure that lab's can only edit their own lab.
#         return Response({'success': False, 'message': 'Not implemented yet :('}, content_type='application/json')

#         # # Get the posted lab data.
#         # lab = request.data
#         # org_id = lab['id']
#         # lab['slug'] = slugify(lab['name'])

#         # # OLDTODO: Handle adding labs.
#         # # Create uuid, latitude, and longitude, other fields?

#         # # Determine any changes.
#         # existing_data = get_document(f'labs/{org_id}')
#         # changes = []
#         # for key, after in lab:
#         #     before = existing_data[key]
#         #     if before != after:
#         #         changes.append({'key': key, 'before': before, 'after': after})

#         # # Get a timestamp.
#         # timestamp = datetime.now().isoformat()
#         # lab['updated_at'] = timestamp

#         # # Create a change log.
#         # log_entry = {
#         #     'action': 'Updated lab data.',
#         #     'type': 'change',
#         #     'created_at': lab['updated_at'],
#         #     'user': claims['uid'],
#         #     'user_name': claims['display_name'],
#         #     'user_email': claims['email'],
#         #     'photo_url': claims['photo_url'],
#         #     'changes': changes,
#         # }
#         # update_document(f'labs/{org_id}/logs/{timestamp}', log_entry)

#         # # Update the lab.
#         # update_document(f'labs/{org_id}', lab)

#         # return Response(log_entry, status=status.HTTP_201_CREATED)
