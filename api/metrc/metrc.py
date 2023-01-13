"""
Traceability API Views | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/13/2021
Updated: 1/13/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with the Metrc API.
"""
# Standard imports:
from json import loads
from typing import Optional

# External imports:
import google.auth
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports:
from cannlytics.firebase import (
    access_secret_version,
    add_secret_version,
    create_log,
    get_document,
    update_document
)
from cannlytics.metrc import initialize_metrc, Metrc
from cannlytics.metrc.models import (
    Location,
)
from cannlytics.auth.auth import authenticate_request #pylint: disable=import-error


AUTH_ERROR = 'Authentication failed. Please login to the console or \
    provide a valid API key in an `Authentication: Bearer <token>` \
    header.'
DEFAULT_STATE = 'ok'


#-----------------------------------------------------------------------
# Authentication
#-----------------------------------------------------------------------

def initialize_traceability(
        project_id: str,
        license_number: str,
        state: Optional[str] = DEFAULT_STATE,
        test: Optional[bool] = False,
        version_id: Optional[str] = 'latest',
    ) -> Metrc:
    """Initialize a Metrc client."""

    # Get vendor version number.
    admin_data = get_document('admin/metrc')
    vendor_version_id = admin_data['vendor_api_key_secret']['version_id']
    if test:
        vendor_secret_id = 'metrc_test_vendor_api_key'
    else:
        vendor_secret_id = 'metrc_vendor_api_key'

    # Get Vendor API key using secret manager.
    vendor_api_key = access_secret_version(
        project_id=project_id,
        secret_id=vendor_secret_id,
        version_id=vendor_version_id
    )

    # Get user API key using secret manager.
    user_api_key = access_secret_version(
        project_id=project_id,
        secret_id=f'{license_number}_secret',
        version_id=version_id
    )

    # Return a Metrc client.
    return initialize_metrc(
        vendor_api_key,
        user_api_key,
        logs=True,
        primary_license=license_number,
        state=state,
        test=test,
    )


def delete_license(request, *args, **argv): #pylint: disable=unused-argument
    """Delete a license from an organization's licenses."""

    # Authenticate the user.
    _, project_id = google.auth.default()
    user_claims = authenticate_request(request)

    # Get the parameters
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
    
    # Update the user's remaining licenses.
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


#-----------------------------------------------------------------------
# Facilities
#-----------------------------------------------------------------------

@api_view(['GET'])
def facilities(request: Request):
    """Get employees for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()
    

    # Get the parameters.
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get facilities from the Metrc API.
    objs = track.get_facilities()

    # Return the requested data.
    data = [obj.to_dict() for obj in objs]
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Employees
#-----------------------------------------------------------------------

@api_view(['GET'])
def employees(request: Request, employee_license: Optional[str] = None):
    """Get employees for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()
    
    # Get the parameters.
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get employees from the Metrc API.
    objs = track.get_employees(license_number=license_number)

    # Return the requested data.
    data = [obj.to_dict() for obj in objs]
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Locations
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def locations(request: Request, area_id: Optional[str] = None):
    """Get, update, and delete locations for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()

    # Get the parameters.
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get location(s) data.
    if request.method == 'GET':
        objs = track.get_locations(license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update locations.
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(Location.from_dict(item))
        if create_items:
            track.create_locations(
                [x['name'] for x in create_items],
                [x['location_type'] for x in create_items],
                license_number=license_number,
                return_obs=True
            )
        if update_items:
            track.update_locations(
                update_items,
                license_number=license_number,
                return_obs=True
            )
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete location(s).
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_location(item['id'])
        else:
            track.delete_location(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Packages
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def packages(request: Request, package_id: Optional[str] = None):
    """Get, update, and delete packages for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get package(s) data.
    # TODO: Implement queries.
    if request.method == 'GET':
        objs = track.get_packages(license_number=license_number, start='2021-06-04', end='2021-06-05')
        try:
            data = [obj.to_dict() for obj in objs]
        except TypeError:
            data = [objs.to_dict()]
        return Response({'data': data}, content_type='application/json')

    # Create / update packages.
    if request.method == 'POST':
        raise NotImplementedError
        
        # TODO: Create packages.


        # TODO: Update packages.


        # TODO: Change items.


        # TODO: Update items.


        # TODO: Finish


        # TODO: Unfinish


        # TODO: Adjust


        # TODO: Remediate


        # TODO: Update note


        # TODO: Change location


    # Delete package(s).
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_package(item['id'])
        else:
            track.delete_package(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Items
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def items(request: Request, item_id: Optional[str] = None):
    """Get, update, and delete items for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get item data.
    if request.method == 'GET':
        objs = track.get_items(license_number=license_number, uid='243821')
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update item(s).
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            track.create_items(
                create_items,
                license_number=license_number,
                return_obs=True
            )
        if update_items:
            track.update_items(
                update_items,
                license_number=license_number,
                return_obs=True
            )
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete item(s).
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_item(item['id'])
        else:
            track.delete_item(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Lab Tests
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def lab_tests(request: Request, test_id: Optional[str] = None):
    """Get lab tests for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()

    # Get the parameters.
    license_number = request.query_params.get('license')
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get lab results.
    # TODO: Implement queries.
    if request.method == 'GET':
        objs = track.get_lab_results(uid='185436', license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # TODO: Post results


#-----------------------------------------------------------------------
# Strains
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def strains(request: Request, strain_id: Optional[str] = None):
    """Get, update, and delete strains for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get strain data.
    if request.method == 'GET':
        objs = track.get_strains(license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update strains.
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            track.create_strains(
                create_items,
                license_number=license_number,
                return_obs=True
            )
        if update_items:
            track.update_strains(
                update_items,
                license_number=license_number,
                return_obs=True
            )
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete strains.
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_strain(item['id'])
        else:
            track.delete_strain(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Batches
#-----------------------------------------------------------------------

# FIXME: Implement!


#-----------------------------------------------------------------------
# Plants
#-----------------------------------------------------------------------

# FIXME: Implement!


#-----------------------------------------------------------------------
# Harvests
#-----------------------------------------------------------------------

# FIXME: Implement!


#-----------------------------------------------------------------------
# Transfers and transfer templates
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def transfers(request: Request, transfer_id: Optional[str] = None):
    """Get, update, and delete transfers for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get transfer data.
    # TODO: Implement queries.
    if request.method == 'GET':
        # TODO: Add filters
        # uid=''
        # transfer_type='incoming'
        # license_number=''
        # start=''
        # end=''
        objs = track.get_transfers(license_number=license_number, start='2021-06-04', end='2021-06-05')
        data = [obj.to_dict() for obj in objs]
        print('Retrieved the data:', data)
        return Response({'data': data}, content_type='application/json')

    # TODO: Create / update transfers.


    # TODO: Create / update transfer templates.


    # Delete transfers.
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_transfer(item['id'])
        else:
            track.delete_transfer(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Patients
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def patients(request: Request, patient_id: Optional[str] = None):
    """Get, update, and delete patients for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()

    # Get the parameters.
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get patient(s) data.
    if request.method == 'GET':
        if patient_id:
            obj = track.get_patients(patient_id, license_number=license_number)
            data = obj.to_dict()
        else:
            objs = track.get_patients(license_number=license_number)
            data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update patient(s).
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            track.create_patients(
                create_items,
                license_number=license_number,
                return_obs=True
            )
        if update_items:
            track.update_patients(
                update_items,
                license_number=license_number,
                return_obs=True
            )
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete patient(s).
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_patient(item['id'])
        else:
            track.delete_patient(data['id'])


#-----------------------------------------------------------------------
# Sales / transactions
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def sales(request: Request, strain_id: Optional[str] = None):
    """Get, update, and delete sales for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    _, project_id = google.auth.default()
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)
    if not license_number or not state:
        message = 'Body data `license` and `state` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get sales data.
    if request.method == 'GET':
        objs = track.get_receipts(license_number=license_number)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update sale(s).
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            track.create_receipts(
                create_items,
                license_number=license_number,
                return_obs=True
            )
        if update_items:
            track.update_receipts(
                update_items,
                license_number=license_number,
                return_obs=True
            )
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete (void) sale(s).
    if request.method == 'DELETE':
        data = request.data['data']
        if isinstance(data, list):
            for item in data:
                track.delete_receipt(item['id'])
        else:
            track.delete_receipt(data['id'])
        return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Waste
#-----------------------------------------------------------------------

@api_view(['GET'])
def waste(request: Request, waste_id: Optional[str] = None):
    """Get specific waste data for a given license number."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if not claims:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    _, project_id = google.auth.default()
    
    # Get the parameters.
    license_number = request.data.get('license')
    test = request.data.get('test', False)
    state = request.data.get('state', DEFAULT_STATE)

    # Initialize Metrc.
    track = initialize_traceability(
        project_id,
        license_number,
        test=test,
        state=state,
    )

    # Get all waste methods for a given license.
    if waste_id == 'methods':
        data = track.get_waste_methods(license_number=license_number)

    # Get all waste reasons for plants for a given license.
    elif waste_id == 'reasons':
        data = track.get_waste_reasons(license_number=license_number)

    # Get all waste types for harvests for a given license.
    elif waste_id == 'types':
        data = track.get_waste_types(license_number=license_number)
    
    # Handle incorrect queries.
    else:
        data = []

    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Miscellaneous
#-----------------------------------------------------------------------

# TODO: Implement API endpoints for:
# - categories
# - customer types
# - units of measure
