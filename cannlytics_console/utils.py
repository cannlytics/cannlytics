"""
General Utility Functions
Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 11/26/2020
Updated: 4/21/2021
"""

# External imports
from django.utils.crypto import get_random_string

# Internal imports
from cannlytics.firebase import get_document, get_collection, get_user
from cannlytics_api.auth import auth
from cannlytics_console.state import data, material


#----------------------------------------------#
# Page rendering helpers
#----------------------------------------------#

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


def get_screen_specific_data(kwargs, context):
    """Get all screen-specific data from Firestore.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any screen-specific data.
    """
    screen = kwargs.get('screen', 'dashboard')
    section = kwargs.get('section', '')
    if section:
        screen_data = data.get(section)
    else:
        screen_data = data.get(screen)
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


def get_screen_specific_state(kwargs, context):
    """Get screen-specific material.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any screen-specific state.
    """
    kwargs['screen'] = kwargs.get('screen', 'dashboard')
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
    user_claims = auth.verify_session(request)
    user_email = user_claims['email']
    user = {
        'email_verified': user_claims['email_verified'],
        'display_name': user_claims.get('name', ''),
        'photo_url': user_claims.get('picture', f'https://robohash.org/{user_email}?set=set5'),
        'uid': user_claims['uid'],
        'email': user_email,
    }
    context.update({'user': user})
    return context


def get_user_specific_state(uid, context):
    """Get the user-specific UI.
    Args:
        uid (str): A user's unique ID.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any user-specific state.
    """
    context['uid'] = uid
    context['organization'] = {}
    print('User session:', uid)
    if not uid:
        return context
    # Optional: Attach custom claim context.
    # claims = get_custom_claims(uid)
    # possible_claims = ['admin', 'qa']
    # for claim in possible_claims:
    #     if claims.get(claim):
    #         context[claim] = state.get(claim)
    return context


def get_user_specific_data(uid, context):
    """Get user-specific data.
    Args:
        uid (str): A user's unique ID.
        context (dict): A dictionary of existing page context.
    Returns
        context (dict): The context updated with any user-specific state.
    """
    context['user'] = get_user(uid)
    print('User Django side:', context['user'])
    # FIXME: Implement
    # context['organizations'] = get_user_organizations(uid)
    context['organizations'] = []
    return context


#----------------------------------------------#
# Authentication helpers
#----------------------------------------------#


def generate_secret_key(env_file_name):
    """Generate a Django secret key.
    Args:
        env_file_name (str): An .env file to write the secret key.
    """
    env_file = open(env_file_name, 'w+')
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    generated_secret_key = get_random_string(50, chars)
    env_file.write('SECRET_KEY = "{}"\n'.format(generated_secret_key))
    env_file.close()


#----------------------------------------------#
# Constants
#----------------------------------------------#

ROLES = [
    {'title': 'Analyst', 'key': 'analyst'},
    {'title': 'Client', 'key': 'client'},
    {'title': 'Transporter', 'key': 'transporter'},
    {'title': 'Manager', 'key': 'manager'},
    {'title': 'Finance', 'key': 'finance'},
    {'title': 'Stakeholder', 'key': 'stakeholder'},
]
