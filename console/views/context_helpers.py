"""
Utility Functions | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/26/2020
Updated: 2/6/2022
License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
"""
# Standard imports.
from datetime import datetime

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import get_document, get_collection, update_document
from console.state import app_context, data_models, material, page_data


def get_data_models(context):
    """Get screen-specific material.
    Args:
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with the standard data models.
    """
    # TODO: Return an organization's specific data models if possible.
    context['data_models'] = data_models
    for item in context['data_models']:
        try:
            del item['fields']
        except KeyError:
            pass
    return context


def get_model_data(context, organization_id):
    """Get model context based on the current page and section.
    Args:
        context (dict): A dictionary of existing page context.
        organization_id (str): The ID of a specific organization.
    Returns
        (dict): The context updated with any model context.
    """
    model = context['screen']
    ref = f'organizations/{organization_id}/data_models/{model}'
    context['data_model'] = get_document(ref)
    return context


def get_organization_data_models(context):
    """Get an organization's specific data models.
    Args:
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with the organization's data models.
    """
    organizations = context.get('organizations')
    if organizations:
        # FIXME: Handle multiple organizations.
        org_id = organizations[0]['organization_id']
        context = get_model_data(context, org_id)
    return context


def get_page_context(kwargs, context):
    """Get screen-specific material.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with any screen-specific state.
    """
    context['app'] = app_context
    parts = [('screen', 'dashboard'), ('section', ''), ('unit', '')]
    for part in parts:
        part_name = part[0]
        default = part[1]
        value = kwargs.get(part_name, default)
        context[part_name] = value
        try:
            page_material = material[value]
            key = value.replace('-', '_')
            context[key] = page_material
        except KeyError:
            continue
    # TODO: Improve: this is not an elegant way to pass this context.
    organization_context = context.get('organizations')
    if organization_context:
        context['organization_context'] = organization_context
    return context


def get_page_data(context):
    """Get all data for a page from Firestore.
    Args:
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with any screen-specific data.
    """
    namespaces = []
    try:
        namespace = context['screen']
        namespaces.append(page_data[namespace])
    except KeyError:
        pass
    try:
        namespace = context['section']
        namespaces.append(page_data[namespace])
    except KeyError:
        pass
    for namespace in namespaces:
        try:
            documents = namespace['documents']
            for item in documents:
                context[item['name']] = get_document(item['ref'])
        except KeyError:
            pass
        try:
            collections = namespace['collections']
            for item in collections:
                context[item['name']] = get_collection(
                    item['ref'],
                    limit=item.get('limit'),
                    order_by=item.get('order_by'),
                    desc=item.get('desc'),
                    filters=item.get('filters'),
                )
        except KeyError:
            pass
    return context


def get_user_data(request, context):
    """Get user-specific context.
    Args:
        request (HTTPRequest): A request to check for a user session.
        context (dict): Existing page context.
    Returns
        context (dict): Page context updated with any user-specific context.
    """
    try:
        claims = authenticate_request(request)
    except:
        return context
    try:
        uid = claims['uid']
        query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
        organizations = get_collection('organizations', filters=[query])
        user_data = get_document(f'users/{uid}')
        context['organizations'] = organizations
        context['user'] = {**claims, **user_data}
    except KeyError:
        context['organizations'] = []
        context['user'] = {}
    return context


def save_analytics(request, context):
    """Save page analytics to Firestore."""
    now = datetime.now().isoformat()
    date = now[:10]
    values = {
        'date': date,
        'time': now,
        'page': request.path,
        'query': request.GET.get('q'),
    }
    # Optional: Merge more user information and more elegantly.
    user = context['user']
    if user:
        values['email'] = user['email']
        values['uid'] = user['uid']
    ref = f'logs/console/page_visits/{now}'
    update_document(ref, values)
