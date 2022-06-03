"""
PayPal Management
Copyright (c) 2021-2022 Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 11/29/2021
Updated: 1/25/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports.
from typing import List, Optional

# External imports.
import requests

# API defaults.
BASE = 'https://api-m.paypal.com'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'en_US',
}


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
    response = requests.post(url, data=data, headers=HEADERS, auth=auth)
    body = response.json()
    return body['access_token']


#------------------------------------------------------------------------------
# Products
#------------------------------------------------------------------------------

def create_paypal_product(
        access_token: str,
        name: str,
        description: str,
        product_id: Optional[str] = None,
        product_type: Optional[str] = 'DIGITAL',
        category: Optional[str] = 'OTHER',
        image_url: Optional[str] = None,
        home_url: Optional[str] = None,
        base: Optional[str] = 'https://api-m.paypal.com',
) -> dict:
    """Create a PayPal product.
    Args:
        access_token (str): A required access token.
        name (str): A name for the product.
        description (str): A description for the product.
        product_id (str): A specific subscription plan ID.
        product_type (str): The type of product: PHYSICAL, DIGITAL, SERVICE.
            The default is `DIGITAL` (optional).
        category (str): The product category, `OTHER` by default (optional).
            See <https://developer.paypal.com/api/catalog-products/v1/> for a
            list of categories.
        image_url (str): A URL for an image for the product.
        home_url (str): The homepage for the product.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (dict): Returns the created products.
    """
    url = f'{base}/v1/catalogs/products'
    data = {
        'id': product_id,
        'name': name,
        'description': description,
        'type': product_type,
        'category': category,
        'image_url': image_url,
        'home_url': home_url,
    }
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {**HEADERS, **authorization}
    response = requests.post(url, data=data, headers=headers)
    return response.json()


def get_paypal_products(
        access_token: str,
        product_id: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        total_required: Optional[bool] = True,
        base: Optional[str] = 'https://api-m.paypal.com',
) -> List[dict]:
    """Get a list of products from PayPal.
    Args:
        access_token (str): A required access token.
        page (int): The page at which to begin listing.
        page_size (int): The number of entries per page.
        total_required (bool): Whether or not to return the total.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (list): A list of PayPal subscriptions.   
    """
    params = {
        'page': page,
        'page_size': page_size,
        'total_required': total_required,
    }
    url = f'{base}/v1/catalogs/products'
    if product_id:
        url += f'/{product_id}'
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {**HEADERS, **authorization}
    response = requests.get(url, params=params, headers=headers)
    body = response.json()
    try:
        return body['products']
    except KeyError:
        return body


def update_paypal_product(
        access_token: str,
        product_id: str,
        field: str,
        value: str,
        operation: Optional[str] = 'replace',
        base: Optional[str] = 'https://api-m.paypal.com',
):
    """Update a PayPal product.
    Args:
        access_token (str): A required access token.
        product_id (str): A specific subscription plan ID.
        field (str): The field to change: `description`, `category`,
            `image_url`, or `home_url`.
        value (str): The new value for the field.
        operation (str): The operation to perform: `add`, `replace`, `remove`.
            The default is `replace` (optional).
        base (str): The base API URL, with the live URL as the default.    
    """
    url = f'{base}/v1/catalogs/products/{product_id}'
    data = {
        'op': operation,
        'path': f'/{field}',
        'value': value,
    }
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {**HEADERS, **authorization}
    requests.put(url, data=data, headers=headers)


#------------------------------------------------------------------------------
# TODO: Payments
# https://developer.paypal.com/api/payments/v2/
#------------------------------------------------------------------------------

def get_paypal_payment(
        access_token: str,
        capture_id: str,
        base: Optional[str] = 'https://api-m.paypal.com',
) -> List[dict]:
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


# Future work: Refund captured payment
# /v2/payments/captures/{capture_id}/refund

# Future work: Show details for authorized payment
# /v2/payments/authorizations/{authorization_id}

# Future work: Capture authorized payment
# /v2/payments/authorizations/{authorization_id}/capture

# Future work: Reauthorize authorized payment
# /v2/payments/authorizations/{authorization_id}/reauthorize

# Future work: Void authorized payment
# /v2/payments/authorizations/{authorization_id}/void

# Future work: Show refund details
# /v2/payments/refunds/{refund_id}

#------------------------------------------------------------------------------
# Subscriptions
#------------------------------------------------------------------------------

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
    headers = {**HEADERS, **authorization}
    data = {'reason': reason}
    response = requests.post(url, data=data, headers=headers)
    return response.status_code == 200


def get_paypal_subscription_plans( #pylint: disable=too-many-arguments
        access_token: str,
        product_id: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        total_required: Optional[bool] = True,
        base: Optional[str] = 'https://api-m.paypal.com',
) -> List[dict]:
    """Get PayPal subscription plans.
    Args:
        access_token (str): A required access token.
        product_id (str): A specific subscription plan ID.
        page (int): The page at which to begin listing.
        page_size (int): The number of entries per page.
        total_required (bool): Whether or not to return the total.
        base (str): The base API URL, with the live URL as the default.
    Returns:
        (list): A list of PayPal subscriptions.    
    """
    url = f'{base}/v1/billing/plans'
    params = {
        'product_id': product_id,
        'page': page,
        'page_size': page_size,
        'total_required': total_required,
    }
    authorization = {'Authorization': f'Bearer {access_token}'}
    headers = {**HEADERS, **authorization}
    response = requests.get(url, params=params, headers=headers)
    body = response.json()
    return body['plans']


#------------------------------------------------------------------------------
# TODO: Invoicing
# https://developer.paypal.com/api/invoicing/v2/
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# TODO: Payouts
# https://developer.paypal.com/api/payments.payouts-batch/v1/
#------------------------------------------------------------------------------

