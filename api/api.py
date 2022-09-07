"""
API Functions | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/7/2021
Updated: 12/27/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory data models.
"""
# Standard imports.
from datetime import datetime
from json import loads
from re import sub
from typing import Any, Callable, Dict, Tuple

# External imports.
from rest_framework.response import Response

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    add_to_array,
    create_log,
    delete_document,
    get_collection,
    get_document,
    update_document,
)

BASE = 'https://cannlytics.com/api'
ENDPOINTS = [
    'analyses',
    'analytes',
    'areas',
    'auth',
    'certificates',
    'contacts',
    'data',
    'instruments',
    'inventory',
    'invoices',
    'measurements',
    'organizations',
    'projects',
    'results',
    'samples',
    'settings',
    'stats',
    'traceability',
    'transfers',
    'users',
    'waste',
]
VERSION = 'v1'


#------------------------------------------------------------------------------
# API Logic
#------------------------------------------------------------------------------

def delete_object(
        request: Response,
        claims: Dict[str, Any],
        model_id: str,
        model_type: str,
        model_type_singular: str,
        organization_id: str,
) -> bool:
    """Delete an object through the API.
    Parse the data. Check that the user is an owner or quality assurance.
    Delete by URL ID if given. Otherwise delete by using posted ID(s).
    """
    quality_control = claims.get('qc', '')
    owner = claims.get('owner', '')
    data = loads(request.body.decode('utf-8'))
    if organization_id not in quality_control and organization_id not in owner:
        return False
    if model_id:
        delete_document(f'organizations/{organization_id}/{model_type}/{model_id}')
        create_log(
            f'organizations/{organization_id}/logs',
            claims,
            f'{model_type.title()} deleted.',
            model_type, 
            model_id, 
            [data]
        )
    else:
        if isinstance(data, dict):
            doc_id = data[f'{model_type_singular}_id']
            delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
            create_log(
                f'organizations/{organization_id}/logs',
                claims,
                f'{model_type.title()} deleted.',
                model_type,
                doc_id,
                [data],
            )
        elif isinstance(data, list):
            for item in data:
                doc_id = item[f'{model_type_singular}_id']
                delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
                create_log(
                    f'organizations/{organization_id}/logs',
                    claims,
                    f'{model_type.title()} deleted.',
                    model_type,
                    doc_id,
                    [data],
                )
    return True


def get_objects(
        request: Response,
        claims: Dict[str, Any],
        organization_id: str,
        model_id: str,
        model_type: str,
) -> list:
    """Read object(s) through the API.
    Get any parameters and filters. Get organization objects if given an
    organization ID. Get a singular object if requested. Get all of a
    user's data if no organization ID is given.
    Args:
        request (HTTPRequest): An HTTP request used to retrieve parameters.
        claims (dict): A dictionary of user claims.
        organization_id (str): An organization ID to narrow matches.
        model_id (str): A specific data model ID.
        model_type (str): The type of data model.
    Returns:
        (list): A list of dictionaries of the data retrieved.
    """
    docs = []
    filters = []
    limit = request.query_params.get('limit', 1000)
    order_by = request.query_params.get('order_by')
    desc = request.query_params.get('desc', False)
    # TODO: Implement filtered requests. For example:
    # name = request.query_params.get('name')
    # if name:
    #     filters.append({'key': 'name', 'operation': '==', 'value': name})
    # Need to be able to handle created_at and updated_at on most objects.
    # FIXME: Handle multiple organizations
    # owner = claims.get('owner', [])
    # team = claims.get('team', [])
    # qa = claims.get('qa', [])
    # authorized_ids = owner + team + qa
    authorized_ids = claims.get('team', '')
    authorized_ids = claims.get('qa', '')
    authorized_ids = claims.get('owner', '')
    if isinstance(authorized_ids, list):
        authorized_ids = authorized_ids[0]
    if organization_id:
        if model_id:
            ref = f'organizations/{organization_id}/{model_type}/{model_id}'
            docs = get_document(ref)
        else:
            items = request.query_params.get('items')
            if items:
                docs = []
                for item in items:
                    ref = f'organizations/{organization_id}/{model_type}/{item}'
                    doc = get_document(ref)
                    docs.append(doc)
            else:
                ref = f'organizations/{organization_id}/{model_type}'
                docs = get_collection(
                    ref,
                    limit=limit,
                    order_by=order_by,
                    desc=desc,
                    filters=filters,
                )
    else:
        if isinstance(authorized_ids, str):
            ref = f'organizations/{authorized_ids}/{model_type}'
            data = get_collection(
                ref,
                limit=limit,
                order_by=order_by,
                desc=desc,
                filters=filters,
            )
            docs += data
        elif isinstance(authorized_ids, list):
            for _id in authorized_ids:
                ref = f'organizations/{_id}/{model_type}'
                data = get_collection(
                    ref,
                    limit=limit,
                    order_by=order_by,
                    desc=desc,
                    filters=filters,
                )
                docs += data
    return docs


def update_object(
        request: Response, 
        claims: Dict[str, Any],
        model_type: str,
        model_type_singular: str,
        organization_id: str,
) -> list:
    """Create or update object(s) through the API.
    Parse the data and add the data to Firestore.
    Return the data and success.
    Args:
        request (HTTPRequest): An HTTP request used to retrieve parameters.
        claims (dict): User-specific custom claims.
        model_type (str): The type of data model.
        model_type_singular (str): The singular of the type of data model.
        organization_id (str): An organization ID to narrow matches.
    Returns:
        (list): A list of dictionaries of the data posted.
    """
    updated_at = datetime.now().isoformat()
    data = loads(request.body.decode('utf-8'))
    if isinstance(data, dict):
        doc_id = data[f'{model_type_singular}_id']
        data['updated_at'] = updated_at
        data['updated_by'] = claims['uid']
        update_document(f'organizations/{organization_id}/{model_type}/{doc_id}', data)
    elif isinstance(data, list):
        for item in data:
            doc_id = item[f'{model_type_singular}_id']
            item['updated_at'] = updated_at
            item['updated_by'] = claims['uid']
            update_document(f'organizations/{organization_id}/{model_type}/{doc_id}', item)
    else:
        return []
    update_totals(model_type, organization_id, doc_id)
    if model_type != 'logs':
        changes = [data]
        if isinstance(data, list):
            changes = data
        create_log(
            f'organizations/{organization_id}/logs',
            claims,
            f'{model_type.title()} edited.',
            model_type,
            doc_id,
            changes
        )
    return data


def update_totals(model_type: str, organization_id: str, doc_id: str) -> None:
    """Update the total count of a given model type for the day
    the document ID was created.
    Args:
        model_type (str): The name of the data model.
        organization_id (str): The ID of the organization.
        doc_id (str): The ID of the document.
    """
    digits = sub('[^0-9]', '', doc_id)
    year = digits[:2]
    month = digits[2:4]
    day = digits[4:6]
    date = f'20{year}-{month}-{day}'
    ref = f'organizations/{organization_id}/stats/organization_settings/daily_totals/{date}'
    add_to_array(ref, f'total_{model_type}', doc_id)


#------------------------------------------------------------------------------
# API Handlers
#------------------------------------------------------------------------------

def get(
        request: Response,
        claims: Dict[str, Any],
        model_type: str,
        model_type_singular: str,
        model_id: str,
        org_id: str,
) -> Tuple[dict, int]:
    """Perform a 'GET' request."""
    data = get_objects(request, claims, org_id, model_id, model_type)
    return {'success': True, 'data': data}, 200


def post(
        request: Response,
        claims: Dict[str, Any],
        model_type: str,
        model_type_singular: str,
        model_id: str,
        org_id: str,
) -> Tuple[dict, int]:
    """Perform a 'POST' request."""
    data = update_object(request, claims, model_type, model_type_singular, org_id)
    if data:
        return {'success': True, 'data': data}, 200
    else:
        message = """The data submitted was not recognized. You can try to
        post either a singular object or an array / list of objects."""
        return {'success': False, 'data': None, 'message': message}, 403


def delete(
        request: Response,
        claims: Dict[str, Any],
        model_type: str,
        model_type_singular: str,
        model_id: str,
        org_id: str,
) -> Tuple[dict, int]:
    """Perform a 'DELETE' request."""
    success = delete_object(request, claims, model_id, model_type, model_type_singular, org_id)
    if success:
        return {'success': True, 'data': []}, 200
    else:
        message = f'Your must be an owner or quality assurance to delete {model_type}.'
        return {'success': False, 'data': None, 'message': message}, 403


def handle_request(
        request: Response,
        actions: Dict[str, Callable],
        model_type: str,
        model_type_singular: str,
        model_id: str,
) -> Tuple[dict, int]:
    """Perform a request after authenticating the user."""
    claims = authenticate_request(request)
    if claims.get('user') is None:
        message = 'Failure to authenticate with the credentials provided.'
        message += claims['message']
        return {'success': False, 'data': None, 'message': message}, 401
    action = actions.get(request.method)
    # FIXME: Pass `org_id`?
    # try:
    #     org_id = request.query_params.get('organization_id', claims['team'])
    #     assert org_id in claims['team']
    # except:
    #     message = 'Failure to authenticate with the credentials provided.'
    #     return {'success': False, 'data': None, 'message': message}, 401
    # # Optional: Restrict actions based on authentication?
    # # if request.method == 'DELETE':
    # #     try:
    # #         assert org_id in claims['owner']
    # #     except:
    # #         message = 'Owner credentials required for deleting data.'
    # #         return {'success': False, 'data': None, 'message': message}, 403
    return action(request, claims, model_type, model_type_singular, model_id, org_id=None)
