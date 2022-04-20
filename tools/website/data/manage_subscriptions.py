"""
Manage Subscriptions | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/26/2021
Updated: 12/26/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_subscriptions.py get_subscription_data
    ```

    Upload data.

    ```
    python tools/data/manage_subscriptions.py upload_subscription_data
    ```
"""
# Standard imports
import os
import sys

# External imports
from dotenv import dotenv_values

# Internal imports
from data_management import get_data, upload_data

# Set credentials.
try:
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    config = dotenv_values('.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


def get_subscription_data():
    """Get subscription data from Firestore."""
    ref = 'public/subscriptions/subscription_plans'
    try:
        return get_data(REF, datafile='.datasets/subscriptions.json')
    except FileNotFoundError:
        return get_data(REF, datafile='../../.datasets/subscriptions.json')


def upload_subscription_data():
    """Upload subscription data from local `.datasets`."""
    ref = 'public/subscriptions/subscription_plans'
    stats_doc = 'public/subscriptions'
    try:
        upload_data('.datasets/subscriptions.json', ref, stats_doc=stats_doc)
    except FileNotFoundError:
        upload_data('../../.datasets/subscriptions.json', ref, stats_doc=stats_doc)


if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
