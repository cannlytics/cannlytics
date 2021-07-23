"""
Upload Subscription PLan | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/15/2021
Updated: 7/15/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

import os
import environ

import sys
root = '../../../'
sys.path.append(root)
from cannlytics import firebase # pylint: disable=import-error
from console import state

if __name__ == '__main__':

    # Initialize Firebase.
    env = environ.Env()
    env.read_env(f'{root}.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Upload subscription plan data to Firestore.
    pricing_tiers = state.material['get-started']['pricing_tiers']
    for item in pricing_tiers:
        name = item['name']
        ref = f'public/subscriptions/subscription_plans/{name}'
        firebase.update_document(ref, item)
