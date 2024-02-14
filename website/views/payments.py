"""
Subscription Views | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/5/2021
Updated: 6/22/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
from json import loads, dumps
import math
import os
from typing import Optional

# External imports:
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import google.auth

# Internal imports:
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    get_document,
    increment_value,
    update_document,
    update_custom_claims,
)
from website.settings import DEFAULT_FROM_EMAIL, PRODUCTION


# Constants.
DEFAULT_PRICE_PER_TOKEN = 0.05
PAYPAL_SECRET = 'paypal-test'
BASE = 'https://api-m.sandbox.paypal.com'
if PRODUCTION == 'True' or PRODUCTION == True:
    PAYPAL_SECRET = 'paypal'
    BASE = 'https://api-m.paypal.com'


@api_view(['GET'])
def get_user_subscriptions(request):
    """Get a user's subscriptions."""
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_subscription = get_document(f'subscribers/{uid}')
        for key, value in user_subscription.items():
            if isinstance(value, float) and math.isnan(value):
                user_subscription[key] = None
        response = {'success': True, 'data': user_subscription}
        return Response(response, content_type='application/json', status=200)
    except KeyError:
        response = {'success': False, 'message': 'Invalid authentication.'}
        return Response(response, content_type='application/json', status=401)


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
    data = {"grant_type": "client_credentials"}
    url = f"{base}/v1/oauth2/token"
    auth = (client_id, secret)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    print('REQUEST TO PAYPAL:', url)
    response = requests.post(url, data=data, headers=headers, auth=auth)
    body = response.json()
    try:
        return body["access_token"]
    except KeyError:
        print('ERROR:', body)


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


@api_view(['POST'])
def create_order(request):
    """Place an order for tokens through PayPal."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_email = claims['email']
    except KeyError:
        response = {'success': False, 'message': 'Unable to authenticate.'}
        return Response(response, content_type='application/json', status=401)
    
    # Get the amount if a user is ordering a subscription.
    data = loads(request.body)
    amount = data.get('amount', 0)

    # Get the amount of the subscription the user wishes to purchase.
    if amount:
        subscription_id = data['subscription_id']
        subscription_data = get_document(f'public/subscriptions/subscription_plans/{subscription_id}')
        number_of_tokens = subscription_data['tokens']
        price = subscription_data['price_usd']
        plan_id = subscription_data['plan_id']

    # Otherwise, get the number of tokens the user wishes to purchase.
    else:

        # Get the number of tokens the user wishes to purchase.
        try:
            number_of_tokens = float(data['tokens'])
        except:
            response = {'success': False, 'message': 'Number of `tokens` or `amount` required in the request body.'}
            return Response(response, content_type='application/json', status=405)

        # Log.
        print('User {} wants to purchase {} tokens.'.format(uid, number_of_tokens))

        # Get the user's price per token.
        plan_id = None
        price_per_token = DEFAULT_PRICE_PER_TOKEN
        user_subscription = get_document(f'subscribers/{uid}')
        if user_subscription:
            price_per_token = user_subscription.get('price_per_token', DEFAULT_PRICE_PER_TOKEN)
            plan_id = user_subscription.get('plan_id')

        # Log.
        print('Price per token: {}'.format(price_per_token))

        # Calculate the price.
        price = price_per_token * number_of_tokens
        print('Price: {}'.format(price))

    # Attempt to make the PayPal request.
    try:

        # Record the order in Firestore.
        try:
            timestamp = datetime.now().isoformat()
            order_id = timestamp.replace(':', '-').replace('.', '-')
            order_ref = f'payments/orders/{uid}/{order_id}'
            order_data = {
                'created_at': timestamp,
                'uid': uid,
                'user_email': user_email,
                'plan_id': plan_id,
                'price': price,
                'price_per_token': price_per_token,
                'number_of_tokens': number_of_tokens,
            }
            update_document(order_ref, order_data)
        except:
            pass

        # Get PayPal access token.
        try:
            project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        except:
            _, project_id = google.auth.default()
        payload = access_secret_version(project_id, PAYPAL_SECRET, 'latest')
        paypal_secrets = loads(payload)
        paypal_client_id = paypal_secrets['client_id']
        paypal_secret = paypal_secrets['secret']
        paypal_access_token = get_paypal_access_token(
            paypal_client_id,
            paypal_secret,
            base=BASE,
        )

        # Define the order payload.
        purchase = [{'amount': {'currency_code': 'USD', 'value': round(price, 2)}}]
        payload = {'intent': 'CAPTURE', 'purchase_units': purchase}

        # Make the request to create the order.
        url = f'{BASE}/v2/checkout/orders'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {paypal_access_token}",
        }
        response = requests.post(url, data=dumps(payload), headers=headers)
        data = response.json()
        print('PAYPAL RESPONSE:')
        print(response.json())
        response.raise_for_status()

        # Update the order with the order ID.
        try:
            update_document(order_ref, {'order_id': data['id']})
        except:
            pass

        # Return the response.
        response = {'success': True, 'data': data}
        return Response(response, content_type='application/json', status=200)

    # Handle internal errors.
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def capture_order(request, order_id):
    """Capture a PayPal order of AI tokens."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_email = claims['email']
    except KeyError:
        response = {'success': False, 'message': 'Unable to authenticate.'}
        return Response(response, content_type='application/json', status=401)

    # Attempt to make the PayPal request.
    try:

        # Get PayPal access token.
        try:
            project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        except:
            _, project_id = google.auth.default()
        payload = access_secret_version(project_id, 'paypal', 'latest')
        paypal_secrets = loads(payload)
        paypal_client_id = paypal_secrets['client_id']
        paypal_secret = paypal_secrets['secret']
        paypal_access_token = get_paypal_access_token(
            paypal_client_id,
            paypal_secret,
            base=BASE,
        )

        # Make the request to capture the order.
        url = f'{BASE}/v2/checkout/orders/{order_id}/capture'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {paypal_access_token}',
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        order_data = response.json()

    # Handle PayPal errors.
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    # Record the completed order in Firestore.
    try:

        # Get the amount if a user is ordering a subscription.
        data = loads(request.body)
        amount = data.get('amount', 0)

        # Get the amount of the subscription the user wishes to purchase.
        if amount:
            subscription_id = data['subscription_id']
            subscription_data = get_document(f'public/subscriptions/subscription_plans/{subscription_id}')
            number_of_tokens = subscription_data['tokens']
            price = subscription_data['price']
            plan_id = subscription_data['plan_id']

        # Otherwise, get the number of tokens.
        else:
            number_of_tokens = float(data['tokens'])

            # Get the user's rate.
            plan_id = None
            price_per_token = DEFAULT_PRICE_PER_TOKEN
            user_subscription = get_document(f'subscribers/{uid}')
            if user_subscription:
                price_per_token = user_subscription.get('price_per_token', DEFAULT_PRICE_PER_TOKEN)
                plan_id = user_subscription.get('plan_id')

            # Calculate the price.
            price = price_per_token * number_of_tokens

        # Make a transaction entry in Firestore.
        timestamp = datetime.now().isoformat()
        transaction_id = timestamp.replace(':', '-').replace('.', '-')
        order_ref = f'payments/transactions/{uid}/{transaction_id}'
        order_data = {**{
            'created_at': timestamp,
            'uid': uid,
            'user_email': user_email,
            'plan_id': plan_id,
            'price': price,
            'price_per_token': price_per_token,
            'number_of_tokens': number_of_tokens,
        }, **order_data}
        update_document(order_ref, order_data)

        # Create subscriber entry.
        if amount:

            # Add tokens to the user's subscription.
            data = {**order_data, **{'tokens': number_of_tokens, 'support': subscription_id}}
            update_document(f'subscribers/{uid}', data)

            # Update the user's custom claims.
            claims = {**claims, **{'support': subscription_id}}
            update_custom_claims(uid, claims=claims)

            # Format the email.
            subject = 'Subscribed to Cannlytics AI'
            message = f'Congratulations,\n\nYou have successfully subscribed to Cannlytics AI. You can use your tokens to run AI-powered jobs in the app:\n\nhttps://data.cannlytics.com\n\nPut your AI jobs to good use!\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long

        # Otherwise, update the user's amount of tokens.
        else:

            # Get the user's current amount of tokens.
            user_subscription = get_document(f'subscribers/{uid}')
            current_tokens = user_subscription.get('tokens', 0)
            data = {**order_data, **{'tokens': current_tokens}}

            # Credit the user with the appropriate tokens.
            subject = 'Cannlytics AI Tokens Purchased'
            message = f'Congratulations,\n\nYou have successfully purchased {number_of_tokens} Cannlytics AI tokens. You can use your tokens to run AI-powered jobs in the app:\n\nhttps://data.cannlytics.com\n\nPut your AI jobs to good use!\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long
            try:
                increment_value(
                    ref=f'subscribers/{uid}',
                    field='tokens',
                    amount=number_of_tokens,
                )
            except:
                subject = 'Cannlytics AI Tokens Purchase Failed'
                message = f'Please be in touch,\n\nYou have ordered {number_of_tokens} Cannlytics AI tokens, but we had trouble crediting your account. Please email dev@cannlytics.com and we will credit your account with your tokens.\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long

        # Send an email to the admin and the user.
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[user_email, DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except:
            pass

        # Return the response.
        response = {'success': True, 'data': data}
        return Response(response, content_type='application/json', status=200)

    # Handle internal errors.
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def unsubscribe(request):
    """Unsubscribe a user from a PayPal subscription."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        user_email = claims['email']
    except KeyError:
        response = {'success': False, 'message': 'Unable to authenticate.'}
        return Response(response, content_type='application/json', status=401)

    # Unsubscribe the user with the PayPal SDK.
    try:

        # Get user's subscription.
        user_subscription = get_document(f'subscribers/{uid}')
        subscription_id = user_subscription['id']

        # Get PayPal access token.
        project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        payload = access_secret_version(project_id, 'paypal', 'latest')
        paypal_secrets = loads(payload)
        paypal_client_id = paypal_secrets['client_id']
        paypal_secret = paypal_secrets['secret']
        paypal_access_token = get_paypal_access_token(paypal_client_id, paypal_secret)

        # Cancel the subscription.
        cancel_paypal_subscription(paypal_access_token, subscription_id)
        print('CANCELED SUBSCRIPTION: {}'.format(subscription_id))

        # Update the user's data in Firestore.
        update_document(f'users/{uid}', {'support': None})
        update_document(f'subscribers/{uid}', {'id': None})

    # Handle errors manually.
    except:
        subscription_id = 'Unidentified'

    # Create an activity log.
    create_log(
        ref='logs/website/subscriptions',
        claims=claims,
        action=f'User {uid} ({user_email}) unsubscribed from {subscription_id}.',
        log_type='subscription',
        key='unsubscribe',
        changes=[{'id': subscription_id, 'uid': uid}],
    )

    # Notify the staff.
    staff_message = """Confirm that the following subscription has been canceled:
    User: {}
    Email: {}
    Subscription ID: {}
    """.format(uid, user_email, subscription_id)
    send_mail(
        subject='User unsubscribed from a PayPal subscription.',
        message=staff_message,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )

    # Optional: Should the user be notified?

    # Return a success message.
    message = 'You have been successfully unsubscribed from your subscription.'
    response = {'success': True, 'message': message}
    return Response(response, content_type='application/json', status=200)
