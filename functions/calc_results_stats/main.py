"""
Calculate Results Stats | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 9/3/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate statistics for all lab results and save them to a
    Firestore collection when a user's lab results changes.
    Firebase Functions for Firestore.

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics import firebase
from firebase_admin import initialize_app, firestore
import pandas as pd
import requests

# Initialize Firebase.
try:
    initialize_app()
except ValueError:
    pass


# # FIXME: Re-write with the new framework.
# import base64
# from cloudevents.http import CloudEvent
# import functions_framework


# @functions_framework.cloud_event
# def subscribe(cloud_event: CloudEvent) -> None:
#     print(
#         "Hello, " + base64.b64decode(cloud_event.data["message"]["data"]).decode()
#     )




def calc_results_stats(event, context) -> None:
    """Calculate statistics for all lab results and save them to a
    Firestore collection when a user's lab results changes."""

    # Initialization.
    start_time = datetime.now()

    # Get the necessary data.
    data = event['value']
    uid = data['fields']['uid']['stringValue']
    lab_result_id = data['fields']['lab_result_id']['stringValue']

    
    # TODO: Remove lab result from `public/data/lab_results` if it was deleted.


    # TODO: Create a log of the changes if updated.
    # create_log(
    #     f'public/data/lab_results/{sample_id}/lab_result_logs',
    #     claims=claims,
    #     action='Parsed COAs.',
    #     log_type='data',
    #     key='api_data_coas',
    #     changes=changes
    # )
  

    # TODO: See if the data exists in 'public/data/lab_results',
    # if so, then update it, otherwise create it.


    # TODO: Calculate lab results statistics (once per day?).


    # TODO: Update the strain statistics for the strain of the lab result.

    # Get the user's results.
    docs = firebase.get_collection(f'users/{uid}/lab_results')
    data = pd.DataFrame(docs)
    data['date'] = pd.to_datetime(data['date_tested'])

    # Group data by month.
    monthly = data.groupby(pd.Grouper(key='date', freq='M'))

    # TODO: Calculate consumption statistics.

    # Calculate monthly totals.
    # monthly = data.groupby(pd.Grouper(key='date', freq='M'))
    # monthly_totals = monthly[TOTALS].sum()

    # Save monthly statistics.
    # for index, row in monthly_totals.iterrows():
    #     doc_id = index.strftime('%Y-%m')
    #     ref = f'users/{uid}/receipts_stats/{doc_id}'
    #     stats = row.to_dict()
    #     stats['updated_at'] = context.timestamp
    #     stats['date'] = doc_id
    #     stats['timestamp'] = index.isoformat()
    #     firebase.update_document(ref, stats)
    #     print('Saved monthly statistics:', ref)

    # TODO: Save the statistics to Firestore.
    # lifetime_ref = f'users/{uid}/stats/spending'
    # lifetime_stats = lifetime_totals.to_dict()
    # firebase.update_document(lifetime_ref, lifetime_stats)


# === Test ===
if __name__ == '__main__':

    # Mock document.
    data = {
        'uid': 'qXRaz2QQW8RwTlJjpP39c1I8xM03',
        'email': 'help@cannlytics.com',
    }
    calc_results_stats(data, {})
