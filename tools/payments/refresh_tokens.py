"""
Refresh Tokens | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/23/2023
Updated: 7/5/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Refresh user's tokens each month.
"""
from datetime import datetime
from cannlytics import firebase
import pandas as pd


# Get all subscribers.
firebase.initialize_firebase()
subscribers = firebase.get_collection('subscribers')
subscriber_data = pd.DataFrame(subscribers)
subscriber_data.set_index('id', inplace=True)

# Make all legacy users into subscribers by givin all free users 10 tokens.
users = firebase.get_collection('users')
user_data = pd.DataFrame(users)
user_data.set_index('id', inplace=True)
for uid, values in user_data.iterrows():
    try:
        user_subscription = subscriber_data.loc[uid]
    except:
        # Populate the user's account with trial tokens.
        update = {
            'support': 'free',
            'tokens': 10,
            'uid': uid,
            'email': values['email'],
            'photo_url': values['photo_url'],
            'display_name': values['display_name'],
            'updated_at': datetime.now().isoformat(),
        }
        ref = f'subscribers/{uid}'
        firebase.update_document(ref, update)


# TODO: Give premium, pro, and enterprise users their alloted tokens
# every 30 days of the refreshed_at time.


# TODO: Give OpenCollective contributors bonus tokens.
