"""
Traceability API Views | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/13/2021
Updated: 1/15/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with the Metrc API.

TODO: Implement the remaining functionality:

    [ ] Packages
    [ ] Lab Tests
    [ ] Plants
    [ ] Harvests
    [ ] Transfers
    [ ] Deliveries

    [ ] Logs
    
    [ ] Rate limits
    <https://www.metrc.com/wp-content/uploads/2021/10/4-Metrc-Rate-Limiting-1.pdf>
    - 50 GET calls per second per facility.
    - 150 GET calls per second per vendor API key.
    - 10 concurrent GET calls per facility.
    - 30 concurrent GET calls per integrator.

"""
# Standard imports:
from json import loads
from typing import Optional

# External imports:
import google.auth
from django.http.response import JsonResponse
from django.http.request import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports:
from cannlytics.auth.auth import authenticate_request
from cannlytics.data import create_hash
from cannlytics.firebase import (
    access_secret_version,
    add_secret_version,
    create_log,
    create_secret,
    get_document,
    update_document
)
from cannlytics.metrc import (
    Metrc,
    MetrcAPIError,
    Location,
)

# Metrc API defaults.
AUTH_ERROR = 'Authentication failed. Please login to the console or \
    provide a valid API key in an `Authentication: Bearer <token>` \
    header.'
METRC_ERROR = 'Metrc API error. POST request will be retried.'
DEFAULT_STATE = 'ok'
LOG_TYPE = 'metrc'


#-----------------------------------------------------------------------
# License and Metrc user API key management
#-----------------------------------------------------------------------

def add_license(request: HttpRequest):
    """Add a license to an organization's licenses on request."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    
    # Get the associated organization.
    org_id = request.query_params.get('org_id')
    if org_id is None:
        message = 'Parameter `org_id` is required.'
        return Response({'error': True, 'message': message}, status=403)

    # Ensure that the user is the owner of the organization.
    owner = claims.get('owner', [])
    if not isinstance(owner, list):
        owner = [owner]
    if org_id not in owner:
        message = 'You are not the owner of this organization.'
        return Response({'error': True, 'message': message}, status=403)

    # Get the license, state, and Metrc user API key.
    try:
        data = loads(request.body.decode('utf-8'))
        metrc_user_api_key = data['metrc_user_api_key']
        license_number = data['license_number']
        license_type = data.get('license_type')
        state = data['state']
    except KeyError:
        message = 'Body data `license_number`, `state`, and `metrc_user_api_key` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Save the key data as a secret.
    _, project_id = google.auth.default()   
    secret_id = create_secret(
        project_id, 
        f'metrc_user_api_key_{org_id}_{state}_{license_number}',
        metrc_user_api_key,
    )

    # Save the key data to Firestore for admin.
    code = create_hash(metrc_user_api_key)
    ref = f'admin/metrc/user_api_key_hmacs/{code}'
    entry = {
        'license_number': license_number,
        'license_type': license_type,
        'org_id': org_id,
        'state': state,
        'secret_id': secret_id,
    }
    update_document(ref, entry)

    # Save the license data to Firestore, for the user to manage.
    doc = get_document(f'organizations/{org_id}')
    existing_licenses = doc['licenses']
    licenses = [{
        'license_number': license_number,
        'license_type': license_type,
        'state': state,
        'user_api_key_secret': {
            'project_id': project_id,
            'secret_id': secret_id,
            'version_id': '1'
        },
    }]
    for license_data in existing_licenses:
        if license_data['license_number'] != license_number:
            licenses.append(license_data)

    # Update the organization's licenses.
    doc['licenses'] = licenses
    update_document(f'organizations/{org_id}', doc)

    # Redundantly save the key data so that the user can user their
    # Cannlytics API key plus a license number.
    authorization = request.META['HTTP_AUTHORIZATION']
    cannlytics_api_key = authorization.split(' ').pop()
    code = create_hash(cannlytics_api_key)
    ref = f'admin/metrc/user_api_key_hmacs/{code}'
    update_document(ref, {project_id: True, 'licenses': licenses})

    # Create an activity log and return a response.
    message = f'License {license_number} added in {state}.'
    create_log(
        ref=f'organizations/{org_id}/logs',
        claims=claims,
        action=message,
        log_type=LOG_TYPE,
        key='add_license',
        changes=[license_number]
    )
    return JsonResponse({'success': True, 'message': message})


def delete_license(request: HttpRequest):
    """Delete a license from an organization's licenses on request."""

    # Authenticate the user.
    _, project_id = google.auth.default()
    user_claims = authenticate_request(request)

    # Get the parameters
    data = loads(request.body.decode('utf-8'))
    deletion_reason = data.get('deletion_reason', 'No deletion reason.')
    license_number = request.query_params.get('license')
    org_id = request.query_params.get('org_id')
    if not license_number or not org_id:
        message = 'Parameters `license` and `org_id` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Delete the license data and redact the secret.
    doc = get_document(f'organizations/{org_id}')
    existing_licenses = doc['licenses']
    licenses = []
    for license_data in existing_licenses:
        if license_data['license_number'] != license_number:
            licenses.append(license_data)
        else:
            add_secret_version(
                project_id,
                license_data['secret_id'],
                'redacted'
            )

    # Update the user's remaining licenses.
    doc['licenses'] = licenses
    update_document(f'organizations/{org_id}', doc)

    # Update admin documents.
    authorization = request.META['HTTP_AUTHORIZATION']
    cannlytics_api_key = authorization.split(' ').pop()
    code = create_hash(cannlytics_api_key)
    ref = f'admin/metrc/user_api_key_hmacs/{code}'
    update_document(ref, {project_id: True, 'licenses': licenses})

    # Create a log.
    message = f'License {license_number} deleted.'
    create_log(
        ref=f'organizations/{org_id}/logs',
        claims=user_claims,
        action=message,
        log_type=LOG_TYPE,
        key='delete_license',
        changes=[license_number, deletion_reason]
    )
    return JsonResponse({'success': True, 'message': message})


#-----------------------------------------------------------------------
# Authentication
#-----------------------------------------------------------------------

def initialize_traceability(
        request: Request,
        license_number: Optional[str] = None,
        version_id: Optional[str] = 'latest',
    ) -> Metrc:
    """Initialize a Metrc client by getting the vendor API key
    from Google Secret Manager and returning an authorized Metrc client.
    """
    # Get the user's Cannlytics or Metrc user API key.
    authorization = request.META['HTTP_AUTHORIZATION']
    user_api_key = authorization.split(' ').pop()
    if not user_api_key:
        return AUTH_ERROR

    # Check if the user or Metrc user API key are known.
    code = create_hash(user_api_key)
    key_data = get_document(f'admin/metrc/user_api_key_hmacs/{code}')
    if key_data is None:
        return AUTH_ERROR
    
    # Get the user's Metrc user API key if they are using a Cannlytics
    # API key, using the 1st license or by license number if provided.
    _, project_id = google.auth.default()
    license_data = None
    if key_data.get(project_id):
        license_number = body.get('license')
        if license_number is None:
            license_data = key_data['licenses'][0]
        else:
            for license_data in key_data['licenses']:
                if license_data['license_number'] == license_number:
                    break
        if license_data is None:
            return AUTH_ERROR
        secret_id = license_data['secret_id']
        user_api_key = access_secret_version(project_id, secret_id)
        if user_api_key is None:
            return AUTH_ERROR

    # Get the parameters for the client.
    body = request.data['data']
    if license_number is None:
        license_number = body.get('license', key_data.get('license_number'))
    if license_data:
        test = license_data['test']
        state = license_data['state']
    else:
        test = body.get('test', False)
        state = body.get('state', DEFAULT_STATE)

    # Get the Vendor API key from Secret Manager.
    if test:
        vendor_secret_id = 'metrc_test_vendor_api_key'
    else:
        vendor_secret_id = 'metrc_vendor_api_key'
    vendor_api_key = access_secret_version(
        project_id=project_id,
        secret_id=vendor_secret_id,
        version_id=version_id
    )

    # Initialize and return a Metrc client.
    return Metrc(
        vendor_api_key,
        user_api_key,
        logs=True,
        primary_license=license_number,
        state=state,
        test=test,
    )


def log_metrc_error(request, action, key):
    """Create a log for a Metrc API request error so that the request
    can be retried."""
    claims = authenticate_request(request)
    create_log(
        ref='logs/metrc/metrc_errors',
        claims=claims,
        action=action,
        log_type=LOG_TYPE,
        key=key,
        changes=[{
            'body': request.data,
            'query_params': request.query_params,
            'url': request.get_full_path(),
        }]
    )


#-----------------------------------------------------------------------
# API Methods
#-----------------------------------------------------------------------

def create_or_update_objects(track, data, create_method, update_method):
    """Create or update given API items."""
    create_items, update_items = [], []
    for item in data:
        if item.get('id'):
            update_items.append(item)
        else:
            create_items.append(item)
    if create_items:
        getattr(track, create_method)(create_items, return_obs=True)
    if update_items:
        getattr(track, update_method)(update_items, return_obs=True)
    items = create_items + update_items
    return Response({'data': items}, content_type='application/json')


def delete_objects(track, data, delete_method):
    """Delete given objects from the Metrc API."""
    if isinstance(data, list):
        for item in data:
            getattr(track, delete_method)(item['id'])
    else:
        getattr(track, delete_method)(data['id'])
    return Response({'success': True, 'data': []}, content_type='application/json')


#-----------------------------------------------------------------------
# Facilities
#-----------------------------------------------------------------------

@api_view(['GET'])
def facilities(request: Request, license_number: Optional[str] = ''):
    """Get facilities for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request, license_number=license_number)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get facilities from the Metrc API.
    try:
        objs = track.get_facilities()
    except MetrcAPIError:
        log_metrc_error(request, track, 'facilities')
        return Response({'error': True, 'message': METRC_ERROR}, status=403)

    # Return the requested data.
    data = [obj.to_dict() for obj in objs]
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Employees
#-----------------------------------------------------------------------

@api_view(['GET'])
def employees(request: Request, license_number: Optional[str] = ''):
    """Get employees for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get employees from the Metrc API.
    try:
        objs = track.get_employees(license_number=license_number)
    except MetrcAPIError:
        log_metrc_error(request, track, 'employees')
        return Response({'error': True, 'message': METRC_ERROR}, status=403)

    # Return the requested data.
    data = [obj.to_dict() for obj in objs]
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Locations
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def locations(request: Request, area_id: Optional[str] = None):
    """Get, update, and delete locations for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get location(s) data.
    if request.method == 'GET':
        objs = track.get_locations()
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
        # FIXME: Standardize location creation.
        if create_items:
            names = [x['name'] for x in create_items]
            types = [x['location_type'] for x in create_items]
            track.create_locations(names, types, return_obs=True)
        if update_items:
            track.update_locations(update_items, return_obs=True)
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
def packages(
        request: Request,
        package_id: Optional[str] = None,
    ):
    """Get, update, and delete packages for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get package(s) data.
    # TODO: Implement queries.
    if request.method == 'GET':
        objs = track.get_packages(
            # start='2021-06-04',
            # end='2021-06-05'
        )
        try:
            data = [obj.to_dict() for obj in objs]
        except TypeError:
            data = [objs.to_dict()]
        return Response({'data': data}, content_type='application/json')

    # Manage packages.
    if request.method == 'POST':

        # Determine the action to perform.
        data = request.data['data']
        # action = request.data.get('action')
        
        # TODO: Change package locations.
        if package_id == 'change_package_locations':
            raise NotImplementedError


        # TODO: Update items.


        # TODO: Finish


        # TODO: Unfinish


        # TODO: Adjust


        # TODO: Remediate


        # TODO: Update note


        # TODO: Change location

        # Create or update packages.
        else:
            return create_or_update_objects(track, data,
                create_method='create_packages',
                update_method='update_packages',
            )

    # Delete package(s).
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_package')

#-----------------------------------------------------------------------
# Items
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def items(request: Request, item_id: Optional[str] = None):
    """Get, update, and delete items for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get item data.
    if request.method == 'GET':
        objs = track.get_items(uid=item_id)
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update item(s).
    if request.method == 'POST':
        return create_or_update_objects(track, data,
            create_method='create_items',
            update_method='update_items',
        )

    # Delete item(s).
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_item')


#-----------------------------------------------------------------------
# Lab Tests
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def lab_tests(request: Request, test_id: Optional[str] = None):
    """Get lab tests for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get lab results.
    # TODO: Implement queries.
    if request.method == 'GET':
        objs = track.get_lab_results(uid='185436')
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # FIXME: Post results
    if request.method == 'POST':
        raise NotImplementedError

        # TODO: Post lab results.


        # TODO: Upload lab result CoA(s).


        # TODO: Release lab result(s).


#-----------------------------------------------------------------------
# Strains
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def strains(request: Request, strain_id: Optional[str] = None):
    """Get, update, and delete strains for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get strain data.
    if request.method == 'GET':
        objs = track.get_strains()
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update strains.
    if request.method == 'POST':
        return create_or_update_objects(track, data,
            create_method='create_strains',
            update_method='update_strains',
        )

    # Delete strains.
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_strain')


#-----------------------------------------------------------------------
# Batches
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def batches(request: Request, batch_id: Optional[str] = None):
    """Manage plant batches for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get batch(es) data.
    if request.method == 'GET':
        if batch_id:
            obj = track.get_batches(batch_id)
            data = obj.to_dict()
        else:
            objs = track.get_batches()
            data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Manage batch(es).
    if request.method == 'POST':
        raise NotImplementedError

        # TODO: Create plant batches.

        # TODO: Manage batches:
        # - Split batch(es).
        # - Create plant package(s)
        # - Move batch(es).
        # - Add additives.
        # - Create plantings.

        # TODO: Implement additives.


#-----------------------------------------------------------------------
# Plants
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def plants(request: Request, plant_id: Optional[str] = None):
    """Get, update, and delete plants for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get plant(s) data.
    if request.method == 'GET':
        if plant_id:
            obj = track.get_plants(plant_id)
            data = obj.to_dict()
        else:
            objs = track.get_plants()
            data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Manage plant(s).
    if request.method == 'POST':
        raise NotImplementedError

        # TODO: Create plant(s).


        # TODO: Create plant package(s).


        # TODO: Manicure plant(s).


        # TODO: Harvest plant(s).


        # TODO: Move plant(s).


        # TODO: Flower plant(s).


    # Delete plant(s).
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'destroy_plants')


#-----------------------------------------------------------------------
# Harvests
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def harvests(request: Request, harvest_id: Optional[str] = None):
    """Manage harvests for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get harvests.
    if request.method == 'GET':
        if harvest_id:
            obj = track.get_harvests(harvest_id)
            data = obj.to_dict()
        else:
            objs = track.get_harvests()
            data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Manage harvest(s).
    if request.method == 'POST':
        raise NotImplementedError

        # TODO: Finish harvest(s).


        # TODO: Unfinish harvest(s).


        # TODO: Remove waste from  harvest(s).


        # TODO: Move harvest(s).


#-----------------------------------------------------------------------
# Transfers, transporters, and transfer templates
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def transfers(request: Request, transfer_id: Optional[str] = None):
    """Get, update, and delete transfers for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get transfer data.
    # TODO: Implement queries.
    if request.method == 'GET':
        # TODO: Add filters
        # uid=''
        # transfer_type='incoming'
        # license_number=''
        # start=''
        # end=''
        objs = track.get_transfers(start='2021-06-04', end='2021-06-05')
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # FIXME: Create / update transfers.


    # TODO: Create / update transfer templates.


    # Delete transfers.
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_transfer')


@api_view(['GET'])
def drivers(request: Request, driver_id: Optional[str] = None):
    """Get transporters and transporter details for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get the data for a transporter.
    obj = track.get_transporters(driver_id)
    data = obj.to_dict()
    return Response({'data': data}, content_type='application/json')


@api_view(['GET'])
def vehicles(request: Request, driver_id: Optional[str] = None):
    """Get transporters and transporter details for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get the details of the transporter driver and vehicle.
    obj = track.get_transporter_details(driver_id)
    data = obj.to_dict()
    return Response({'data': data}, content_type='application/json')


# TODO: Implement transfer template endpoint for methods:
# `get_transfer_templates`
# `create_transfer_templates`
# `update_transfer_templates`
# `delete_transfer_template`


#-----------------------------------------------------------------------
# Patients
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def patients(request: Request, patient_id: Optional[str] = None):
    """Get, update, and delete patients for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get patient(s) data.
    if request.method == 'GET':
        if patient_id:
            obj = track.get_patients(patient_id)
            data = obj.to_dict()
        else:
            objs = track.get_patients()
            data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update patient(s).
    if request.method == 'POST':
        return create_or_update_objects(track, data,
            create_method='create_patients',
            update_method='update_patients',
        )

    # Delete patient(s).
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_patient')


#-----------------------------------------------------------------------
# Sales / transactions
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def sales(request: Request, strain_id: Optional[str] = None):
    """Get, update, and delete sales for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get sales data.
    if request.method == 'GET':
        objs = track.get_receipts()
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
            track.create_receipts(create_items, return_obs=True)
        if update_items:
            track.update_receipts(update_items, return_obs=True)
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # Delete (void) sale(s).
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_receipt')


#-----------------------------------------------------------------------
# Deliveries
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def deliveries(request: Request, delivery_id: Optional[str] = None):
    """Get, update, and delete deliveries for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get deliveries data.
    if request.method == 'GET':
        objs = track.get_deliveries()
        data = [obj.to_dict() for obj in objs]
        return Response({'data': data}, content_type='application/json')

    # Create / update deliveries.
    if request.method == 'POST':
        create_items, update_items = [], []
        data = request.data['data']
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            track.create_deliveries(create_items, return_obs=True)
        if update_items:
            track.update_deliveries(update_items, return_obs=True)
        items = create_items + update_items
        return Response({'data': items}, content_type='application/json')

    # TODO: Complete deliveries.

    # TODO: get_return_reasons

    # Delete deliveries.
    if request.method == 'DELETE':
        data = request.data['data']
        return delete_objects(track, data, 'delete_delivery')


#-----------------------------------------------------------------------
# Miscellaneous
#-----------------------------------------------------------------------

def get_metrc_types(
        request: Request,
        method: str,
        license_number: Optional[str] = '',
    ):
    # Initialize Metrc.
    track = initialize_traceability(request, license_number)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get data from the Metrc API.
    try:
        objs = getattr(track, method)()
    except MetrcAPIError:
        log_metrc_error(request, track, method)
        return Response({'error': True, 'message': METRC_ERROR}, status=403)

    # Return the requested data.
    try:
        data = [obj.to_dict() for obj in objs]
    except AttributeError:
        data = objs
    return Response({'data': data}, content_type='application/json')


@api_view(['GET'])
def adjustment_reasons(request: Request, license_number: Optional[str] = ''):
    """Get package adjustment reasons for a given license number."""
    return get_metrc_types(request, 'get_adjustment_reasons', license_number)


@api_view(['GET'])
def batch_types(request: Request, license_number: Optional[str] = ''):
    """Get batch types for a given license number."""
    return get_metrc_types(request, 'get_batch_types', license_number)


@api_view(['GET'])
def categories(request: Request, license_number: Optional[str] = ''):
    """Get categories for a given license number."""
    return get_metrc_types(request, 'get_item_categories', license_number)


@api_view(['GET'])
def customer_types(request: Request, license_number: Optional[str] = ''):
    """Get customer types for a given license number."""
    return get_metrc_types(request, 'get_customer_types', license_number)


@api_view(['GET'])
def location_types(request: Request, license_number: Optional[str] = ''):
    """Get location types for a given license number."""
    return get_metrc_types(request, 'get_location_types', license_number)


@api_view(['GET'])
def package_statuses(request: Request, license_number: Optional[str] = ''):
    """Get package statuses for a given license number."""
    return get_metrc_types(request, 'get_package_statuses', license_number)


@api_view(['GET'])
def package_types(request: Request, license_number: Optional[str] = ''):
    """Get package types for a given license number."""
    return get_metrc_types(request, 'get_package_types', license_number)


@api_view(['GET'])
def return_reasons(request: Request, license_number: Optional[str] = ''):
    """Get return reasons for a given license number."""
    return get_metrc_types(request, 'get_return_reasons', license_number)


@api_view(['GET'])
def test_statuses(request: Request, license_number: Optional[str] = ''):
    """Get test statuses for a given license number."""
    return get_metrc_types(request, 'get_test_statuses', license_number)


@api_view(['GET'])
def test_types(request: Request, license_number: Optional[str] = ''):
    """Get test types for a given license number."""
    return get_metrc_types(request, 'get_test_types', license_number)


@api_view(['GET'])
def transfer_types(request: Request, license_number: Optional[str] = ''):
    """Get transfer types for a given license number."""
    return get_metrc_types(request, 'get_transfer_types', license_number)


@api_view(['GET'])
def units(request: Request, license_number: Optional[str] = ''):
    """Get units of measure for a given license number."""
    return get_metrc_types(request, 'get_units_of_measure', license_number)


@api_view(['GET'])
def waste_methods(request: Request, license_number: Optional[str] = ''):
    """Get waste methods for a given license number."""
    return get_metrc_types(request, 'get_waste_methods', license_number)


@api_view(['GET'])
def waste_reasons(request: Request, license_number: Optional[str] = ''):
    """Get waste reasons for a given license number."""
    return get_metrc_types(request, 'get_waste_reasons', license_number)


@api_view(['GET'])
def waste_types(request: Request, license_number: Optional[str] = ''):
    """Get waste types for a given license number."""
    return get_metrc_types(request, 'get_waste_types', license_number)
