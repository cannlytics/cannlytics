"""
Cannlytics Subscriptions Tests
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/22/2023
Updated: 6/22/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports:
from datetime import datetime
import json
import sys
from typing import Optional

# External imports:
from cannlytics.firebase import initialize_firebase, update_document
from dotenv import dotenv_values
import requests

# Internal imports:
sys.path.append('../..')


def get_paypal_access_token(
        client_id: str,
        secret: str,
        base: Optional[str] = 'https://api-m.sandbox.paypal.com',
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
    try:
        return body['access_token']
    except KeyError:
        print('ERROR:', body)


def create_paypal_product(access_token, request_id, product_data):
    """
    Create a PayPal product.
    
    Args:
        access_token (str): The PayPal access token.
        request_id (str): The PayPal request ID.
        product_data (dict): The data for the product.
    """
    url = "https://api-m.sandbox.paypal.com/v1/catalogs/products"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "PayPal-Request-Id": request_id,
    }
    response = requests.post(url, headers=headers, json=plan_data)
    if response.status_code == 201:
        print("Product created successfully.")
        return response.json()
    else:
        print(f"Failed to create product: {response.content}")


def create_paypal_subscription(access_token, request_id, plan_data):
    """
    Create a PayPal subscription plan.
    
    Args:
        access_token (str): The PayPal access token.
        request_id (str): The PayPal request ID.
        plan_data (dict): The data for the plan.
    """
    url = "https://api-m.sandbox.paypal.com/v1/billing/plans"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "PayPal-Request-Id": request_id,
    }
    response = requests.post(url, headers=headers, json=plan_data)
    if response.status_code == 201:
        print("Plan updated successfully.")
        return response.json()
    else:
        print(f"Failed to update plan: {response.content}")


# === Tests ===
if __name__ == '__main__':

    # Get a PayPal access token.
    config = dotenv_values('../../.env')
    paypal_access_token = get_paypal_access_token(
        config['TEST_PAYPAL_CLIENT_ID'],
        config['TEST_PAYPAL_SECRET'],
    )

    # Create a product.
    product_data = {
        "name": "Cannlytics AI Subscription",
        "description": "A Cannlytics AI subscription.",
        "type": "SERVICE",
        "category": "SOFTWARE",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_ai_with_text.png?alt=media&token=78d19117-eff5-4f45-a8fa-3bbdabd6917d",
        "home_url": "https://cannlytics.com"
    }

    # Create a plan.
    plan_data = {
        "product_id": None,
        "name": "Premium",
        "description": "Premium Cannlytics AI subscription.",
        "billing_cycles": [
        {
            "frequency": {
            "interval_unit": "MONTH",
            "interval_count": 1
            },
            "tenure_type": "REGULAR",
            "sequence": 1,
            "total_cycles": 12,
            "pricing_scheme": {
                "fixed_price": {
                    "value": "4.20",
                    "currency_code": "USD"
                }
            }
        }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": False,
            "setup_fee": {
                "value": "0",
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 1
        },
        "taxes": {
            "percentage": "9.5",
            "inclusive": False
        }
    }

    # Create a product.
    product_data = create_paypal_product(
        access_token=paypal_access_token,
        request_id=datetime.now().isoformat(),
        product_data=product_data,
    )
    print('Created plan:', product_data)

    # Create a subscription.
    plan_data['product_id'] = product_data['id']
    subscription_data = create_paypal_subscription(
        access_token=paypal_access_token,
        request_id=datetime.now().isoformat(),
        plan_data=plan_data,
    )
    print('Created subscription plan:', subscription_data)

    # Save the data in Firestore.
    doc_id = subscription_data['id']
    ref = f'public/subscriptions/test_subscription_plans/{doc_id}'
    initialize_firebase()
    update_document(ref, subscription_data)
    print('Saved subscription data to Firestore:', ref)
