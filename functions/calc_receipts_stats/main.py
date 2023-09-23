"""
Calculate Receipts Stats | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 7/7/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate spending statistics for user when they update
    their receipts and save them to a Firestore collection.

"""

# External imports:
from cannlytics import firebase
from firebase_functions import firestore_fn, options
from firebase_admin import initialize_app, firestore
import pandas as pd


# Initialize Firebase.
initialize_app()


# Set the region.
options.set_global_options(region=options.SupportedRegion.US_CENTRAL1)


@firestore_fn.on_document_written(
    document='users/{uid}/receipts/{receipt_id}',
    # timeout_sec=300,
    # memory=options.MemoryOption.MB_512,
)
def calc_receipts_stats(
        event: firestore_fn.Event[firestore_fn.Change],
    ) -> None:
    """Calculate statistics for a strain and save them to a
    Firestore collection when a user's strain data changes."""

    # Get an object with the current document values.
    # If the document does not exist, it was deleted.
    document = (event.data.after.to_dict()
                if event.data.after is not None else None)

    # Get an object with the previous document values.
    # If the document does not exist, it was newly created.
    previous_values = (event.data.before.to_dict()
                        if event.data.before is not None else None)


    # TODO: Smartly handle only data that changed to
    # prevent unnecessarily calculating statistics.
    # changed_data = {k: document[k] for k in set(document) - set(previous_values)}

    # Get the user's ID.
    uid = event.params['uid']

    # Get the user's receipts.
    docs = firebase.get_collection(f'users/{uid}/receipts')
    data = pd.DataFrame(docs)
    data['date'] = pd.to_datetime(data['date_sold'])

    # Group data by month.
    monthly = data.groupby(pd.Grouper(key='date', freq='M'))

    # TODO: Calculate total transactions:
    # - lifetime
    # - by month
    # - by quarter
    # - by year
    # - by retailer
    # - by product type
    # - by strain
    totals = ['total_transactions', 'total_tax', 'total_price']
    monthly_totals = monthly[totals].sum()

    # TODO: Calculate spending:
    # - lifetime
    # - by month
    # - by quarter
    # - by year
    # - by retailer
    # - by product type
    # - by strain


    # TODO: Calculate total tax:
    # - lifetime
    # - by month
    # - by quarter
    # - by year

    # TODO: Calculate total spend:
    # - lifetime
    # - by year
    # - by quarter
    # - by month
    # - by retailer
    # - by product type
    # - by strain

    # TODO: Calculate average basket size:
    # - lifetime
    # - by month
    # - by quarter
    # - by year
    # - by day of the week

    # TODO: Calculate average price per gram:
    # - flower
    # - concentrate
    # - edible

    # TODO: Calculate proportion of spend on each product type:
    # - lifetime
    # - by year
    # - by quarter
    # - by month

    # TODO: Handle no receipts.

    # Save monthly statistics.
    for index, row in monthly_totals.iterrows():
        doc_id = index.strftime('%Y-%m')
        ref = f'users/{uid}/receipts_stats/{doc_id}'
        stats = row.to_dict()
        stats['updated_at'] = firestore.SERVER_TIMESTAMP
        stats['date'] = index.isoformat()
        firebase.update_document(ref, stats)
        print('Saved monthly statistics:', ref)

    # TODO: Save annual statistics.

    # TODO: Save lifetime statistics.
