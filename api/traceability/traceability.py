"""
Traceability API Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 6/13/2021
Updated: 7/19/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with the Metrc API.
"""

# Standard imports
from json import loads

# External imports
import google.auth
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    access_secret_version,
    add_secret_version,
    create_log,
    get_document,
    update_document
)
from cannlytics.metrc import initialize_metrc
from api.auth.auth import authenticate_request #pylint: disable=import-error


AUTH_ERROR = 'Authentication failed. Please login to the console or \
    provide a valid API key in an `Authentication: Bearer <token>` \
    header.'

#-----------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------

def initialize_traceability(project_id, license_number, version_id):
    """Initialize a Metrc client.
    Optional: Figure out how to pre-initialize and save Metrc client.
    """

    # Get vendor version number.
    admin_data = get_document('admin/metrc')
    vendor_version_id = admin_data['vendor_api_key_secret']['version_id']

    # Get Vendor API key using secret manager.
    vendor_api_key = access_secret_version(
        project_id=project_id,
        secret_id='metrc_vendor_api_key',
        version_id=vendor_version_id
    )

    # Get user API key using secret manager.
    user_api_key = access_secret_version(
        project_id=project_id,
        secret_id=f'{license_number}_secret',
        version_id=version_id
    )

    track = initialize_metrc(vendor_api_key, user_api_key)
    return track

#-----------------------------------------------------------------------
# Endpoints
#-----------------------------------------------------------------------

@api_view(['GET'])
def employees(request):
    """Get employees for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    version_id = request.query_params.get('version_id')

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Make a request to the Metrc API.
    objs = track.get_employees(license_number=license_number)
    data = [obj.to_dict() for obj in objs]

    # Return the requested data.
    return Response({'data': data}, content_type='application/json')


@api_view(['GET', 'POST'])
def items(request):
    """Get, update, and delete items for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get data.
    if request.method == 'GET':
        objs = track.get_items(license_number=license_number, uid='243821')
        data = [obj.to_dict() for obj in objs]
        print('Retrieved the data:', data)
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update items.

    # TODO: Delete items.


@api_view(['GET', 'POST'])
def lab_tests(request):
    """Get lab tests for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get lab results.
    if request.method == 'GET':
        # FIXME: Get a longer list of lab results from Firestore
        objs = track.get_lab_results(uid='185436', license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # TODO: Post results


@api_view(['GET', 'POST'])
def locations(request):
    """Get, update, and delete locations for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get data.
    if request.method == 'GET':
        objs = track.get_locations(license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        print('Retrieved the data:', data)
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update locations.

    # TODO: Delete locations.


@api_view(['GET', 'POST'])
def packages(request):
    """Get, update, and delete packages for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get data.
    if request.method == 'GET':
        # FIXME: Get a longer list of packages from Firestore?
        objs = track.get_packages(license_number=license_number, start='2021-06-04', end='2021-06-05')
        try:
            data = [obj.to_dict() for obj in objs]
        except TypeError:
            data = [objs.to_dict()]
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update packages.

    # TODO: Delete packages.


@api_view(['GET', 'POST'])
def strains(request):
    """Get, update, and delete strains for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get data.
    if request.method == 'GET':
        objs = track.get_strains(license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update strains.

    # TODO: Delete strains.


@api_view(['GET', 'POST'])
def transfers(request):
    """Get, update, and delete transfers for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    version_id = request.query_params.get('version_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(project_id, license_number, version_id)

    # Get data.
    if request.method == 'GET':
        # TODO: Add filters
        # uid=''
        # transfer_type='incoming'
        # license_number=''
        # start=''
        # end=''
        # FIXME: Get transfers by specified date range? Or get longer list from Firestore.
        objs = track.get_transfers(license_number=license_number, start='2021-06-04', end='2021-06-05')
        data = [obj.to_dict() for obj in objs]
        print('Retrieved the data:', data)
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update transfers.

    # TODO: Delete transfers.


#-----------------------------------------------------------------------
# Actions
#-----------------------------------------------------------------------

def delete_license(request, *args, **argv): #pylint: disable=unused-argument
    """Delete a license from an organization's licenses."""

    # Authenticate the user.
    _, project_id = google.auth.default()
    user_claims = authenticate_request(request)
    data = loads(request.body.decode('utf-8'))
    deletion_reason = data.get('deletion_reason', 'No deletion reason.')
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('license')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Delete the license data and redact the secret.
    doc = get_document(f'organizations/{org_id}')
    existing_licenses = doc['licenses']
    licenses = []
    for license_data in existing_licenses:
        license_number = license_data['license_number']
        if license_data['license_number'] != license_number:
            licenses.append(license_data)
        else:
            add_secret_version(
                project_id,
                license_data['user_api_key_secret']['secret_id'],
                'redacted'
            )
    doc['licenses'] = licenses
    update_document(f'organizations/{org_id}', doc)

    # Create a log.
    create_log(
        ref=f'organizations/{org_id}/logs',
        claims=user_claims,
        action='License deleted.',
        log_type='traceability',
        key='delete_license',
        changes=[license_number, deletion_reason]
    )
    return JsonResponse({'status': 'success', 'message': 'License deleted.'})
