"""
General Utility Functions
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 11/26/2020
Updated: 7/8/2021
"""

# External imports
from django.utils.crypto import get_random_string

# Internal imports
from api.auth import auth
from cannlytics.firebase import get_document, get_collection
from console.state import data, material


def get_model_context(context, organization_id):
    """Get model context based on the current page and section.
    Args:
        request (request): The request object.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any model context.
    """
    model = context['screen']
    ref = f'organizations/{organization_id}/data_models/{model}'
    context['data_model'] = get_document(ref)
    return context


def get_page(request, default=''):
    """Get a page name given a request.
    Args:
        request (request): The request object.
        default (str): A default page to return.
    Returns
        page (str): The page's URL slug.
    """
    page = '/'.join(request.path.split('/')[2:]).rstrip('/')
    if not page:
        page = default
    return page


def get_page_data(kwargs, context):
    """Get all screen-specific data from Firestore.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any screen-specific data.
    """
    if context['section']:
        screen_data = data.get(context['section'])
    else:
        screen_data = data.get(context['screen'])
    if screen_data is None:
        return context
    documents = screen_data.get('documents')
    collections = screen_data.get('collections')
    if documents:
        for item in documents:
            context[item['name']] = get_document(item['ref'])
    if collections:
        for item in collections:
            context[item['name']] = get_collection(
                item['ref'],
                limit=item.get('limit'),
                order_by=item.get('order_by'),
                desc=item.get('desc'),
                filters=item.get('filters'),
            )
    return context


def get_page_context(kwargs, context):
    """Get screen-specific material.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any screen-specific state.
    """
    for value in kwargs.values():
        screen_material = material.get(value)
        key = value.replace('-', '_')
        context[key] = screen_material
    return context


def get_user_context(request, context):
    """Get the user-specific context.
    Args:
        request (HTTPRequest): A request to check for a user session.
        context (dict): Existing page context.
    Returns
        context (dict): Page context updated with any user-specific context.
    """
    claims = auth.verify_session(request)
    if claims:
        uid = claims['uid']
        query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
        organizations = get_collection('organizations', filters=[query])
        user_data = get_document(f'users/{uid}')
        context['organizations'] = organizations
        context['user'] = {**claims, **user_data}
        if organizations:
            context = get_model_context(context, organizations[0]['organization_id'])
    return context
