"""
Views | Cannlytics API
Created: 1/22/2021

API to interface with cannabis analytics.
"""

# External imports
from datetime import datetime
from json import loads

# External imports
from django.core.mail import send_mail
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    create_log,
    get_collection,
    get_document,
    update_document,
)
from cannlytics_api.auth import auth
from cannlytics_console.settings import (
    DEFAULT_FROM_EMAIL,
    LIST_OF_EMAIL_RECIPIENTS,
)

BASE = 'https://api.cannlytics.com'
ENDPOINTS = ['labs']
VERSION = 'v1'


#----------------------------------------------#
# Base Endpoints
#----------------------------------------------#

@api_view(['GET'])
def index(request, format=None):
    """Informational base endpoint."""
    message = f'Welcome to the Cannlytics API. The current version is {VERSION} and is located at {BASE}/{VERSION}.'
    return Response({'message': message}, content_type='application/json')


@api_view(['GET'])
def base(request, format=None):
    """Informational version endpoint."""
    message = f'Welcome to {VERSION} of the Cannlytics API. Available endpoints:\n\n'
    for endpoint in ENDPOINTS:
        message += f'{endpoint}\n'
    return Response({'message': message}, content_type='application/json')


#----------------------------------------------#
# Organization Endpoints
#----------------------------------------------#

# def organizations(request):
#     """Get or update user's organizations."""
#     claims = auth.authenticate(request)
#     if request.method =='POST':
#         post_data = loads(request.body.decode('utf-8'))
#         uid = claims['uid']

#         # Return an error if the organization already exists
#         # and the user is not part of the organization's team.
#         query = {'key': 'organization', 'operation': '==', 'value': organization}
#         organizations = get_collection('organizations', filters=[query])
#         if not organizations:
#             message = 'Organization does not exist. Please check the organization name and try again.'
#             return Response({'success': False, 'message': message}, status=400)

#         # Create activity log.
#         # changes = [post_data]
#         # create_log(f'users/{uid}/logs', claims, 'Updated user data.', 'users', 'user_data', changes)

#         # Create organization if it doesn't exist
#         # All organizations have a unique `org_id`.
#         organization = {
#             'owner': [],
#             'name': '',
#             'license': '',
#             'license_type': '',
#             'team': [],
#             'support': '',
#         }

#         # If an organization already exists, then only the owner edit the organization's team.
#         # update_document(f'users/{uid}', post_data)

#         # On organization creation, the creating user get custom claims.
#         # owner: [org_id, ...]

#         # Owners can add another user to the team.
#         # team: [org_id, ...]
#         # The receiving user then gets the claims.
#         # team: [org_id, ...]

#         # If a user has org_id in their team claims, then they can perform team actions.

#         # Only user's with org_id in owner claim can do sensitive operations.
#         # Such as adding team members, archiving organization

#         # Each organization can have multiple licenses.

#         # Create activity log.
#         # changes = [post_data]
#         # create_log(f'organization/{uid}/logs', claims, 'Updated organization data.', 'organizations', 'organization_data', changes)

#         return Response(organization, content_type='application/json')
#     else:
#         # user_data = get_document(f'users/{claims['uid']}')
#         return Response({}, content_type='application/json')



# def confirm_join_organization():
#     """Confirm a user's request to join an organization."""
#     return NotImplementedError


# def decline_join_organization():
#     """Decline a user's request to join an organization."""
#     return NotImplementedError


# def join_organization(request):
#     """Send the owner of an organization a request for a user to join."""

#     # Identify the user.
#     claims = auth.authenticate(request)
#     uid = claims['uid']
#     user_email = claims['email']
#     post_data = loads(request.body.decode('utf-8'))
#     organization = post_data.get('organization')

#     # Return an error if the organization doesn't exist.
#     query = {'key': 'organization', 'operation': '==', 'value': organization}
#     organizations = get_collection('organizations', filters=[query])
#     if not organizations:
#         message = 'Organization does not exist. Please check the organization name and try again.'
#         return Response({'success': False, 'message': message}, status=400)

#     # Send the owner an email requesting to add the user to the organization's team.
#     org_email = organizations[0]['email']
#     text = f"A user with the email address {user_email} would like to join your organization, \
#         {organization}. Do you want to add this user to your organization's team? Please \
#         reply YES or NO to confirm."
#     paragraphs = []
#     # TODO: Generate confirm, decline, and unsubscribe links with HMACs from user's uid and owner's uid.
#     user_hmac = ''
#     owner_hmac = ''
#     # Optional: Find new home's for endpoints in cannlytics_api and cannlytics_website
#     confirm_link = f'https://console.cannlytics.com/api/organizations/confirm?hash={owner_hmac}&member={user_hmac}'
#     decline_link = f'https://console.cannlytics.com/api/organizations/decline?hash={owner_hmac}&member={user_hmac}'
#     unsubscribe_link = f'https://console.cannlytics.com/api/unsubscribe?hash={owner_hmac}'
#     html_message = render_to_string('templates/cannlytics_console/emails/action_email_template.html', {
#         'recipient': org_email,
#         'paragraphs': paragraphs,
#         'primary_action': 'Confirm',
#         'primary_link': confirm_link,
#         'secondary_action': 'Decline',
#         'secondary_link': decline_link,
#         'unsubscribe_link': unsubscribe_link,
#     })

#     # TODO: Skip sending email if owner is unsubscribed.
#     send_mail(
#         subject="Request to join your organization's team.",
#         message=text,
#         from_email=DEFAULT_FROM_EMAIL,
#         recipient_list=LIST_OF_EMAIL_RECIPIENTS,
#         fail_silently=False,
#         html_message=html_message
#     )

#     # Create activity logs.
#     create_log(f'users/{uid}/logs', claims, 'Requested to join an organization.', 'users', 'user_data', [post_data])
#     create_log(f'organization/{uid}/logs', claims, 'Request from a user to join the organization.', 'organizations', 'organization_data', [post_data])

#     message = f'Request to join {organization} sent to the owner.'
#     return Response({'success': True, 'message': message}, content_type='application/json')


# @api_view(['GET', 'POST'])
# def staff():
#     """Get, create, or update information about an organization's staff."""
#     return NotImplementedError


#----------------------------------------------#
# Lab endpoints
#----------------------------------------------#

@api_view(['GET'])
def lab(request, format=None):
    """Get or update information about a lab."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get('limit', None)
        order_by = request.query_params.get('order_by', 'state')
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ 'data': labs}, content_type='application/json')


@api_view(['GET', 'POST'])
def labs(request, format=None):
    """Get or update information about labs."""

    # Query labs.
    if request.method == 'GET':
        limit = request.query_params.get('limit', None)
        order_by = request.query_params.get('order_by', 'state')
        # TODO: Get any filters from dict(request.query_params)
        labs = get_collection('labs', order_by=order_by, limit=limit, filters=[])
        return Response({ 'data': labs}, content_type='application/json')

    # Update a lab given a valid Firebase token.
    elif request.method == 'POST':

        # Check token.
        try:
            claims = auth.authenticate(request)
        except:
            return Response({'error': 'Could not auth.authenticate.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the posted lab data.
        lab = request.data
        org_id = lab['id']
        lab['slug'] = slugify(lab['name'])

        # TODO: Handle adding labs.
        # Create uuid, latitude, and longitude, other fields?

        # Determine any changes.
        existing_data = get_document(f'labs/{org_id}')
        changes = []
        for key, after in lab:
            before = existing_data[key]
            if before != after:
                changes.append({'key': key, 'before': before, 'after': after})

        # Get a timestamp.
        timestamp = datetime.now().isoformat()
        lab['updated_at'] = timestamp

        # Create a change log.
        log_entry = {
            'action': 'Updated lab data.',
            'type': 'change',
            'created_at': lab['updated_at'],
            'user': claims['uid'],
            'user_name': claims['display_name'],
            'user_email': claims['email'],
            'photo_url': claims['photo_url'],
            'changes': changes,
        }
        update_document(f'labs/{org_id}/logs/{timestamp}', log_entry)

        # Update the lab.
        update_document(f'labs/{org_id}', lab)

        return Response(log_entry, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def lab_logs(request, org_id, format=None):
    """Get or create lab logs."""

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/logs')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create a log.
        return Response({ 'data': 'Under construction'}, content_type='application/json')


@api_view(['GET', 'POST'])
def lab_analyses(request, org_id, format=None):
    """
    Get or update (TODO) lab analyses.
    """

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/analyses')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create an analysis.
        return Response({ 'data': 'Under construction'}, content_type='application/json')


#----------------------------------------------#
# Informational Endpoints
#----------------------------------------------#

@api_view(['GET'])
def regulations(request, format=None):
    """Get regulation information."""
    message = f'Get information about regulations on a state-by-state basis.'
    return Response({'message': message}, content_type='application/json')
