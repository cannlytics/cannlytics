"""
Data Market Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/5/2021
Updated: 1/26/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports
import os
from datetime import datetime
from json import loads
import requests

# External imports
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import FileResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    access_secret_version,
    add_to_array,
    create_log,
    create_short_url,
    get_collection,
    get_document,
    get_file_url,
    increment_value,
    update_document,
)
from website.settings import DEFAULT_FROM_EMAIL, FIREBASE_API_KEY, FIREBASE_PROJECT_ID
# from cannlytics.data import market
from cannlytics.paypal import (
    get_paypal_access_token,
    # get_paypal_payment,
)
from website.views.mixins import BaseMixin


# TODO: Publish cannlytics v0.0.11
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'en_US',
}
def get_paypal_payment(
        access_token: str,
        capture_id: str,
        base = 'https://api-m.paypal.com',
):
    """Get captured payment details.
    Args:
        access_token (str): A required access token.
        capture_id (str): The captured payment ID.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (list): A list of PayPal subscriptions.   
    """
    url = f'{base}/v2/payments/captures/{capture_id}'
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {**HEADERS, **authorization}
    response = requests.get(url, headers=headers)
    return response.json()


class DatasetView(BaseMixin, TemplateView):
    """Dataset page."""

    def get_template_names(self):
        return ['website/pages/data/dataset.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get PayPal credentials.
        context['paypal'] = get_document('credentials/paypal')

        # Get the page's dataset.
        dataset_id = self.kwargs.get('dataset_id', '')
        if dataset_id:
            context['dataset'] = get_document(f'public/data/datasets/{dataset_id}')

        return context


@csrf_exempt
def buy_data(request):
    """Facilitate the purchase of a dataset on the data market."""

    # Ensure that the user has a valid email.
    data = loads(request.body)
    try:
        user_email = data['email']
        validate_email(user_email)
    except ValidationError:
        response = {'success': False, 'message': 'Invalid email in request body.'}
        return JsonResponse(response)
    
    # Check if the payment ID is valid.
    # FIXME: Make this required.
    try:
        payment_id = data['payment_id']
        print('Checking payment ID:', payment_id)
        project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        payload = access_secret_version(project_id, 'paypal', 'latest')
        paypal_secrets = loads(payload)
        paypal_client_id = paypal_secrets['client_id']
        paypal_secret = paypal_secrets['secret']
        paypal_access_token = get_paypal_access_token(paypal_client_id, paypal_secret)
        payment = get_paypal_payment(paypal_access_token, payment_id)
        assert payment['id'] == payment_id
        print('Payment ID matched captured payment ID.')
    except:
        pass

    # Future work: Ensure that the user has a .edu email for student discount?

    # Get the dataset zipped folder.
    dataset = data['dataset']
    file_name = dataset['file_name']
    file_ref = dataset['file_ref']
    download_url = get_file_url(file_ref)
    # Optional: Allow for specifying suffix options.
    short_url = create_short_url(FIREBASE_API_KEY, download_url, FIREBASE_PROJECT_ID)
    data['download_url'] = download_url
    data['short_url'] = short_url

    # Keep track of a user's downloaded data if the user is signed in.
    now = datetime.now()
    iso_time = now.isoformat()
    data['created_at'] = iso_time
    data['updated_at'] = iso_time
    try:
        claims = authenticate_request(request)
        uid = claims['uid']
        update_document(f'users/{uid}/datasets', {**data, **{'uid': uid}})
    except KeyError:
        pass

    # Optional: Read the email template from storage?
    # Optional: Use HTML template.
    # Optional: Load messages from state?
    # # template_url = 'website/emails/newsletter_subscription_thank_you.html'
    # Optional: Actually attach the datafile (too large a file problem?)

    # Email the data to the user.
    message = f'Congratulations on your new dataset,\n\nYou can access your data with the following link:\n\n{short_url}\n\nYou can monitor the market for new datasets.\n\nAlways here to help,\nThe Cannlytics Team' #pylint: disable=line-too-long
    subject = 'Dataset Purchased - Your Dataset is Attached'
    send_mail(
        subject=subject,
        message=message,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user_email, DEFAULT_FROM_EMAIL],
        fail_silently=False,
        # html_message = render_to_string(template_url, {'context': 'values'})
    )

    # Create an activity log.
    create_log(
        ref='logs/website/payments',
        claims=claims,
        action=f'User ({user_email}) bought a dataset.',
        log_type='market',
        key='buy_data',
        changes=data,
    )

    # Return the file to download.
    return FileResponse(open(download_url, 'rb'), filename=file_name)


# Future work: Implement blockchain market.

# @csrf_exempt
# def publish_data(request):
#     """Publish a dataset on the data market."""
#     ocean = market.initialize_market()
#     files = [
#         {
#             'index': 0,
#             'contentType': 'text/text',
#             'url': 'https://raw.githubusercontent.com/trentmc/branin/main/branin.arff'
#         }
#     ]
#     data_token, asset = market.publish_data(
#         ocean,
#         os.environ('TEST_PRIVATE_KEY1'),
#         files,
#         'DataToken1',
#         'DT1',
#         'KLS',
#         data_license='CC0: Public Domain',
#     )
#     # TODO: Keep track of data_token and asset on the data market?


# @csrf_exempt
# def sell_data(request):
#     """Sell a dataset on the data market."""
#     ocean = market.initialize_market()
#     # TODO: Get the data token!!!
#     data_token = None
#     market.sell_data(
#         ocean,
#         os.environ('TEST_PRIVATE_KEY1'),
#         data_token,
#         100,
#         fixed_price=True,
#     )


# @csrf_exempt
# def buy_data(request):
#     """Buy a dataset on the data market."""
#     # TODO: Get the data token and asset!!!
#     data_token, asset = None, None
#     ocean = market.initialize_market()
#     seller_wallet = market.get_wallet(
#         ocean,
#         os.environ('TEST_PRIVATE_KEY1')
#     )
#     market.buy_data(
#         ocean,
#         os.environ('TEST_PRIVATE_KEY2'),
#         data_token.address,
#         seller_wallet,
#         min_amount=2,
#         max_amount=5,
#     )
#     market.download_data(
#         ocean,
#         os.environ('TEST_PRIVATE_KEY2'),
#         asset.did
#     )
#     # TODO: Facilitate the download for the user.


@csrf_exempt
def promotions(request):
    """Record a promotion, by getting promo code,
    finding any matching promotion document,
    and updating the views."""
    try:
        data = loads(request.body)
        promo_code = data['promo_code']
        matches = get_collection('promos/events/promo_stats', filters=[
            {'key': 'hash', 'operation': '>=', 'value': promo_code},
            {'key': 'hash', 'operation': '<=', 'value': '\uf8ff'},
        ])
        match = matches[0]
        promo_hash = match['hash']
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        increment_value(f'promos/events/promo_stats/{promo_hash}', 'views')
        add_to_array(f'promos/events/promo_stats/{promo_hash}', 'viewed_at', timestamp)
        # Optional: If user has an account,
        # record which user visited in viewed_by collection.
        return JsonResponse({'message': {'success': True}})
    except:
        return JsonResponse({'message': {'success': False}})
