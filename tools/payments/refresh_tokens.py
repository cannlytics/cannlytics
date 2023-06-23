"""
Refresh Tokens | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/23/2023
Updated: 6/23/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Refresh user's tokens each month.
"""
from cannlytics import firebase


# Get all subscribers.
initialize_firebase()
subscribers = firebase.get_collection('subscribers')

# TODO: Give premium, pro, and enterprise users their alloted tokens
# every 30 days of the refreshed_at time.


# TODO: Give all free users 10 tokens.


# TODO: Give OpenCollective contributors tokens.
