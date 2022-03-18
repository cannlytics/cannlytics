"""
Augment Washington State Leaf Traceability Sales Data
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/29/2022
Updated: 2/4/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: This script calculates various statistics from the sales data using
relevant fields from the lab results, licensees, inventories,
inventory types, and strains datasets.

Data sources:

    - WA State Traceability Data January 2018 - November 2021
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=1
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=2

Data Guide:

    - Washington State Leaf Data Systems Guide
    https://lcb.wa.gov/sites/default/files/publications/Marijuana/traceability/WALeafDataSystems_UserManual_v1.37.5_AddendumC_LicenseeUser.pdf

Data available at:

    - https://cannlytics.com/data/market/augmented-washington-state-sales
"""
# Standard imports.
from datetime import datetime
import gc
import json
from typing import Any, Optional

# External imports.
import pandas as pd

# Internal imports
from utils import format_millions, get_number_of_lines


def augment_dataset(
        data: Any,
        data_file: str,
        fields: dict,
        merge_key: str,
        match_key: Optional[str] = 'global_id',
        chunk_size: Optional[int] = 1_000_000,
        row_count: Optional[int] = None,
        sep: Optional[str] = '\t',
        encoding: Optional[str] = 'utf-16',
        date_columns: Optional[list] = None,
) -> Any:
    """Augment a given dataset with another dataset from its datafile, by
    follwing these steps:
        1. Read in a chunk of the augmenting dataset and iterate until all of
            its rows are read;
        2. Merge the chunk of augmenting data with the data to be augmented;
        3. Keep the augmented data.
    Args:
        data (DataFrame): The data to be augmented.
        data_file (str): The file name of the dataset used for augmenting.
        fields (dict): A dictionary of fields to merge from the augmenting dataset.
        merge_key (str): The field in the data being augmented to merge on.
        match_key (str): The field in the augmenting data to merge on,
            `global_id` by default (optional).
        chunk_size (int): The number of rows to read in the augmenting dataset
            at 1 time (optional).
        row_count (int): The number of rows in the augmenting datafile (optional).
        sep (str): The type of separation in the augmenting datafile (optional).
        encoding (str): The type of encoding of the augmenting datafile (optional).
        date_columns (list): A list of date columns in the augmenting datafile (optional).
    Returns:
    """
    read_rows = 0
    skiprows = None
    columns = list(fields.keys())
    if date_columns:
        columns += date_columns
    if row_count is None:
        row_count = get_number_of_lines(data_file)
    while read_rows < row_count:
        if read_rows:
            skiprows = [i for i in range(1, read_rows)]
        shard = pd.read_csv(
            data_file,
            sep=sep,
            encoding=encoding,
            usecols=columns,
            dtype=fields,
            skiprows=skiprows,
            nrows=chunk_size,
            parse_dates=date_columns,
        )
        match_columns = {}
        match_columns[match_key] = merge_key
        shard.rename(
            columns=match_columns,
            inplace=True,
        )
        data = pd.merge(
            left=data,
            right=shard,
            how='left',
            left_on=merge_key,
            right_on=merge_key,
        )
        column_names = list(data.columns)
        drop_columns = []
        rename_columns = {}
        for name in column_names:
            if name.endswith('_y'):
                drop_columns.append(name)
            if name.endswith('_x'):
                rename_columns[name] = name.replace('_x', '')
        try:
            data.drop(drop_columns, axis=1, inplace=True, errors='ignore')
        except TypeError:
            pass
        try:
            data.rename(columns=rename_columns, inplace=True)
        except TypeError:
            pass
        read_rows += chunk_size
        percent_read = round(read_rows / row_count * 100)
        print('Augmented %i / %i (%i%%) observations from %s' %
              (format_millions(read_rows), format_millions(row_count),
               percent_read, data_file))
    del shard
    gc.collect()
    return data


#------------------------------------------------------------------------------
# Read sales data.
#------------------------------------------------------------------------------

# Specify the sales items needed.
sales_items_fields = {
    'mme_id': 'string',
    'inventory_id': 'string',
    'qty': 'float',
    'uom': 'string',
    'price_total': 'float',
    'name': 'string',
}
sales_items_date_fields = [
    'created_at',
]

# Specify the time range to calculate statistics.
time_range = pd.date_range(start='2021-02-01', end='2021-11-30')

# Specify the series to be collected.
augmented_sales_items = []
daily_total_sales = {}
total_sales_by_retailer = {}

# Iterate over all of the sales items.
sales_chunk_size = 10_000_001
sale_items_datasets = [
    {'file_name': 'D:/leaf-data/SaleItems_0.csv', 'rows': 90_000_001},
    {'file_name': 'D:/leaf-data/SaleItems_1.csv', 'rows': 90_000_001},
    {'file_name': 'D:/leaf-data/SaleItems_2.csv', 'rows': 90_000_001},
    {'file_name': 'D:/leaf-data/SaleItems_3.csv', 'rows': 76_844_111},
]
start_time = datetime.now()
for dataset in sale_items_datasets:

    skip_rows = None
    rows_read = 0
    number_of_rows = dataset['rows']
    file_name = dataset['file_name']
    while rows_read < number_of_rows:

        # Define the chunk size.
        if rows_read > 0:
            skip_rows = [i for i in range(1, rows_read)]

        # Read in the chunk of sales.
        sale_items = pd.read_csv(
            file_name,
            sep='\t',
            encoding='utf-16',
            usecols=list(sales_items_fields.keys()) + sales_items_date_fields,
            dtype=sales_items_fields,
            parse_dates=sales_items_date_fields,
            nrows=sales_chunk_size,
            skiprows=skip_rows,
        )
        sale_items.rename(
            columns={'name': 'product_name'},
            inplace=True,
        )

        # Merge sale_items inventory_id to inventories inventory_id.
        sale_items = augment_dataset(
            sale_items,
            data_file='D:/leaf-data/Inventories_0.csv',
            fields={
                'global_id': 'string',
                'strain_id': 'string',
                'inventory_type_id': 'string',
                'lab_result_id': 'string',
            },
            merge_key='inventory_id',
            chunk_size=13_000_000,
            row_count=129_920_072,
            # chunk_size=1_000_000,
            # row_count=2_000_000,
        )

        # Get inventory type (global_id) with inventory_type_id to get
        # name and intermediate_type.
        sale_items = augment_dataset(
            sale_items,
            data_file='D:/leaf-data/InventoryTypes_0.csv',
            fields={
                'global_id': 'string',
                'name': 'string',
                'intermediate_type': 'string',
            },
            merge_key='inventory_type_id',
            chunk_size=28_510_000,
            row_count=57_016_229,
            # chunk_size=1_000_000,
            # row_count=2_000_000,
        )
        sale_items.rename(
            columns={'name': 'inventory_type_name'},
            inplace=True,
        )

        # TODO: Make this into a function.
        # Match with augmented lab results to get total_cannabinoids.
        # lab_result_fields = {
        #     'lab_result_id': 'string',
        #     'total_cannabinoids': 'float',
        # }
        # lab_results = pd.read_csv(
        #     'D:/leaf-data/augmented/augmented-washington-state-lab-results.csv',
        #     usecols=list(lab_result_fields.keys()),
        #     dtype=lab_result_fields,
        #     # nrows=1000,
        # )
        # sale_items = pd.merge(
        #     left=sale_items,
        #     right=lab_results,
        #     how='left',
        #     left_on='lab_result_id',
        #     right_on='lab_result_id',
        # )

        # Optional: Lookup inventory_type_id with strain_id if the
        # inventory type is not yet identified.

        # TODO: Calculate time between tested and sold (shelf-life).

        # TODO: Keep track of that intermediate_type sales.

        # TODO: Keep track of total_cannabinoids, lab_result_id, and total_price.

        # TODO: Iterate over the time range.
        for date in time_range:

            day = date.date()

            # Get the day's sales.
            day_sales = sale_items.loc[
                sale_items['created_at'] == date
            ]

            #  Add price_total to the daily total sales.
            existing_stats = daily_total_sales.get(day, {'total': 0})
            existing_sales = existing_stats['total']
            total_sales = day_sales['price_total'].sum()
            daily_total_sales[day] = {'total': existing_sales + total_sales}

            # TODO: Add price_total to daily sales by type.

            # TODO: Add price_total to daily sales by retailer.

            # Optional: Keep track of number of items sold.

            # Optional: Keep track of the quantity sold.

            # TODO: Keep track of average daily price by type.

            # TODO: If contains THC, Keep track of average price per mg of THC.

            # TODO: If contains CBD, Keep track of average price per mg of CBD.

            # Optional: Keep track of shelf-life (time from testing to sale).

            print('Updated stats for', day)

        # TODO: Save augmented sale items.

    # Keep track of the sale items read.
    rows_read += sales_chunk_size
    percent_read = round(rows_read / number_of_rows * 100)
    print('Processed %i / %i (%i%%) of %s.' %
          (format_millions(rows_read), format_millions(number_of_rows),
           percent_read, file_name))
    run_time = datetime.now() - start_time
    print('Run time:', run_time)


# TODO: Save the daily total sales series.
# daily_plant_data = pd.DataFrame(daily_plant_count)
# daily_plant_data.columns = ['date', 'total_plants', 'total_cultivators']
# daily_plant_data.to_csv('D:/leaf-data/augmented/daily_plant_data_2020c.csv')

# TODO: Save the daily sales by licensee.
# panel_plant_data = pd.DataFrame(plant_panel)
# panel_plant_data.to_csv('D:/leaf-data/augmented/daily_licensee_plant_data_2020c.csv')


#------------------------------------------------------------------------------
# TODO: Augment sales data with licensee data.
#------------------------------------------------------------------------------

# Merge mme_id to mme_id to get information about the retailer:
# - latitude, longitude, name.

# # Add code variable to lab results with IDs.
# results_with_ids['code'] = results_with_ids['global_for_inventory_id'].map(
#     lambda x: x[x.find('WA'):x.find('.')]
# ).str.replace('WA', '')

# # Specify the licensee fields.
# licensee_fields = {
#     'global_id' : 'string',
#     'code': 'string',
#     'name': 'string',
#     'type': 'string',
#     'address1': 'string',
#     'address2': 'string',
#     'city': 'string',
#     'state_code': 'string',
#     'postal_code': 'string',
# }
# licensee_date_fields = [
#     'created_at', # No records if issued before 2018-02-21.
# ]
# licensee_columns = list(licensee_fields.keys()) + licensee_date_fields

# # # Read in the licensee data.
# licensees = pd.read_csv(
#     # '../.datasets/Licensees_0.csv',
#     '../.datasets/geocoded_licensee_data.csv',
#     # sep='\t',
#     # encoding='utf-16',
#     usecols=licensee_columns,
#     dtype=licensee_fields,
#     parse_dates=licensee_date_fields,
# )

# # Format the licensees data.
# licensees.rename(columns={
#     'global_id': 'mme_id',
#     'created_at': 'license_created_at',
#     'type': 'license_type',
# }, inplace=True)

# # Combine the data sets.
# results_with_ids = pd.merge(
#     left=results_with_ids,
#     right=licensees,
#     how='left',
#     left_on='code',
#     right_on='code'
# )
# results_with_ids.rename(columns={'global_id_x': 'global_id'}, inplace=True)
# results_with_ids.drop(['global_id_y'], axis=1, inplace=True, errors='ignore')

# # Save lab results enhanced with additional fields.
# results_with_ids.to_csv('../.datasets/lab_results_with_licensee_data.csv')


#------------------------------------------------------------------------------
# Calculate sales statistics.
#------------------------------------------------------------------------------

# TODO: Aggregate total_transaction, total_revenue, and average_price
# for each lab result.

# Using total sales by day, estimate if there is a day of the week effect?
# Null hypothesis: There is no statistical difference in sales depending on the day of the week.
# Alternative hypothesis: There is a statistical difference in sales depending on the day of the week.


# What is the total amount of cannabinoids consumed in Washington Sate over time?


# In mg/g, assuming dumptrucks of 100% cannabinoid concentrate, then how many
# dumptrucks a year are Washingtonians consuming?


# Answer the age old questions, does THC matter? If so, then how much?
# My hypothesis is that there is a direct linear relationship between THC
# concentration demanded by people and its price.

# Run a regression of total sales for a given lab result and it's total cannabinoids.


# Plot the regression of sales on THC.
# Y-Axis Avg. price per mg/g of THC (of goods with THC)
# X-Axis g of THC produced


# Similarly, plot the regression of sales on CBD
# Y-Axis Ag price per mg/g of CBD (of goods with CBD)
# X-Axis g of CBD produced

# Estimate an inverse demand function
# price_thc = y_0 + b_0 quantity_thc + u_t


# Estimate a regression of price on total_cannabinoids ***


#------------------------------------------------------------------------------
# TODO: Visualize sales data.
#------------------------------------------------------------------------------

# Plot monthly sales by retailer for a time lapse video.


# Plot average price of various products over time.


# Plot the market share of various products over time.


