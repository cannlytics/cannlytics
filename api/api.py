"""
API Functions | Cannlytics API
Created: 7/7/2021
Updated: 7/7/2021

API to interface with laboratory data models.
"""
# pylint:disable=line-too-long

# Standard imports
from json import loads

# Internal imports
from cannlytics.firebase import (
    create_log,
    delete_document,
    get_collection,
    get_document,
    update_document,
)

def get_objects(request, authorized_ids, organization_id, model_id, model_type):
    """Read object(s) through the API.
    Get any parameters and filters. Get organization objects if given an
    organization ID. Get a singular object if requested. Get all of a
    user's data if no organization ID is given.
    Args:
        request (HTTPRequest): An HTTP request used to retrieve parameters.
        authorized_ids (list): A list of organizations the use belongs to.
        organization_id (str): An organization ID to narrow matches.
        model_id (str): A specific data model ID.
        model_type (str): The type of data model.
    Returns:
        (list): A list of dictionaries of the data retrieved.
    """
    filters = []
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    desc = request.query_params.get('desc', False)
    # TODO: Implement filtered requests. For example:
    # name = request.query_params.get('name')
    # if name:
    #     filters.append({'key': 'name', 'operation': '==', 'value': name})
    if organization_id:
        if model_id:
            print('Requested:', model_id)
            ref = f'organizations/{organization_id}/{model_type}/{model_id}'
            docs = get_document(ref)
        else:
            ref = f'organizations/{organization_id}/{model_type}'
            docs = get_collection(ref, limit=limit, order_by=order_by, desc=desc, filters=filters)
    else:
        docs = []
        for _id in authorized_ids:
            ref = f'organizations/{_id}/{model_type}'
            docs += get_collection(ref, limit=limit, order_by=order_by, desc=desc, filters=filters)
    return docs


def update_object(request, claims, model_type, model_type_singular, organization_id):
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
    data = loads(request.body.decode('utf-8'))
    if isinstance(data, dict):
        doc_id = data[f'{model_type_singular}_id']
        update_document(f'organizations/{organization_id}/{model_type}/{doc_id}', data)
    elif isinstance(data, list):
        for item in data:
            doc_id = item[f'{model_type_singular}_id']
            update_document(f'organizations/{organization_id}/{model_type}/{doc_id}', item)
    else:
        return []
    create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} edited.', model_type, f'{model_type}_post', [data])
    return data


def delete_object(request, claims, model_id, model_type, model_type_singular, organization_id, owner, qa):
    """Delete an object through the API.
    Parse the data. Check that the user is an owner or quality assurance.
    Delete by URL ID if given. Otherwise delete by using posted ID(s).
    """
    data = loads(request.body.decode('utf-8'))
    if organization_id not in qa and organization_id not in owner:
        return False
    if model_id:
        delete_document(f'organizations/{organization_id}/{model_type}/{model_id}')
    else:
        if isinstance(data, dict):
            doc_id = data[f'{model_type_singular}_id']
            delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
        elif isinstance(data, list):
            for item in data:
                doc_id = item[f'{model_type_singular}_id']
                delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
    create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} deleted.', model_type, f'{model_type}_delete', [data])
    return True
