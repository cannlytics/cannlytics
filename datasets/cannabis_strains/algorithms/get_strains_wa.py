"""
Curate CCRS Strain Data
Copyright (c) 2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/25/2023
Updated: 8/13/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml>

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics.utils import sorted_nicely
import pandas as pd


# Define the fields that will be used.
FIELDS = {
    'initial_quantity': 'string',
    'inventory_created_at': 'string',
    'inventory_type': 'string',
    'quantity_on_hand': 'string',
    'strain_name': 'string',
    'strain_type': 'string',
    'unit_weight_grams': 'string',
}
NUMERIC = ['unit_weight_grams', 'initial_quantity', 'quantity_on_hand']


def curate_ccrs_strains(data_dir, stats_dir):
    """Curate CCRS strains by merging additional datasets."""

    print('Curating strains...')
    start = datetime.now()

    # Create stats directory if it doesn't already exist.
    inventory_dir = os.path.join(stats_dir, 'inventory')
    inventory_files = sorted_nicely(os.listdir(inventory_dir))

    # TODO: Calculate totals by month!

    # Calculate strain statistics using curated inventory items.
    strain_stats = pd.DataFrame({'total_weight': [], 'total_sold': []})
    for i, datafile in enumerate(inventory_files):
        if datafile.startswith('~$'):
            continue
        print('Augmenting:', datafile, i + 1, '/', len(inventory_files))

        # Read the inventory items.
        data = pd.read_excel(
            os.path.join(inventory_dir, datafile),
            usecols=list(FIELDS.keys()),
            dtype=FIELDS,
        )

        # FIXME: Implement monthly stats.
        # sample['product_created_at'].min()
        # sample['product_created_at'].max()

        # Identify all flower products.
        flower = data.copy(deep=True).loc[data['inventory_type'] == 'Usable Marijuana']

        # Convert columns to numeric.
        for col in NUMERIC:
            flower[col] = flower[col].apply(
                lambda x: pd.to_numeric(x, errors='coerce')
            )

        # Calculate total weight.
        total_weight = flower['unit_weight_grams'].mul(flower['initial_quantity'])

        # Calculate total sold.
        quantity_sold = flower['initial_quantity'] - flower['quantity_on_hand']
        total_sold = flower['unit_weight_grams'].mul(quantity_sold)

        # Convert weight to pounds.
        flower = flower.assign(
            total_weight = total_weight * 0.00220462,
            total_sold = total_sold * 0.00220462,
        )

        # Aggregate weights by `strain_name`.
        flower_stats = flower.groupby('strain_name').agg({
            'total_weight': 'sum',
            'total_sold': 'sum',
        })

        # Simply copy statistics on the first iteration.
        if i == 0:
            strain_stats = strain_stats.add(flower_stats, fill_value=0)

        # Otherwise, aggregate statistics.
        else:
            weights = [strain_stats['total_weight'], flower_stats['total_weight']]
            sales = [strain_stats['total_sold'], flower_stats['total_sold']]
            strain_weight = pd.concat(weights, axis=1).sum(axis=1)
            strain_sold = pd.concat(sales, axis=1).sum(axis=1)

            # Increment strain weight statistics.
            strain_stats = strain_stats.reindex(strain_weight.index)
            strain_stats.loc[strain_weight.index, 'total_weight'] = strain_weight

            # Increment strain sold statistics.
            strain_stats = strain_stats.reindex(strain_sold.index)
            strain_stats.loc[strain_sold.index, 'total_sold'] = strain_sold

        # Add strain type.
        flower_types = flower.groupby('strain_name')['strain_type'].first()
        # FIXME: This raises a warning on the 1st iteration.
        strain_stats.loc[flower_types.index, 'strain_type'] = flower_types

    # Save the strain statistics.
    strains_dir = os.path.join(stats_dir, 'strains')
    if not os.path.exists(strains_dir): os.makedirs(strains_dir)
    outfile = os.path.join(strains_dir, 'strain-statistics.xlsx')
    strain_stats.to_excel(outfile)

    # Complete strains curation.
    end = datetime.now()
    print('✓ Finished curating strains in', end - start)
    return strain_stats


# === Test ===
# [✓] Tested: 2023-08-14 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    data_dir = f'{base}\\June 2023 CCRS Monthly Reports\\June 2023 CCRS Monthly Reports\\'
    stats_dir = f'{base}\\ccrs-stats\\'
    curate_ccrs_strains(data_dir, stats_dir)
