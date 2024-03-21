"""
Curate CCRS Sales
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/1/2023
Updated: 8/29/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/plb3dr2fvsuvgixb38g10tbwqos73biz>

"""
# Standard imports:
from datetime import datetime
import gc
import os
from typing import  List, Optional

import numpy as np

# External imports:
from cannlytics.data.ccrs import (
    CCRS,
    CCRS_DATASETS,
    get_datafiles,
    merge_datasets,
    standardize_dataset,
    unzip_datafiles,
)
from cannlytics.utils import camel_to_snake, rmerge, sorted_nicely
import pandas as pd


def aggregate_monthly_sales(
        data_dir: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
    """Aggregate sales items by month."""

    # Determine the month range.
    months = []
    count = (end.year - start.year) * 12 + (end.month - start.month) + 1
    for i in range(count):
        year = start.year + (start.month + i - 1) // 12
        month = (start.month + i - 1) % 12 + 1
        iso_month = f'{year}-{month:02d}'
        months.append(iso_month)

    # Iterate over months.
    for month in months:

        # Read all sales items for the month.
        month_data = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(f'{month}.xlsx'):
                    file_path = os.path.join(root, file)
                    month_data.append(pd.read_excel(file_path))

        # Save the aggregated sales items for the month.
        month_data = pd.concat(month_data)
        outfile = os.path.join(data_dir, f'sales-items-{month}.xlsx')
        month_data.to_excel(outfile, index=False)


def calc_daily_sales(
        df: pd.DataFrame,
        stats: dict,
    ) -> dict:
    """Calculate sales by licensee by day.
    Note: The absolute value of the `Discount` is used.
    """
    group = ['licensee_id', 'sale_date']
    sum_columns = ['unit_price', 'discount', 'sales_tax', 'other_tax']  # replace with your column names
    daily = df.groupby(group, as_index=False)[sum_columns].sum()
    for _, row in daily.iterrows():
        licensee_id = row['licensee_id']
        date = row['sale_date'][:10]
        licensee_data = stats.get(licensee_id, {})
        date_data = licensee_data.get(date, {})
        licensee_data[date] = {
            'total_price': date_data.get('total_price', 0) + row['unit_price'],
            'total_discount': date_data.get('total_discount', 0) + abs(row['discount']),
            'total_sales_tax': date_data.get('total_sales_tax', 0) + row['sales_tax'],
            'total_other_tax': date_data.get('total_other_tax', 0) + row['other_tax'],
        }
        stats[licensee_id] = licensee_data
    return stats


def save_licensee_items_by_month(
        manager: CCRS,
        df: pd.DataFrame,
        data_dir: str,
        key: str = 'licensee_id',
        item_type: Optional[str] = 'sales',
        subset: Optional[str] = '',
        parse_dates: Optional[list] =None,
        dtype: Optional[dict] = None,
        verbose: Optional[bool] = True,
    ) -> None:
    """Save items by licensee by month to licensee-specific directories.
    Note: Datafiles must be under 1 million items.
    """
    licensees = list(df['licensee_id'].unique())
    for index in licensees:
        if isinstance(index, float):
            try:
                licensee_id = str(int(index))
            except ValueError:
                licensee_id = str(index)
        else:
            licensee_id = index
        licensee_dir = os.path.join(data_dir, licensee_id)
        if not os.path.exists(licensee_dir): os.makedirs(licensee_dir)
        licensee_items = df.loc[df[key] == index]
        months = list(licensee_items['month'].unique())
        for month in months:
            outfile = f'{licensee_dir}/{item_type}-{licensee_id}-{month}.xlsx'
            month_items = licensee_items.loc[licensee_items['month'] == month]
            try:
                existing_items = pd.read_excel(
                    outfile,
                    parse_dates=parse_dates,
                    dtype=dtype,
                )
                month_items = pd.concat([existing_items, month_items])
                month_items[subset] = month_items[subset].astype(str)
                month_items.drop_duplicates(subset=subset, keep='last', inplace=True)
            except FileNotFoundError:
                pass
            except ValueError as e:
                manager.create_log(f'Error reading Excel file: {e}')
            month_items.sort_index(axis=1).to_excel(outfile, index=False)
            if verbose:
                manager.create_log(f'Saved: {licensee_id} {month} {len(month_items)}')


def save_stats_by_month(
        df: pd.DataFrame,
        data_dir: str,
        series: str,
    ) -> None:
    """Save given series statistics by month to given data directory."""
    df['month'] = df['date'].apply(lambda x: x[:7])
    months = list(df['month'].unique())
    for month in months:
        outfile = f'{data_dir}/{series}-{month}.xlsx'
        month_stats = df.loc[df['month'] == month]
        month_stats.to_excel(outfile, index=False)


def stats_to_df(stats: dict[dict]) -> pd.DataFrame:
    """Compile statistics from a dictionary of dictionaries into a DataFrame."""
    data = []
    for index, dates in stats.items():
        for date, values in dates.items():
            data.append({
                'licensee_id': index,
                'date': date,
                **values,
            })
    return pd.DataFrame(data)


def ripple_list(file_paths, n):
    """
    Given a list of file paths and a starting point 'n', generates an
    ordered list of dataset paths spiraling outwards. The order starts
    at the given index 'n' and then alternates between one less and one
    greater, continuing to spiral out from the initial index.

    Args:
        file_paths (list): The list of file paths.
        n (int): The starting index for the datasets.

    Returns:
        list: A list of dataset paths in the order they should be
        searched, starting from 'n' and spiraling outwards.

    Example:
        file_paths = ['file_path_0', 'file_path_1', ..., 'file_path_96']
        ripple_list(file_paths, 25)
        >> ['file_path_25', 'file_path_24', 'file_path_26', 'file_path_23', 'file_path_27', ... , 'file_path_96']
    """
    dataset_paths = []
    dataset_paths.append(file_paths[n])
    left, right = n - 1, n + 1
    total_paths = len(file_paths)
    while left >= 0 or right < total_paths:
        if left >= 0:
            dataset_paths.append(file_paths[left])
            left -= 1
        if right < total_paths:
            dataset_paths.append(file_paths[right])
            right += 1
    return dataset_paths


def curate_ccrs_sales(
        data_dir,
        stats_dir,
        reverse: Optional[bool] = False,
        first_file: Optional[int] = 0,
        last_file: Optional[int] = None,
        manager: Optional[CCRS] = None,
        release: Optional[str] = '',
        skip_existing: Optional[bool] = True,
    ):
    """Curate CCRS sales by merging additional datasets."""

    # Initialize.
    if manager is None:
        manager = CCRS()
    manager.create_log('Curating sales...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(data_dir)

    # Create stats directory if it doesn't already exist.
    licensees_dir = os.path.join(stats_dir, 'licensee_stats')
    sales_stats_dir = os.path.join(stats_dir, f'sales-stats-{release}')
    sales_dir = os.path.join(stats_dir, f'sales-{release}')
    if not os.path.exists(licensees_dir): os.makedirs(licensees_dir)
    if not os.path.exists(sales_dir): os.makedirs(sales_dir)
    if not os.path.exists(sales_stats_dir): os.makedirs(sales_stats_dir)

    # Define all sales fields.
    # Note: `IsDeleted` throws a ValueError if it's a bool.
    fields = CCRS_DATASETS['sale_details']['fields']
    date_fields = CCRS_DATASETS['sale_details']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    item_types['IsDeleted'] = 'string'

    # Get all datafiles.
    inventory_dir = os.path.join(stats_dir, f'inventory-{release}')
    inventory_files = sorted_nicely(os.listdir(inventory_dir))
    sales_items_files = get_datafiles(data_dir, 'SalesDetail_')
    # lab_results_dir = os.path.join(stats_dir, 'lab_results')
    # results_file = os.path.join(lab_results_dir, 'inventory_lab_results_0.xlsx')

    # Iterate over all sales items files to calculate stats.
    # daily_licensee_sales = {}
    if last_file: sales_items_files = sales_items_files[:last_file]
    if reverse:
        sales_items_files.reverse()
    for datafile in sales_items_files[first_file:]:

        # Skip already curated files.
        basename = datafile.split('/')[-1]
        index = int(basename.split('_')[-1].split('.')[0])
        outfile = os.path.join(sales_dir, f'sales_{index}.csv')
        if os.path.exists(outfile) and skip_existing:
            manager.create_log('Skipping already curated file: ' + datafile)
            continue

        # Read in the sales items.
        manager.create_log(f'Augmenting: {datafile}')
        midpoint_start = datetime.now()
        try:
            items = pd.read_csv(
                datafile,
                sep='\t',
                encoding='utf-16',
                parse_dates=date_fields,
                usecols=item_cols,
                dtype=item_types,
            )
        except Exception as e:
            manager.create_log('Failed to read sales items: ' + str(e))
            continue

        # Remove any sales items that were deleted.
        items = items.loc[
            (items['IsDeleted'] != 'True') &
            (items['IsDeleted'] != True)
        ]

        # Efficiently order sales headers.
        manager.create_log('Merging sale header data...')
        sale_headers_files = get_datafiles(data_dir, 'SaleHeader_', desc=False)
        try:
            sale_headers_files = ripple_list(sale_headers_files, index)
        except IndexError:
            pass

        # Iterate over the sales headers until all items have been augmented.
        items = merge_datasets(
            items,
            sale_headers_files,
            dataset='sale_headers',
            on='SaleHeaderId',
            target='LicenseeId',
            how='left',
            validate='m:1',
            rename={
                'CreatedDate': 'sale_created_date',
                'CreatedBy': 'sale_created_by',
                'UpdatedDate': 'sale_updated_date',
                'UpdatedBy': 'sale_updated_by',
                # 'LicenseeId': 'sale_licensee_id',
                'ExternalIdentifier': 'sale_external_id',
            },
            break_once_matched=False,
        )

        # Standardize inventory items.
        # items = standardize_dataset(items)
        items.rename(columns={col: camel_to_snake(col) for col in items.columns}, inplace=True)
        items.rename(columns={
            'external_identifier': 'sale_item_external_id',
            'created_by': 'sale_item_created_by',
            'created_date': 'sale_item_created_date',
            'updated_by': 'sale_item_updated_by',
            'updated_date': 'sale_item_updated_date',
            'licensee_id': 'sale_licensee_id',
        }, inplace=True)

        # Augment with curated inventory.
        manager.create_log('Merging inventory data...')
        items['strain_name'] = np.nan
        for datafile in inventory_files:

            # Read inventory data file.
            try:
                inventory_data = pd.read_excel(os.path.join(inventory_dir, datafile))
            except:
                continue

            # Remove inventory item duplicates.
            # FIXME: Why are there duplicates?
            inventory_data['inventory_id'] = inventory_data['inventory_id'].astype(str)
            inventory_data.drop_duplicates(subset='inventory_id', keep='first', inplace=True)

            # Clean the data.
            inventory_data['licensee_id'] = inventory_data['licensee_id'].astype(str)
            
            # FIXME: Account for product_id?

            # Merge inventory data with sales data.
            already_matched = items.loc[~items['strain_name'].isna()]
            unmatched = items.loc[items['strain_name'].isna()]
            matched = rmerge(
                unmatched,
                inventory_data,
                on='inventory_id',
                how='left',
                validate='m:1',
            )
            items = pd.concat([already_matched, matched])
            # matched = match.loc[~match[target].isna()]
            print('Strains matched:', len(items.loc[~items['strain_name'].isna()]))


        # # Augment with curated lab results.
        # # FIXME: This may be overwriting data points.
        # # Note: I think a product lab results file is needed.
        # manager.create_log('Merging lab result data...')
        # lab_results_columns = {
        #     'inventory_id': str,
        #     'lab_id': str,
        #     'created_by': str,
        #     'created_date': str,
        #     'updated_by': str,
        #     'updated_date': str,
        #     'delta_9_thc': str,
        #     'thca': str,
        #     'total_thc': str,
        #     'cbd': str,
        #     'cbda': str,
        #     'total_cbd': str,
        #     'moisture_content': str,
        #     'water_activity': str,
        #     'status': str,
        #     'results': str,
        #     'pesticides': str,
        #     'residual_solvents': str,
        #     'heavy_metals': str,
        # }
        # lab_results = pd.read_excel(
        #     results_file,
        #     usecols=list(lab_results_columns.keys()),
        #     dtype=lab_results_columns,
        # )
        # lab_results.rename(columns={
        #     'created_by': 'lab_result_created_by',
        #     'created_date': 'lab_result_created_date',
        #     'updated_by': 'lab_result_updated_by',
        #     'updated_date': 'lab_result_updated_date',
        # }, inplace=True)
        # # TODO: Convert certain values to numeric?
        # # lab_results['inventory_id'] = lab_results['inventory_id'].astype(str)
        # lab_results.drop_duplicates(subset='inventory_id', keep='first', inplace=True)
        # items = rmerge(
        #     items,
        #     lab_results,
        #     on='inventory_id',
        #     how='left',
        #     validate='m:1',
        # )
        # del lab_results
        # gc.collect()

        # Save the augmented sales items.
        manager.create_log('Saving augmented sales data...')
        items.to_csv(outfile, index=False)
        manager.create_log('Saved augmented sales datafile: ' + str(index))

        # Optional: Create a hash of the augmented sales data
        # and save a log of the hash and the datafile name.

        # # At this stage, sales by licensee by day can be incremented.
        # manager.create_log('Updating sales statistics...')
        # daily_licensee_sales = calc_daily_sales(items, daily_licensee_sales)

        # Save augmented sales to licensee-specific files by month.
        manager.create_log('Saving augmented sales by month...')
        items['month'] = items['sale_date'].apply(lambda x: x.isoformat()[:7])
        save_licensee_items_by_month(
            manager,
            items,
            licensees_dir,
            verbose=False,
            subset='sale_detail_id',
            key='sale_licensee_id',
        )
        save_licensee_items_by_month(
            manager,
            items,
            licensees_dir,
            verbose=False,
            subset='sale_detail_id',
            key='licensee_id',
        )
        midpoint_end = datetime.now()
        manager.create_log('Curated sales file in: ' + str(midpoint_end - midpoint_start))

    # === Deprecated ===

    # # Compile the sales statistics.
    # manager.create_log('Compiling licensee sales statistics...')
    # stats = stats_to_df(daily_licensee_sales)

    # # Save the compiled statistics.
    # min_date = stats['date'].min()
    # max_date = stats['date'].max()
    # stats_file = f'{sales_stats_dir}/sales-by-licensee-{min_date}-to-{max_date}.xlsx'
    # stats.to_excel(stats_file, index=False)

    # # Save the statistics by month.
    # save_stats_by_month(stats, sales_stats_dir, 'sales-by-licensee')

    # TODO: Calculate and save aggregate statistics.

    # Finish curating sales.
    end = datetime.now()
    manager.create_log('✓ Finished curating sales in ' + str(end - start))


def calculate_and_save_stats(
        manager: CCRS,
        file_paths: List[str],
        sales_stats_dir: str,
    ):
    """
    Iterates over a list of file paths, each representing sales items.
    Calculates daily sales statistics for each licensee, compiles these
    statistics, and saves the results to an Excel file in the specified directory.
    Also saves the monthly statistics for each licensee for easy future reference.

    Args:
        file_paths (list of str): List of file paths, each pointing to a file
            representing sales items.
        sales_stats_dir (str): Directory path where the sales statistics 
            Excel file should be saved.

    Returns:
        dict: Dictionary with the updated daily sales statistics for each licensee.
    """
    # Increment sales by licensee by day.
    daily_licensee_sales = {}
    for file_path in file_paths:
        manager.create_log(f'Updating sales statistics for {file_path}...')
        items = pd.read_csv(file_path)
        daily_licensee_sales = calc_daily_sales(items, daily_licensee_sales)

    # Compile the sales statistics.
    manager.create_log('Compiling licensee sales statistics...')
    stats = stats_to_df(daily_licensee_sales)

    # Save the compiled statistics.
    min_date = stats['date'].min()
    max_date = stats['date'].max()
    stats_file = f'{sales_stats_dir}/sales-by-licensee-{min_date}-to-{max_date}.xlsx'
    stats.to_excel(stats_file, index=False)

    # Save the statistics by month.
    save_stats_by_month(stats, sales_stats_dir, 'sales-by-licensee')
    manager.create_log('Saved sales statistics to: ' + stats_file)
    return daily_licensee_sales


# === Test ===
# [ ] Tested:
if __name__ == '__main__':

    # Parameters.
    manager = CCRS()
    first_file = 85
    last_file = None
    reverse = False
    skip_existing = True

    # Specify where your data lives.
    base = 'D://data/washington/'
    releases = [
        # 'CCRS PRR (3-6-23)',
        # 'CCRS PRR (4-4-23)',
        # 'CCRS PRR (5-7-23)',
        # 'CCRS PRR (6-6-23)',
        'CCRS PRR (8-4-23)',
        # 'CCRS PRR (9-5-23)',
        # 'CCRS PRR (11-2-23)',
        # 'CCRS PRR (12-2-23)',
        # 'CCRS PRR (1-2-24)',
        # 'CCRS PRR (2-2-24)',
    ]
    for release in reversed(releases):

        data_dir = f'{base}/{release}/{release}/'
        stats_dir = f'{base}/stats/'
        sales_dir = os.path.join(stats_dir, f'sales-{release}')
        sales_stats_dir = os.path.join(stats_dir, f'sales-stats-{release}')

        # Curate CCRS sales.
        # FIXME: The output data is not correct.
        curate_ccrs_sales(
            data_dir,
            stats_dir,
            reverse=reverse,
            first_file=first_file,
            last_file=last_file,
            manager=manager,
            release=release,
            skip_existing=skip_existing,
        )

        # Aggregate monthly sales items.
        # aggregate_monthly_sales(
        #     data_dir=f'{base}/ccrs-stats/sales_stats',
        #     start=pd.to_datetime('2023-01-01'),
        #     end=pd.to_datetime('2023-08-01'),
        # )

        # Calculate sales by licensee by day.
        augmented_files = sorted_nicely(os.listdir(sales_dir))
        augmented_files = [os.path.join(sales_dir, f) for f in augmented_files if not f.startswith('~$')]
        daily_licensee_sales = calculate_and_save_stats(
            manager=manager,
            file_paths=augmented_files,
            sales_stats_dir=sales_stats_dir,
        )
