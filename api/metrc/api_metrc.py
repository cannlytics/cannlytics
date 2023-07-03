"""
Traceability API Views | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/13/2021
Updated: 3/25/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with the Metrc API.

TODO:

    [ ] Also update Firestore as methods are performed.

    [ ] Implement time period queries by allowing for the `start` and `end`
    to be specified by the user, then iterate over that range, day-by-day.

    [ ] Handle rate limits.
    See: <https://www.metrc.com/wp-content/uploads/2021/10/4-Metrc-Rate-Limiting-1.pdf>
    - 50 GET calls per second per facility.
    - 150 GET calls per second per vendor API key.
    - 10 concurrent GET calls per facility.
    - 30 concurrent GET calls per integrator.
"""
# Standard imports:
from datetime import date, datetime
from typing import Any, Optional

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
    get_collection,
    increment_value,
    update_document,
    update_documents,
    delete_document,
)
from cannlytics.metrc import Metrc, MetrcAPIError
from cannlytics.utils import (
    camelcase,
    camel_to_snake,
    clean_dictionary,
    clean_nested_dictionary,
    snake_case,
)

# Metrc API defaults.
AUTH_ERROR = 'Authentication failed. Please login to the console or \
provide a valid API key in an `Authentication: Bearer <token>` \
header.'
METRC_ERROR = 'Metrc API error. POST request will be retried.'
DEFAULT_STATE = 'ok'
LOG_TYPE = 'metrc'
SECRET_SETTINGS = {
    'replication': {'automatic': {}},
    'expire_time': None, # TODO: Add 1 year expiration timestamp.
}


#-----------------------------------------------------------------------
# Metrc authentication.
#-----------------------------------------------------------------------

def authorize_org(claims: dict, org_id: str) -> bool:
    """Ensure that the user is authorized to work with the organization."""
    ownership = claims.get('owner', [])
    team = claims.get('team', [])
    if isinstance(ownership, str):
        ownership = [ownership]
    if isinstance(team, str):
        team = [team]
    if org_id not in ownership + team:
        return False
    return True


def get_vendor_api_key(
        state: str,
        test: Optional[bool] = True,
        project_id: Optional[str] = None,
    ) -> str:
    """Get the Metrc vendor API key from Google Secret Manager."""
    if project_id is None:
        _, project_id = google.auth.default()
    if test:
        secret_id = f'metrc_test_vendor_api_key_{state.lower()}'
    else:
        secret_id = f'metrc_vendor_api_key_{state.lower()}'
    try:
        return access_secret_version(project_id, secret_id)
    except:
        return None
    

def get_user_api_key_data(org_id: str, license_number: Optional[str] = None):
    """Get the API key data that is valid for the license, 
    or get the 1st API key if no license is given."""
    doc, query = {}, None
    ref = f'organizations/{org_id}/metrc_user_api_keys'
    if license_number:
        query = [{
            'key': 'licenses',
            'operation': 'array_contains',
            'value': license_number
        }]
    docs = get_collection(ref, filters=query, limit=1, order_by='created_at')
    if docs:
        doc = docs[0]
    return doc

def increment_api_usage(org_id):
    """Increment organization usage."""
    iso_month = date.today().strftime('%Y-%m')
    ref = f'organizations/{org_id}/metrc_usage/{iso_month}'
    increment_value(ref, 'metrc_api_requests}')


def initialize_traceability(request: Request) -> Metrc:
    """Initialize a Metrc client by getting the Metrc user and vendor API key
    from Google Secret Manager and returning an authorized Metrc client.
    """
    # Get the user's Cannlytics API key (or Metrc user API key?).
    claims = authenticate_request(request)
    authorization = request.META['HTTP_AUTHORIZATION']
    token = authorization.split(' ').pop()
    if not token:
        return AUTH_ERROR

    # Get posted data.
    if isinstance(request.data, list):
        body = {}
    else:
        body = request.data.get('data', request.data)

    # Get the organization the user may have passed, or
    # use `cannlytics.eth` to allow Metrc user API keys directly.
    org_id = request.query_params.get('org_id', body.get('org_id'))
    if org_id is None:
        if claims is None:
            org_id = 'cannlytics.eth'
        else:
            owner = claims.get('owner', claims.get('team', []))
            if not isinstance(owner, list):
                owner = [owner]
            org_id = owner[0]

    # Ensure that the user is authorized to work with the organization.
    authorized = authorize_org(claims, org_id)
    if not authorized:
        return AUTH_ERROR

    # Get any passed license number.
    license_number = body.get('license', request.query_params.get('license'))
    
    # Get the API key data.
    key_data = get_user_api_key_data(org_id, license_number)
    if not key_data:
        print('FAILED TO FIND METRC USER API KEY DATA!')
        return AUTH_ERROR
    
    # Get the Firebase project ID.
    _, project_id = google.auth.default()

    # Get the Metrc user API key.
    secret_id = key_data.get('secret_id', '')
    metrc_user_api_key = access_secret_version(project_id, secret_id)
    if metrc_user_api_key is None:
        print('FAILED TO FIND METRC USER API KEY:', state, 'TEST:', test)
        return AUTH_ERROR

    # Get the Vendor API key from Secret Manager.
    state = key_data.get('state', 'ok')
    test = key_data.get('test', True)
    metrc_vendor_api_key = get_vendor_api_key(state, test, project_id)
    if metrc_vendor_api_key is None:
        print('FAILED TO FIND METRC VENDOR API KEY:', state, 'TEST:', test)
        return AUTH_ERROR
    
    # Increment organization usage.
    increment_api_usage(org_id)

    # Initialize and return a Metrc client.
    return Metrc(
        metrc_vendor_api_key,
        metrc_user_api_key,
        logs=True,
        primary_license=license_number,
        state=state,
        test=test,
    )


#-----------------------------------------------------------------------
# General Metrc API methods.
#-----------------------------------------------------------------------

def get_objects(
        request: Request,
        track: Metrc,
        get_method: str,
        uid: Optional[str] = '',
        **kwargs,
    ) -> Response:
    """Perform a simple `GET` request to the Metrc API."""
    # Try to get the requested items.
    try:
 
        # Get singular items.
        if uid:
            obj = getattr(track, get_method)(uid, **kwargs)
            data = obj.to_dict()

        # Get multiple items.
        else:
            objs = getattr(track, get_method)(**kwargs)
            data = [obj.to_dict() for obj in objs]

    # Return any Metric error.
    except MetrcAPIError as error:
        log_metrc_error(request, get_method, str(error))
        response = {'error': True, 'message': str(error)}
        return Response(response, status=error.response.status_code)

    # Create a log and return the data.
    log_metrc_request(request, data, 'get_objects', get_method)
    return Response({'data': data}, content_type='application/json')


def create_or_update_objects(
        request: Request,
        track: Metrc,
        create_method: str,
        update_method: str,
        return_obs: Optional[bool] = True,
        update: Optional[bool] = False,
        **kwargs,
    ) -> Response:
    """Create or update given API items."""
    create_items, update_items = [], []

    # Get the data posted.
    if isinstance(request.data, list):
        data = request.data
    else:
        data = request.data.get('data', request.data)
    if data is None:
        message = 'No data. You can pass a list of objects in the request body.'
        response = {'error': True, 'message': message}
        return Response(response, content_type='application/json')
    elif isinstance(data, dict):
        data = [data]

    # Determine if the data is being updated or deleted.
    for item in data:
        if item.get('id') or update:
            update_items.append(item)
        else:
            create_items.append(item)

    # Create items.
    if create_items:
        create_items = [
            clean_nested_dictionary(x, camelcase) for x in create_items
        ]
        try:
            create_items = getattr(track, create_method)(
                create_items,
                return_obs=return_obs,
                **kwargs,
            )
        except MetrcAPIError as error:
            log_metrc_error(request, create_method, str(error))
            response = {'error': True, 'message': str(error)}
            return Response(response, status=error.response.status_code)
        if not isinstance(create_items, list):
            create_items = [create_items]

    # Update items.
    if update_items:
        update_items = [
            clean_nested_dictionary(x, camelcase) for x in update_items
        ]
        try:
            update_items = getattr(track, update_method)(
                update_items,
                return_obs=return_obs,
                **kwargs,
            )
        except MetrcAPIError as error:
            log_metrc_error(request, update_method, str(error))
            response = {'error': True, 'message': str(error)}
            return Response(response, status=error.response.status_code)
        if not isinstance(update_items, list):
            update_items = [update_items]

    # Return all items after creating entries in Firestore.
    items = create_items + update_items
    try:
        items = [x.to_dict() for x in items]
    except:
        pass
    try:
        log_metrc_request(
            request,
            items,
            'create_or_update_objects',
            update_method,
        )
    except:
        print('Failed to create logs.')
    try:
        doc = track.primary_license
        model = create_method.replace('create_', '')
        org_id = request.query_params.get('org_id', 'cannlytics.eth')
        org_col = f'organizations/{org_id}/metrc'
        refs = [f'{org_col}/{doc}/{model}/{x["id"]}' for x in items]
        update_documents(refs, items)
    except:
        print('Failed to update data in Firestore.')
    return Response({'data': items}, content_type='application/json')


def delete_objects(
        request: Request,
        track: Metrc,
        delete_method: str,
        uid: Optional[str] = '',
    ) -> Response:
    """Delete given objects from the Metrc API."""
    # Get the data posted.
    if isinstance(request.data, list):
        data = request.data
    else:
        data = request.data.get('data', request.data)

    # Delete multiple items.
    model = delete_method.replace('delete_', '')
    org_id = request.query_params.get('org_id', 'cannlytics.eth')
    org_col = f'organizations/{org_id}/metrc'
    collection = f'{org_col}/{track.primary_license}/{model}/'
    if isinstance(data, list):
        for item in data:
            uid = item['id']
            getattr(track, delete_method)(uid)
            try:
                delete_document(f'{collection}/{uid}')
            except:
                print('Failed to delete data from Firestore.')

    # Delete singular items.
    else:
        if not uid:
            uid = data.get('id', data.get('Id'))
            if uid is None:
                message = 'UID not specified. You can append a UID to the path or pass a list of objects with `id`s in the request body.'
                response = {'error': True, 'message': message}
                return Response(response, content_type='application/json')
        getattr(track, delete_method)(uid)
        try:
            delete_document(f'{collection}/{uid}')
        except:
            print('Failed to delete data from Firestore.')

    # Create a log and return an empty success response.
    log_metrc_request(request, data, 'delete_object', delete_method)
    response = {'success': True, 'data': []}
    return Response(response, content_type='application/json')


def perform_method(request, track, data, method, **kwargs):
    """Perform a given method in the Metrc API given data."""
    # FIXME: Also update Firestore as these update.

    # Format the data.
    if isinstance(data, list):
        data = [clean_nested_dictionary(x, camelcase) for x in data]
    elif isinstance(data, dict):
        data = clean_nested_dictionary(data, camelcase)

    # Perform the action.
    try:
        objs = getattr(track, method)(data, return_obs=True, **kwargs)
    except MetrcAPIError as error:
        log_metrc_error(request, method, str(error))
        response = {'error': True, 'message': str(error)}
        return Response(response, status=error.response.status_code)

    # Return any data.
    response = {'success': True, 'data': objs}
    return Response(response, content_type='application/json')


#-----------------------------------------------------------------------
# Metrc + Firestore synchronization.
#-----------------------------------------------------------------------

def update_firestore():
    """Update Firestore when given object(s) are changed."""

    # TODO: Manipulate the data if simple change.

    # TODO: Get the data from Metrc if necessary.

    # TODO: Save the updated data to Firestore.

    raise NotImplementedError


#-----------------------------------------------------------------------
# Metrc API request logging.
#-----------------------------------------------------------------------

def log_metrc_request(
        request: Request,
        data: Any,
        key: str,
        action: str,
    ) -> None:
    """Create a log for a request to the Metrc API, including any data
    returned."""
    claims = authenticate_request(request)
    create_log(
        ref='logs/metrc/metrc_requests',
        claims=claims,
        action=action,
        log_type=LOG_TYPE,
        key=key,
        changes=[{
            'body': request.data,
            'data': data,
            'method': request.method,
            'query_params': request.query_params,
            'url': request.get_full_path(),
        }]
    )


def log_metrc_error(request: Request, key: str, action: str) -> None:
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
            'method': request.method,
            'query_params': request.query_params,
            'url': request.get_full_path(),
        }]
    )


#-----------------------------------------------------------------------
# Metrc user API key management.
#-----------------------------------------------------------------------

@api_view(['POST'])
def add_metrc_user_api_key(request: HttpRequest):
    """Add a Metrc user API key to an organization on request."""

    # Authenticate the user.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the associated organization.
    data = request.data.get('data', request.data)
    org_id = request.query_params.get('org_id', data.get('org_id'))
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
        metrc_user_api_key = data['metrc_user_api_key']
        state = data['state']
        test = data.get('test', False)
    except KeyError:
        message = 'Post data `state` and `metrc_user_api_key` are required.'
        return Response({'error': True, 'message': message}, status=403)

    # Save the key data as a secret.
    _, project_id = google.auth.default()
    prefix = metrc_user_api_key[:4]
    suffix = metrc_user_api_key[-4:]
    secret_id = f'metrc_user_api_key_{org_id}_{state}_{prefix}_{suffix}'
    try:
        create_secret(project_id, secret_id, SECRET_SETTINGS)
    except:
        pass # Secret may already be created.
    add_secret_version(project_id, secret_id, metrc_user_api_key)

    # Get all facilities and their license numbers for the key.
    try:
        metrc_vendor_api_key = get_vendor_api_key(state, test, project_id)
        track = Metrc(
            metrc_vendor_api_key,
            metrc_user_api_key,
            logs=True,
            state=state,
            test=test,
        )
        facilities = track.get_facilities()
        licenses = [x.license['number'] for x in facilities]
    except MetrcAPIError as error:
        log_metrc_error(request, 'add_metrc_api_key', str(error))
        response = {'error': True, 'message': 'Invalid user API key.'}
        return Response(response, status=error.response.status_code)

    # Redundantly save the key data so that the user can user their
    # Cannlytics API key plus an organization ID.
    authorization = request.META['HTTP_AUTHORIZATION']
    cannlytics_api_key = authorization.split(' ').pop()
    user_hash = create_hash(cannlytics_api_key, org_id)

    # Save the key data to Firestore.
    metrc_hash = create_hash(metrc_user_api_key, org_id)
    entry = {
        'id': metrc_hash,
        'created_by': user_hash,
        'created_at': datetime.now().isoformat(),
        'org_id': org_id,
        'state': state,
        'secret_id': secret_id,
        'prefix': prefix,
        'suffix': suffix,
        'licenses': licenses,
        'user': False,
        'sync': True,
    }

    # Save the data to Firestore.
    refs = [
        f'organizations/{org_id}/metrc_user_api_keys/{metrc_hash}',
        f'organizations/{org_id}/metrc_user_api_keys/{user_hash}'
    ]
    update_documents(refs, [entry, {**entry, **{'user': True}}])

    # Create an activity log and return a response.
    message = f'Metrc user API key ({prefix}...{suffix}) added in {state}.'
    create_log(
        ref=f'organizations/{org_id}/logs',
        claims=claims,
        action=message,
        log_type=LOG_TYPE,
        key='add_license',
        changes=[entry]
    )
    return JsonResponse({'success': True, 'message': message})


@api_view(['POST'])
def delete_metrc_user_api_key(request: HttpRequest):
    """Delete a Metrc user API key from an organization on request."""

    # Authenticate the user.
    _, project_id = google.auth.default()
    user_claims = authenticate_request(request)

    # Get the parameters
    data = request.data.get('data', request.data)
    deletion_reason = data.get('deletion_reason', 'No deletion reason.')
    prefix = request.query_params.get('prefix')
    suffix = request.query_params.get('suffix')
    org_id = request.query_params.get('org_id', data.get('org_id'))
    if not org_id:
        message = 'Organization, `org_id`, is required.'
        return Response({'error': True, 'message': message}, status=403)
    
    # Query the Metrc user API key data using the key's prefix and suffix.
    query = [
        {'key': 'prefix', 'operation': '==', 'value': prefix},
        {'key': 'suffix', 'operation': '==', 'value': suffix},
    ]
    ref = f'organizations/{org_id}/metrc_user_api_keys'
    match = get_collection(ref, filters=query, limit=1)
    if not match:
        message = 'Unable to identify Metrc user API key from `prefix` and `suffix`.'
        return Response({'error': True, 'message': message}, status=403)

    # Get the Metrc user API key data.
    metrc_hash = match[0]['id']
    doc_id = f'organizations/{org_id}/metrc_user_api_keys/{metrc_hash}'
    doc = get_document(doc_id)

    # Redact the secret.
    add_secret_version(project_id, doc['secret_id'], 'redacted')

    # Delete the double-entered key data.
    user_hash = doc['created_by']
    delete_document(doc_id)
    delete_document(f'organizations/{org_id}/metrc_user_api_keys/{user_hash}')

    # Create a log.
    state = doc['state']
    message = f'Metrc user API key ({prefix}...{suffix}) deleted in {state}.'
    create_log(
        ref=f'organizations/{org_id}/logs',
        claims=user_claims,
        action=message,
        log_type=LOG_TYPE,
        key='delete_license',
        changes=[deletion_reason, doc]
    )
    return JsonResponse({'success': True, 'message': message})


#-----------------------------------------------------------------------
# Syncing
#-----------------------------------------------------------------------

@api_view(['GET'])
def sync_metrc(request: Request):
    """Request for Metrc data to be synced."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)
    
    # Get the organization.
    body = request.data.get('data', request.data)
    org_id = request.query_params.get('org_id', body.get('org_id'))

    # Adjust the key data to `sync` via a cloud function.
    authorization = request.META['HTTP_AUTHORIZATION']
    cannlytics_api_key = authorization.split(' ').pop()
    user_hash = create_hash(cannlytics_api_key, org_id)
    try:
        ref = f'organizations/{org_id}/metrc_user_api_keys/{user_hash}'
        update_document(ref, {'sync': True})
    except:
        return Response({'error': True, 'message': 'Unable to sync.'}, status=403)


#-----------------------------------------------------------------------
# Facilities
#-----------------------------------------------------------------------

@api_view(['GET'])
def facilities(request: Request, facility_id: Optional[str] = ''):
    """Get facilities for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)
    try:

        # Get a specific facility.
        if facility_id:
            obj = track.get_facility(facility_id)
            data = obj.to_dict()
        
        # Get facilities from the Metrc API.
        else:
            objs = track.get_facilities()
            data = [obj.to_dict() for obj in objs]

    # Return an error if the request failed.
    except MetrcAPIError as error:
        log_metrc_error(request, 'facilities', str(error))
        response = {'error': True, 'message': str(error)}
        return Response(response, status=error.response.status_code)

    # Return the requested data.
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Employees
#-----------------------------------------------------------------------

@api_view(['GET'])
def employees(request: Request, employee_id: Optional[str] = None):
    """Get employees for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get the license number from parameters or the body.
    if license_number is None:
        license_number = request.query_params.get('license',
            request.data.get('license'))

    # Get employee(s) from the Metrc API.
    try:
        objs = track.get_employees(license_number=license_number)
    except MetrcAPIError as error:
        log_metrc_error(request, 'employees', str(error))
        response = {'error': True, 'message': str(error)}
        return Response(response, status=error.response.status_code)
    
    # If the user passes an employee ID, then only return that employee.
    if employee_id:
        for obj in objs:
            if obj.license == employee_id:
                data = obj.to_dict()
    else:
        data = [obj.to_dict() for obj in objs]

    # Return the requested data.
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Locations
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def locations(request: Request, area_id: Optional[str] = ''):
    """Get, update, and delete locations for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get location(s) data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_locations',
            uid=area_id,
            action=request.query_params.get('type', 'active'),
            license_number=track.primary_license,
        )

    # Create / update locations.
    # Optional: Standardize location creation.
    if request.method == 'POST':
        create_items, update_items = [], []
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        if isinstance(data, dict):
            data = [data]
        for item in data:
            if item.get('id'):
                update_items.append(item)
            else:
                create_items.append(item)
        if create_items:
            names = [x['name'] for x in create_items]
            types = [x['location_type_name'] for x in create_items]
            try:
                track.create_locations(names, types, return_obs=True)
            except MetrcAPIError as error:
                log_metrc_error(request, 'create_locations', str(error))
                response = {'error': True, 'message': str(error)}
                return Response(response, status=error.response.status_code)
        if update_items:
            try:
                update_items = [clean_nested_dictionary(x, camelcase) for x in update_items]
                track.update_locations(update_items, return_obs=True)
            except MetrcAPIError as error:
                log_metrc_error(request, 'update_locations', str(error))
                response = {'error': True, 'message': str(error)}
                return Response(response, status=error.response.status_code)
        items = create_items + update_items
        try:
            col = track.primary_license
            refs = [f'metrc/{col}/locations/{x.get("id", x.get("ID"))}' for x in items]
            update_documents(refs, items)
        except:
            pass
        return Response({'data': items}, content_type='application/json')

    # Delete location(s).
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_location', area_id)


#-----------------------------------------------------------------------
# Packages
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def packages(request: Request, package_id: Optional[str] = ''):
    """Get, update, and delete packages for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get package(s) data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_packages',
            uid=package_id,
            action=request.query_params.get('type', 'active'),
            label=request.query_params.get('label'),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Manage packages.
    if request.method == 'POST':

        # Get the data posted and determine the action to perform.
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        action = snake_case(request.query_params.get('action', package_id))

        # Change package locations.
        if action == 'move':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='change_package_locations')

        # Update items.
        elif action == 'change_package_items':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='change_package_items')

        # Create plant batch(es) from given package(s).
        elif action == 'create_plant_batches':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='create_plant_batches_from_packages')

        # Finish packages.
        elif action == 'finish':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='manage_packages', action='finish')

        # Unfinish packages.
        elif action == 'unfinish':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='manage_packages', action='unfinish')

        # Adjust packages.
        elif action == 'adjust':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='manage_packages', action='adjust')

        # Remediate packages.
        elif action == 'remediate':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='manage_packages', action='remediate')

        # Update note(s) for packages.
        elif action == 'update_package_notes':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='update_package_notes')

        # Create a testing package.
        elif action == 'create_testing_package':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='create_packages', testing=True)

        # Create or update packages.
        else:
            return create_or_update_objects(request, track,
                create_method='create_packages',
                update_method='update_packages',
            )


#-----------------------------------------------------------------------
# Items
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def items(request: Request, item_id: Optional[str] = ''):
    """Get, update, and delete items for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get item data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_items',
            uid=item_id,
            action=request.query_params.get('type', 'active'),
            license_number=track.primary_license,
        )

    # Create / update item(s).
    if request.method == 'POST':
        return create_or_update_objects(request, track,
            create_method='create_items',
            update_method='update_items',
        )

    # Delete item(s).
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_item', item_id)


#-----------------------------------------------------------------------
# Lab Tests
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def lab_tests(
        request: Request,
        test_id: Optional[str] = '',
        coa_id: Optional[str] = '',
    ):
    """Get lab tests for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get lab results.
    if request.method == 'GET':

        # Get a COA for a test.
        if coa_id or test_id == 'coas':
            if not coa_id:
                coa_id = request.query_params.get('id', '')
            try:
                track.get_coa(coa_id, license_number=track.primary_license)
            except MetrcAPIError as error:
                log_metrc_error(request, 'get_coa', str(error))
                response = {'error': True, 'message': str(error)}
                return Response(response, status=error.response.status_code)

        # Get test data.
        return get_objects(request, track, 'get_lab_results',
            uid=test_id,
            license_number=track.primary_license
        )

    # Post results.
    if request.method == 'POST':
        data = request.data
        if data is None:
            data = request.data.get('data')
        if isinstance(data, dict):
            data = [data]
        action = snake_case(request.query_params.get('action', test_id))

        # Release lab result(s).
        if action == 'release':
            return perform_method(request, track, data,
                method='release_lab_results')

        # Upload lab result COA(s).
        if action == 'coas':
            return perform_method(request, track, data,
                method='upload_coas')

        # Post lab results.
        else:
            return perform_method(request, track, data,
                method='post_lab_results')


#-----------------------------------------------------------------------
# Strains
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def strains(request: Request, strain_id: Optional[str] = ''):
    """Get, update, and delete strains for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get strain data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_strains',
            uid=strain_id,
            action=request.query_params.get('type', 'active'),
            license_number=track.primary_license,
        )

    # Create / update strains.
    if request.method == 'POST':
        return create_or_update_objects(request, track,
            create_method='create_strains',
            update_method='update_strains',
        )

    # Delete strains.
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_strain', strain_id)


#-----------------------------------------------------------------------
# Batches
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def batches(request: Request, batch_id: Optional[str] = ''):
    """Manage plant batches for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get batch(es) data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_batches',
            uid=batch_id,
            action=request.query_params.get('type', 'active'),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Manage batch(es).
    if request.method == 'POST':
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        action = snake_case(request.query_params.get('action', batch_id))

        # Add additives.
        if action == 'add_additives':
            return perform_method(request, track, data,
                method='add_batch_additives')

        # Create plant package from a batch.
        elif action == 'create_plant_package':
            return perform_method(request, track, data,
                method='create_plant_package_from_batch')

        # Destroy plants.
        elif action == 'destroy_plants':
            return perform_method(request, track, data,
                method='destroy_batch_plants')

        # Flower batch.
        elif action == 'flower':
            return perform_method(request, track, data,
                method='change_batch_growth_phase')
        
        # Move batch.
        elif action == 'move':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='move_batches')

        # Split batch(es).
        elif action == 'split':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='split_batches')

        # Create plant batches (create plantings).
        else:
            return create_or_update_objects(request, track,
                create_method='create_plant_batches',
                update_method='create_plant_batches',
            )


#-----------------------------------------------------------------------
# Plants
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def plants(request: Request, plant_id: Optional[str] = ''):
    """Get, update, and delete plants for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get plant(s) data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_plants',
            uid=plant_id,
            label=request.query_params.get('label'),
            action=request.query_params.get('type', 'vegetative'),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Manage plant(s).
    if request.method == 'POST':
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        action = snake_case(request.query_params.get('action', plant_id))

        # Create plant package(s).
        if action == 'create_plant_packages':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='create_plant_packages')
    
        # Flower plant(s).
        elif action == 'flower':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='flower_plants')

        # Harvest plant(s).
        elif action == 'harvest':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='harvest_plants')

        # Manicure plant(s).
        elif action == 'manicure':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='manicure_plants')

        # Move plant(s).
        elif action == 'move':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='move_plants')

        # Add additive(s).
        elif action == 'add_additives':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='add_plant_additives')

        # Create plant(s).
        else:
            return create_or_update_objects(request, track,
                create_method='create_plants',
                update_method=None,
            )

    # Delete plant(s).
    if request.method == 'DELETE':
        return delete_objects(request, track, 'destroy_plants', plant_id)


#-----------------------------------------------------------------------
# Harvests
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def harvests(request: Request, harvest_id: Optional[str] = ''):
    """Manage harvests for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get harvests.
    if request.method == 'GET':
        return get_objects(request, track, 'get_harvests',
            uid=harvest_id,
            action=request.query_params.get('type', 'active'),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Manage harvest(s).
    if request.method == 'POST':
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        action = snake_case(request.query_params.get('action', harvest_id))

        # Finish harvest(s).
        if action == 'finish':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='finish_harvests')
    
        # Unfinish harvest(s).
        elif action == 'unfinish':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='unfinish_harvests')

        # Remove waste from harvest(s).
        elif action == 'remove_waste':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='remove_waste')

        # Move harvest(s).
        elif action == 'move':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='move_harvests')

        # Create harvest packages.
        elif action == 'create_packages':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='create_harvest_packages')

        # Create harvest testing packages
        elif action == 'create_testing_packages':
            if isinstance(data, dict): data = [data]
            return perform_method(request, track, data,
                method='create_harvest_testing_packages')

        # Otherwise return an error.
        message = 'Updating harvests requires you to pass a `action` parameter.'
        response = {'error': True, 'message': message}
        return Response(response, content_type='application/json')


#-----------------------------------------------------------------------
# Transfers, transporters, and transfer templates
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def transfers(request: Request, transfer_id: Optional[str] = ''):
    """Get, update, and delete transfers for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get transfer data.
    if request.method == 'GET':

        # FIXME: Implement:
            # - /transfers/v1/delivery/package/{id}/requiredlabtestbatches
            # - /transfers/v1/delivery/{id}/packages/wholesale
            # - /transfers/v1/delivery/{id}/packages

        # Get transfer packages.
        # action = snake_case(request.query_params.get('action', transfer_id))
        if transfer_id == 'packages':
            action = request.query_params.get('type', 'packages')
            if action == 'wholesale':
                action = 'packages/wholesale'
            elif action == 'testing':
                action = 'requiredlabtestbatches'
            return perform_method(request, track, transfer_id,
                'get_transfer_packages', action=action)
        

        # Otherwise get transfers.
        return get_objects(request, track, 'get_transfers',
            uid=transfer_id,
            transfer_type=request.query_params.get('type', 'incoming'),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Create / update transfers.
    # FIXME: Updating transfers causes an error if returning data.
    if request.method == 'POST':
        return create_or_update_objects(request, track,
                create_method='create_transfers',
                update_method='update_transfers',
                return_obs=False, 
            )

    # Delete transfers.
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_transfer', transfer_id)


@api_view(['GET', 'POST', 'DELETE'])
def transfer_templates(request: Request, template_id: Optional[str] = ''):
    """Get, update, and delete transfer templates for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get data.
    if request.method == 'GET':
        return get_objects(request, track, 'get_transfer_templates',
            uid=template_id,
            action=request.query_params.get('type', ''),
            start=request.query_params.get('start'),
            end=request.query_params.get('end'),
            license_number=track.primary_license,
        )

    # Create / update data.
    if request.method == 'POST':
        return create_or_update_objects(request, track,
            create_method='create_transfer_templates',
            update_method='update_transfer_templates',
        )

    # Delete data.
    if request.method == 'DELETE':
        return delete_objects(
            request,
            track,
            'delete_transfer_template',
            template_id
        )


@api_view(['GET'])
def drivers(request: Request, driver_id: Optional[str] = ''):
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
def vehicles(request: Request, driver_id: Optional[str] = ''):
    """Get transporters and transporter details for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get the details of the transporter driver and vehicle.
    obj = track.get_transporter_details(driver_id)
    data = obj.to_dict()
    return Response({'data': data}, content_type='application/json')


#-----------------------------------------------------------------------
# Patients
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def patients(request: Request, patient_id: Optional[str] = ''):
    """Get, update, and delete patients for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get patient(s) data.
    if request.method == 'GET':
        params = request.query_params

        # Get patient registration locations.
        if patient_id == 'locations':
            try:
                objs = track.get_patient_registration_locations()
            except MetrcAPIError as error:
                log_metrc_error(request, 'get_patient_registration_locations', str(error))
                response = {'error': True, 'message': str(error)}
                return Response(response, status=error.response.status_code)
            try:
                objs = [clean_dictionary(x, camel_to_snake) for x in objs]
            except:
                pass
            return Response({'data': objs}, content_type='application/json')
        
        # Get patient data.
        return get_objects(request, track, 'get_patients', 
            uid=patient_id,
            action=params.get('type', 'active'),
            license_number=track.primary_license,
        )

    # Create / update patient(s).
    if request.method == 'POST':
        # FIXME: Handle `update_patients`.
        return create_or_update_objects(request, track,
            create_method='create_patients',
            update_method='update_patients',
        )

    # Delete patient(s).
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_patient', patient_id)


#-----------------------------------------------------------------------
# Sales / transactions
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def sales(request: Request, sale_id: Optional[str] = ''):
    """Get, update, and delete sales for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get sales data.
    if request.method == 'GET':
        params = request.query_params
        return get_objects(request, track, 'get_receipts', 
            uid=sale_id,
            action=params.get('type', 'active'),
            start=params.get('start'),
            end=params.get('end'),
            sales_start=params.get('sales_start', params.get('salesStart')),
            sales_end=params.get('sales_end', params.get('salesEnd')),
            license_number=track.primary_license,
        )

    # Create / update sale(s).
    if request.method == 'POST':
        return create_or_update_objects(request, track,
            create_method='create_receipts',
            update_method='update_receipts',
        )

    # Delete (void) sale(s).
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_receipt', sale_id)


@api_view(['GET', 'POST', 'DELETE'])
def transactions(
        request: Request,
        start: Optional[str] = '',
        end: Optional[str] = '',
    ):
    """Get, create, and update transactions for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get transactions data.
    if request.method == 'GET':
        params = request.query_params
        return get_objects(request, track, 'get_transactions', 
            start=params.get('start', start),
            end=params.get('end', end),
            license_number=track.primary_license,
        )

    # Create / update transaction(s).
    if request.method == 'POST':
        update = False
        if request.query_params.get('action') == 'update':
            update = True
        return create_or_update_objects(request, track,
            create_method='create_transactions',
            update_method='update_transactions',
            update=update,
            date=request.query_params.get('date', start),
        )


#-----------------------------------------------------------------------
# Deliveries
#-----------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def deliveries(request: Request, delivery_id: Optional[str] = ''):
    """Get, update, and delete deliveries for a given license number."""

    # Initialize Metrc.
    track = initialize_traceability(request)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get deliveries data.
    if request.method == 'GET':
        params = request.query_params
        return get_objects(request, track, 'get_deliveries',
            uid=delivery_id,
            action=params.get('type', 'active'),
            start=params.get('start'),
            end=params.get('end'),
            sales_start=params.get('sales_start'),
            sales_end=params.get('sales_end'),
            license_number=track.primary_license,
        )

    # Manage deliveries.
    if request.method == 'POST':
        if isinstance(request.data, list):
            data = request.data
        else:
            data = request.data.get('data', request.data)
        action = snake_case(request.query_params.get('action', delivery_id))

        # Complete deliveries.
        if action == 'complete':
            return perform_method(request, track, data,
                method='complete_deliveries')
        
        # TODO: depart, restock, deliver, end

        # Create / update deliveries.
        else:
            return create_or_update_objects(request, track,
                create_method='create_deliveries',
                update_method='update_deliveries',
            )

    # Delete deliveries.
    if request.method == 'DELETE':
        return delete_objects(request, track, 'delete_delivery', delivery_id)


#-----------------------------------------------------------------------
# Types
#-----------------------------------------------------------------------

def get_metrc_types(
        request: Request,
        method: str,
        license_number: Optional[str] = '',
    ):
    """Get metadata for the possible types of the given `method`."""
    # Initialize Metrc.
    track = initialize_traceability(request, license_number)
    if isinstance(track, str):
        return Response({'error': True, 'message': track}, status=403)

    # Get data from the Metrc API.
    try:
        objs = getattr(track, method)()
    except MetrcAPIError as error:
        log_metrc_error(request, method, str(error))
        response = {'error': True, 'message': str(error)}
        return Response(response, status=error.response.status_code)

    # Return the requested data.
    try:
        data = [obj.to_dict() for obj in objs]
    except AttributeError:
        data = objs
    try:
        data = [clean_dictionary(x, camel_to_snake) for x in data]
    except AttributeError:
        pass
    return Response({'data': data}, content_type='application/json')


@api_view(['GET'])
def additive_types(request: Request, license_number: Optional[str] = ''):
    """Get additive types for a given license number."""
    return get_metrc_types(request, 'get_additive_types', license_number)


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


@api_view(['GET'])
def growth_phases(request: Request, license_number: Optional[str] = ''):
    """Get growth phases for a given license number."""
    return get_metrc_types(request, 'get_growth_phases', license_number)
