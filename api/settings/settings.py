"""
Settings | Cannlytics API
Created: 1/22/2021
Updated: 4/27/2021
Description: API to interface with a user's or organization's settings.
"""

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
from cannlytics_api.auth import auth
from cannlytics_console.settings import (
    DEFAULT_FROM_EMAIL,
    LIST_OF_EMAIL_RECIPIENTS,
)

#-----------------------------------------------------------------------
# Website API Functions
#-----------------------------------------------------------------------

def unsubscribe(request):
    """Unsubscribe a user from emails."""
    return NotImplementedError

#-----------------------------------------------------------------------
# Support emails
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def errors(request):
    """Send an error email to support.
    FIXME: Add throttling https://www.django-rest-framework.org/api-guide/throttling/
    """

    # Try to identify the user.
    try:
        claims = auth.authenticate(request)
        uid = claims['uid']
        user_email = claims['email']
        post_data = loads(request.body.decode('utf-8'))
        organization = post_data.get('organization')
    except:
        # FIXME: Strict throttling needed here!
        claims = {}

    if request.method == 'POST':

        # TODO: Get meta data
        # https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.META
        print(request.META) 

        # TODO: Format the error data into an email.
        # org_email = organizations[0]['email']
        # text = f"A user with the email address {user_email} would like to join your organization, \
        #     {organization}. Do you want to add this user to your organization's team? Please \
        #     reply YES or NO to confirm."
        # # Optional: Find new home's for endpoints in cannlytics_api and cannlytics_website
        # confirm_link = f'https://console.cannlytics.com/api/organizations/confirm?hash={owner_hmac}&member={user_hmac}'
        # decline_link = f'https://console.cannlytics.com/api/organizations/decline?hash={owner_hmac}&member={user_hmac}'
        # unsubscribe_link = f'https://console.cannlytics.com/api/unsubscribe?hash={owner_hmac}'
        # html_message = render_to_string('templates/cannlytics_console/emails/action_email_template.html', {
        #     'recipient': org_email,
        #     'paragraphs': paragraphs,
        #     'primary_action': 'Confirm',
        #     'primary_link': confirm_link,
        #     'secondary_action': 'Decline',
        #     'secondary_link': decline_link,
        #     'unsubscribe_link': unsubscribe_link,
        # })
        message = 'A user reported a new error in the Cannlytics Console.'

        # Send the Cannlytics team an error email.
        send_mail(
            subject='New error reported in the Cannlytics Console',
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=LIST_OF_EMAIL_RECIPIENTS,
            fail_silently=False,
            # html_message=html_message
        )

        # Create an error log.
        timestamp = get_timestamp()
        create_log(
            f'logs/errors/error_logs/{timestamp}',
            claims,
            action=message,
            log_type='console',
            key='console', # Optional: Customize based on reported error.
        )

        message = f'Request to join {organization} sent to the owner.'
        return Response({'success': True, 'message': message}, content_type='application/json')

    elif request.method == 'GET':

        # Get errors if user created them.
        query = {'key': 'email', 'operation': '==', 'value': claims['email']}
        docs = get_collection('logs/errors/error_logs', filters=[query])
        return Response(docs, content_type='application/json')

        # Optional: Get organization-based errors, etc. ?
