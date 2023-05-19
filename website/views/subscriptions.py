"""
Subscription Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/5/2021
Updated: 5/18/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports
from datetime import datetime
from json import loads
import os
from typing import Optional

# External imports
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    access_secret_version,
    add_to_array,
    create_log,
    create_user,
    get_document,
    update_document,
)
from website.settings import DEFAULT_FROM_EMAIL
from website.utils.utils import get_promo_code


def get_paypal_access_token(
        client_id: str,
        secret: str,
        base: Optional[str] = 'https://api-m.paypal.com',
) -> str:
    """Get a PayPal access token.
    Args:
        client_id (str): Your PayPal client ID.
        secret (str): Your PayPal secret.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (str): The PayPal access token.
    """
    data = {'grant_type': 'client_credentials'}
    url = f'{base}/v1/oauth2/token'
    auth = (client_id, secret)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }
    response = requests.post(url, data=data, headers=headers, auth=auth)
    body = response.json()
    return body['access_token']


def cancel_paypal_subscription(
        access_token: str,
        subscription_id: str,
        reason: Optional[str] = 'No reason provided.',
        base: Optional[str] = 'https://api-m.paypal.com',
):
    """Cancel a PayPal subscription for an individual subscriber.
    Args:
        access_token (str): A required access token.
        subscription_id (str): A specific subscription ID.
        reason (str): The reason for cancellation.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (bool): An indicator if cancellation was successful.
    """
    url = f'{base}/v1/billing/subscriptions/{subscription_id}/cancel'
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }
    headers = {**headers, **authorization}
    data = {'reason': reason}
    response = requests.post(url, data=data, headers=headers)
    return response.status_code == 200


def subscribe(request):
    """Subscribe a user to newsletters, sending them a notification with the
    ability to unsubscribe. Creates a Cannlytics account and sends a welcome
    email if the user does not have an account yet.
    """

    # Ensure that the user has a valid email.
    data = loads(request.body)
    try:
        user_email = data['email']
        validate_email(user_email)
    except ValidationError:
        response = {'success': False, 'message': 'Invalid email in request body.'}
        return JsonResponse(response)

    # Create a promo code that can be used to download data.
    promo_code = get_promo_code(8)
    add_to_array('promos/data', 'promo_codes', promo_code)

    # Record the subscription in Firestore.
    now = datetime.now()
    iso_time = now.isoformat()
    data['created_at'] = iso_time
    data['updated_at'] = iso_time
    data['promo_code'] = promo_code
    update_document(f'subscribers/{user_email}', data)

    # Save the user's subscription.
    plan_name = data['plan_name']
    try:
        claims = authenticate_request(request)
        uid = claims['uid']
        user_data = {'support': True}
        if plan_name == 'newsletter':
            user_data['newsletter'] = True
        else:
            user_data[f'{plan_name}_subscription_id'] = data['id']
        update_document(f'users/{uid}', user_data)
    except KeyError:
        pass

    # Create an account if one does not exist.
    try:
        name = (data.get('first_name', '') + data.get('last_name', '')).strip()
        _, password = create_user(name, user_email)
        message = f'Congratulations,\n\nYou can now login to the Cannlytics console (https://console.cannlytics.com) with the following credentials.\n\nEmail: {user_email}\nPassword: {password}\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long
        subject = 'Welcome to the Cannlytics Platform'
    except:
        message = f'Congratulations,\n\nYou are now subscribed to Cannlytics.\n\nPlease stay tuned for more material or email {DEFAULT_FROM_EMAIL} to begin.\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long
        subject = 'Welcome to the Cannlytics Newsletter'

    # Create an activity log.
    create_log(
        ref='logs/website/subscriptions',
        claims=claims,
        action=f'User ({user_email}) subscribed to {plan_name}.',
        log_type='subscription',
        key='subscribe',
        changes=data,
    )

    # Send a welcome / thank you email.
    # TODO: Use HTML template and load messages / templates from state.
    # template_url = 'website/emails/newsletter_subscription_thank_you.html'
    send_mail(
        subject=subject,
        message=message,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user_email, DEFAULT_FROM_EMAIL],
        fail_silently=False,
        # html_message = render_to_string(template_url, {'context': 'values'})
    )

    # Return a success message.
    response = {'success': True, 'message': 'User successfully subscribed.'}
    return JsonResponse(response)


@api_view(['GET'])
def get_user_subscriptions(request):
    """Get a user's subscriptions."""
    claims = authenticate_request(request)
    try:
        user_id = claims['uid']
        subscriptions = get_document(f'subscribers/{user_id}')
        response = {'success': True, 'data': subscriptions}
        return Response(response, content_type='application/json')
    except KeyError:
        response = {'success': False, 'message': 'Invalid authentication.'}
        return Response(response, content_type='application/json')


def unsubscribe(request):
    """Unsubscribe a user from a PayPal subscription."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_email = claims['email']
    except KeyError:
        response = {'success': False, 'message': 'Unable to authenticate.'}
        return JsonResponse(response)

    # Get the subscription they wish to unsubscribe from.
    data = loads(request.body)
    plan_name = data['plan_name']

    # Unsubscribe the user with the PayPal SDK.
    try:
        project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        payload = access_secret_version(project_id, 'paypal', 'latest')
        paypal_secrets = loads(payload)
        paypal_client_id = paypal_secrets['client_id']
        paypal_secret = paypal_secrets['secret']
        paypal_access_token = get_paypal_access_token(paypal_client_id, paypal_secret)
        user_data = get_document(f'users/{uid}')
        subscription_id = user_data[f'{plan_name}_subscription_id']
        cancel_paypal_subscription(paypal_access_token, subscription_id)
        updated_user_data = {'support': False}
        updated_user_data[f'{plan_name}_subscription_id'] = ''
        update_document(f'users/{uid}', updated_user_data)
    except:
        subscription_id = 'Unidentified'

    # Create an activity log.
    create_log(
        ref='logs/website/subscriptions',
        claims=claims,
        action=f'User ({user_email}) unsubscribed from {plan_name}.',
        log_type='subscription',
        key='subscribe',
        changes=data,
    )

    # Notify the staff.
    staff_message = """Confirm that the following subscription has been canceled:
    User: {}
    Email: {}
    Plan: {}
    Subscription ID: {}
    """.format(uid, user_email, plan_name, subscription_id)
    send_mail(
        subject='User unsubscribed from a PayPal subscription.',
        message=staff_message,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )

    # Return a success message.
    message = 'Successfully unsubscribed from subscription.'
    response = {'success': True, 'message': message}
    return JsonResponse(response)
