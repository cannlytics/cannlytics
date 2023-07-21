"""
Calculate Receipts Stats | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2023
Updated: 7/8/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Calculate spending statistics for user when they update
    their receipts and save them to a Firestore collection.

"""

# External imports:
from cannlytics import firebase
import pandas as pd


# Initialize Firebase.
firebase.initialize_firebase()


TOTALS = ['total_transactions', 'total_tax', 'total_price']


def calc_product_type_proportions(data):
    """Calculate the proportion of spend on each product type."""

    # Explode the data frame on the product_types column
    exploded_data = data.explode('product_types')

    # Convert product_types to lowercase for case-insensitive grouping.
    exploded_data['product_types'] = exploded_data['product_types'].str.lower()

    # Calculate the proportion of spend by product type.
    product_type_totals = exploded_data.groupby('product_types')['total_price'].sum()
    total_spend = product_type_totals.sum()
    product_type_proportions = product_type_totals / total_spend

    # Group proportions less than 1% into "Other".
    product_type_proportions = product_type_proportions[product_type_proportions >= 0.01]
    product_type_proportions['other'] = 1 - product_type_proportions.sum()

    # Create and return product type proportion dictionary.
    return product_type_proportions.to_dict()


def calc_receipts_stats(event, context) -> None:
    """Calculate statistics for a user's receipts and save them to a
    Firestore collection when a user's receipt data changes."""

    # TODO: Smartly handle only data that changed to
    # prevent unnecessarily calculating statistics.
    # changed_data = {k: document[k] for k in set(document) - set(previous_values)}

    # Get the user's ID.
    resource_parts = context.resource.split('/')
    uid = resource_parts[resource_parts.index('users') + 1]
    print('User ID:', uid)

    # Get the user's receipts.
    docs = firebase.get_collection(f'users/{uid}/receipts')
    data = pd.DataFrame(docs)

    # TODO: Handle no receipts or deleted receipts.


    # Add a datetime column.
    data['date'] = pd.to_datetime(data['date_sold'])

    # Calculate monthly totals.
    monthly = data.groupby(pd.Grouper(key='date', freq='M'))
    monthly_totals = monthly[TOTALS].sum()

    # TODO: Calculate total transactions:
    # ✓ lifetime
    # ✓ by month
    # - by quarter
    # - by year
    # - by retailer
    # - by product type
    # - by strain

    # Calculate lifetime totals.
    lifetime_totals = data[TOTALS].sum()
    lifetime_totals['updated_at'] = context.timestamp

    # TODO: Calculate total spending:
    # ✓ lifetime
    # ✓ by month
    # - by quarter
    # - by year
    # - by retailer
    # - by product type
    # - by strain


    # TODO: Calculate total tax:
    # ✓ lifetime
    # ✓ by month
    # - by quarter
    # - by year

    # TODO: Calculate average basket size:
    # - lifetime
    # - by month
    # - by quarter
    # - by year
    # - by day of the week

    # TODO: Calculate average price per gram:
    # - flower
    # - concentrate
    # - edible (price per each)

    # TODO: Calculate proportion of spend on each product type:
    # - lifetime
    # - by year
    # - by quarter
    # - by month

    # Save monthly statistics.
    for index, row in monthly_totals.iterrows():
        doc_id = index.strftime('%Y-%m')
        ref = f'users/{uid}/receipts_stats/{doc_id}'
        stats = row.to_dict()
        stats['updated_at'] = context.timestamp
        stats['date'] = doc_id
        stats['timestamp'] = index.isoformat()
        firebase.update_document(ref, stats)
        print('Saved monthly statistics:', ref)

    # TODO: Save annual statistics.

    # TODO: Save retailer, product type, and strain spending statistics.
    # Group data by product type and calculate total spend for each product type

    # Calculate product type proportions.
    product_type_proportions = calc_product_type_proportions(data)

    # Save lifetime statistics.
    lifetime_ref = f'users/{uid}/stats/spending'
    lifetime_stats = lifetime_totals.to_dict()
    lifetime_stats['product_type_proportions'] = product_type_proportions
    firebase.update_document(lifetime_ref, lifetime_stats)