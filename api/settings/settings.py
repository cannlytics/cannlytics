"""
Settings | Cannlytics API
Created: 1/22/2021
Updated: 4/27/2021
Description: API to interface with a user's or organization's settings.
"""
# pylint:disable=line-too-long

# Standard imports
from json import loads

# External imports
from cannlytics.utils.utils import get_timestamp
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import create_log, get_collection
from api.auth import auth
from api.api import get_objects, update_object, delete_object
from console.settings import (
    DEFAULT_FROM_EMAIL,
    LIST_OF_EMAIL_RECIPIENTS,
)

#-----------------------------------------------------------------------
# Logs
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def logs(request, format=None, log_id=None):
    """Get and create logs."""

    # Initialize and authenticate.
    model_id = log_id
    model_type = 'logs'
    model_type_singular = 'log'
    claims = auth.verify_session(request)
    try:
        uid = claims['uid']
        owner = claims.get('owner', [])
        team = claims.get('team', [])
        qa = claims.get('qa', [])
        authorized_ids = owner + team + qa
    except KeyError:
        message = 'Your request was not authenticated. Ensure that you have a valid session or API key.'
        return Response({'error': True, 'message': message}, status=401)
    
    # Authorize that the user can work with the data.
    organization_id = request.query_params.get('organization_id')
    if organization_id not in authorized_ids:
        message = f'Your must be an owner, quality assurance, or a team member of this organization to manage {model_type}.'
        return Response({'error': True, 'message': message}, status=403)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, authorized_ids, organization_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, organization_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)


#-----------------------------------------------------------------------
# Website API Functions
#-----------------------------------------------------------------------

def unsubscribe(request):
    """Unsubscribe a user from emails."""
    return NotImplementedError

#-----------------------------------------------------------------------
# Support emails
#-----------------------------------------------------------------------

# @api_view(['GET', 'POST'])
# def errors(request):
#     """Send an error email to support.
#     FIXME: Add throttling https://www.django-rest-framework.org/api-guide/throttling/
#     """

#     # Try to identify the user.
#     try:
#         claims = auth.authenticate(request)
#         uid = claims['uid']
#         user_email = claims['email']
#         post_data = loads(request.body.decode('utf-8'))
#         organization = post_data.get('organization')
#     except:
#         # FIXME: Strict throttling needed here!
#         claims = {}

#     if request.method == 'POST':

#         # TODO: Get meta data
#         # https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.META
#         print(request.META) 

#         # TODO: Format the error data into an email.
#         # org_email = organizations[0]['email']
#         # text = f"A user with the email address {user_email} would like to join your organization, \
#         #     {organization}. Do you want to add this user to your organization's team? Please \
#         #     reply YES or NO to confirm."
#         # # Optional: Find new home's for endpoints in api and cannlytics_website
#         # confirm_link = f'https://console.cannlytics.com/api/organizations/confirm?hash={owner_hmac}&member={user_hmac}'
#         # decline_link = f'https://console.cannlytics.com/api/organizations/decline?hash={owner_hmac}&member={user_hmac}'
#         # unsubscribe_link = f'https://console.cannlytics.com/api/unsubscribe?hash={owner_hmac}'
#         # html_message = render_to_string('templates/console/emails/action_email_template.html', {
#         #     'recipient': org_email,
#         #     'paragraphs': paragraphs,
#         #     'primary_action': 'Confirm',
#         #     'primary_link': confirm_link,
#         #     'secondary_action': 'Decline',
#         #     'secondary_link': decline_link,
#         #     'unsubscribe_link': unsubscribe_link,
#         # })
#         message = 'A user reported a new error in the Cannlytics Console.'

#         # Send the Cannlytics team an error email.
#         send_mail(
#             subject='New error reported in the Cannlytics Console',
#             message=message,
#             from_email=DEFAULT_FROM_EMAIL,
#             recipient_list=LIST_OF_EMAIL_RECIPIENTS,
#             fail_silently=False,
#             # html_message=html_message
#         )

#         # Create an error log.
#         timestamp = get_timestamp()
#         create_log(
#             f'logs/errors/error_logs/{timestamp}',
#             claims,
#             action=message,
#             log_type='console',
#             key='console', # Optional: Customize based on reported error.
#         )

#         message = f'Request to join {organization} sent to the owner.'
#         return Response({'success': True, 'message': message}, content_type='application/json')

#     elif request.method == 'GET':

#         # Get errors if user created them.
#         query = {'key': 'email', 'operation': '==', 'value': claims['email']}
#         docs = get_collection('logs/errors/error_logs', filters=[query])
#         return Response(docs, content_type='application/json')

#         # Optional: Get organization-based errors, etc. ?
