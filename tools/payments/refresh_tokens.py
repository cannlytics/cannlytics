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
import pandas as pd


# Get all subscribers.
firebase.initialize_firebase()
subscribers = firebase.get_collection('subscribers')
subscriber_data = pd.DataFrame(subscribers)
subscriber_data.set_index('id', inplace=True)

# Make all legacy users into subscribers.
users = firebase.get_collection('users')
user_data = pd.DataFrame(users)
user_data.set_index('id', inplace=True)
for uid, values in user_data.iterrows():
    try:
        user_subscription = subscriber_data.loc[uid]
        print(user_subscription)
        break
    except:
        pass
        # TODO: Populate the user's account with trial tokens.

# TODO: Give premium, pro, and enterprise users their alloted tokens
# every 30 days of the refreshed_at time.


# TODO: Give all free users 10 tokens.


# TODO: Give OpenCollective contributors tokens.
