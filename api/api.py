"""
API Functions | Cannlytics API
Created: 7/7/2021
Updated: 7/8/2021

API to interface with laboratory data models.
"""
# pylint:disable=line-too-long

# Standard imports
from datetime import datetime
from json import loads
from re import sub

# Internal imports
from cannlytics.firebase import (
    add_to_array,
    create_log,
    delete_document,
    get_collection,
    get_document,
    update_document,
)


def delete_object(request, claims, model_id, model_type, model_type_singular, organization_id):
    """Delete an object through the API.
    Parse the data. Check that the user is an owner or quality assurance.
    Delete by URL ID if given. Otherwise delete by using posted ID(s).
    """
    qa = claims.get('qa', '')
    owner = claims.get('owner', '')
    data = loads(request.body.decode('utf-8'))
    if organization_id not in qa and organization_id not in owner:
        return False
    if model_id:
        delete_document(f'organizations/{organization_id}/{model_type}/{model_id}')
        create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} deleted.', model_type, model_id, [data])
    else:
        if isinstance(data, dict):
            doc_id = data[f'{model_type_singular}_id']
            delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
            create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} deleted.', model_type, doc_id, [data])
        elif isinstance(data, list):
            for item in data:
                doc_id = item[f'{model_type_singular}_id']
                delete_document(f'organizations/{organization_id}/{model_type}/{doc_id}')
                create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} deleted.', model_type, doc_id, [data])
    return True


def get_objects(request, claims, organization_id, model_id, model_type):
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
            print('Requested:', model_id)
            ref = f'organizations/{organization_id}/{model_type}/{model_id}'
            docs = get_document(ref)
        else:
            items = request.query_params.get('items')
            print('Items:', items)
            if items:
                docs = []
                for item in items:
                    ref = f'organizations/{organization_id}/{model_type}/{item}'
                    doc = get_document(ref)
                    docs.append(doc)
            else:
                ref = f'organizations/{organization_id}/{model_type}'
                docs = get_collection(ref, limit=limit, order_by=order_by, desc=desc, filters=filters)
    else:
        if isinstance(authorized_ids, str):
            ref = f'organizations/{authorized_ids}/{model_type}'
            docs += get_collection(ref, limit=limit, order_by=order_by, desc=desc, filters=filters)
        elif isinstance(authorized_ids, list):
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
            print('Saving item:\n', item)
            update_document(f'organizations/{organization_id}/{model_type}/{doc_id}', item)
    else:
        return []
    update_totals(model_type, organization_id, doc_id)
    if model_type != 'logs':
        changes = [data]
        if isinstance(data, list):
            changes = data
        create_log(f'organizations/{organization_id}/logs', claims, f'{model_type.title()} edited.', model_type, doc_id, changes)
    return data


def update_totals(model_type, organization_id, doc_id):
    """Update the total count of a given model type for the day
    the document ID was created."""
    digits = sub('[^0-9]', '', doc_id)
    year = digits[:2]
    month = digits[2:4]
    day = digits[4:6]
    date = f'20{year}-{month}-{day}'
    ref = f'organizations/{organization_id}/stats/organization_settings/daily_totals/{date}'
    add_to_array(ref, f'total_{model_type}', doc_id)
