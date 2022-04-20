"""
Upload Subscription PLan | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/15/2021
Updated: 3/25/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports.
import os
import sys

# External packages.
from dotenv import dotenv_values

# Internal imports
root = '../../../'
sys.path.append(root)
from cannlytics import firebase # pylint: disable=import-error
from console import state # pylint: disable=import-error

if __name__ == '__main__':

    # Initialize Firebase.
    config = dotenv_values(f'{root}.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Upload subscription plan data to Firestore.
    pricing_tiers = state.material['get-started']['pricing_tiers']
    for item in pricing_tiers:
        name = item['name']
        ref = f'public/subscriptions/subscription_plans/{name}'
        firebase.update_document(ref, item)
