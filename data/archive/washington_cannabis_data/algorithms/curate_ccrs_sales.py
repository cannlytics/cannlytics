"""
Curate CCRS Sales
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/1/2023
Updated: 4/17/2023
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
from typing import  Optional

# External imports:
from cannlytics.data.ccrs import (
    get_datafiles,
    merge_datasets,
    standardize_dataset,
    unzip_datafiles,
)
from cannlytics.data.ccrs.ccrs import anonymize
from cannlytics.data.ccrs.constants import CCRS_DATASETS
from cannlytics.utils import camel_to_snake, rmerge, sorted_nicely
import pandas as pd


def calc_daily_sales(
        df: pd.DataFrame,
        stats: dict,
    ) -> dict:
    """Calculate sales by licensee by day.
    Note: The absolute value of the `Discount` is used.
    """
    group = ['licensee_id', 'sale_date']
    daily = df.groupby(group, as_index=False).sum()
    for _, row in daily.iterrows():
        licensee_id = row['licensee_id']
        date = row['sale_date'].isoformat()[:10]
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
        df: pd.DataFrame,
        data_dir: str,
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
        licensee_items = df.loc[df['licensee_id'] == index]
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
            month_items.sort_index(axis=1).to_excel(outfile, index=False)
            if verbose:
                print('Saved', licensee_id, month, 'items:', len(month_items))


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


# def curate_ccrs_sales(
#         data_dir,
#         stats_dir,
#         reverse: Optional[bool] = False,
#         first_file: Optional[int] = 0,
#         last_file: Optional[int] = None,
#     ):
#     """Curate CCRS sales by merging additional datasets."""

# DEV:
if __name__ == '__main__':

    base = 'D:\\data\\washington\\'
    data_dir = f'{base}\\CCRS PRR (3-6-23)\\CCRS PRR (3-6-23)\\'
    stats_dir = f'{base}\\ccrs-stats\\'
    first_file = 3
    last_file = None
    reverse = False

    print('Curating sales...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(data_dir)

    # Create stats directory if it doesn't already exist.
    licensees_dir = os.path.join(stats_dir, 'licensee_stats')
    sales_dir = os.path.join(stats_dir, 'sales')
    if not os.path.exists(licensees_dir): os.makedirs(licensees_dir)
    if not os.path.exists(stats_dir): os.makedirs(sales_dir)

    # Define all sales fields.
    # Note: `IsDeleted` throws a ValueError if it's a bool.
    fields = CCRS_DATASETS['sale_details']['fields']
    date_fields = CCRS_DATASETS['sale_details']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    item_types['IsDeleted'] = 'string'

    # Iterate over all sales items files to calculate stats.
    daily_licensee_sales = {}
    inventory_dir = os.path.join(stats_dir, 'inventory')
    inventory_files = sorted_nicely(os.listdir(inventory_dir))
    sales_items_files = get_datafiles(data_dir, 'SalesDetail_')
    if last_file: sales_items_files = sales_items_files[:last_file]
    if reverse:
        sales_items_files.reverse()
    for i, datafile in enumerate(sales_items_files[first_file:]):
        print('Augmenting:', datafile)
        midpoint_start = datetime.now()

        # Read in the sales items.
        items = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            parse_dates=date_fields,
            usecols=item_cols,
            dtype=item_types,
        )

        # Remove any sales items that were deleted.
        items = items.loc[
            (items['IsDeleted'] != 'True') &
            (items['IsDeleted'] != True)
        ]

        # Iterate over the sales headers until all items have been augmented.
        # Note: There is probably a clever way to reduce the number of times
        # that the headers are read. Currently reads all sale headers from
        # current to earliest then reads earliest to current for the
        # 2nd half to try to reduce unnecessary reads.
        if i < len(sales_items_files) / 2:
            sale_headers_files = get_datafiles(data_dir, 'SaleHeader_')
        else:
            sale_headers_files = get_datafiles(data_dir, 'SaleHeader_', desc=False)
        print('Merging sale header data...')
        items = merge_datasets(
            items,
            sale_headers_files,
            dataset='sale_headers',
            on='SaleHeaderId',
            target='LicenseeId',
            how='left',
            validate='m:1',
        )

        # Standardize inventory items.
        items = standardize_dataset(items)

        # Augment with curated inventory.
        print('Merging inventory data...')
        for datafile in inventory_files:

            # Read inventory data file.
            try:
                data = pd.read_excel(os.path.join(inventory_dir, datafile))
            except:
                continue

            # Remove inventory item duplicates.
            # FIXME: Why are there duplicates?
            data['inventory_id'] = data['inventory_id'].astype(str)
            data.drop_duplicates(subset='inventory_id', keep='first', inplace=True)
            
            # Merge inventory data with sales data.
            items = rmerge(
                items,
                data,
                on='inventory_id',
                how='left',
                validate='m:1',
            )

        # At this stage, sales by licensee by day can be incremented.
        print('Updating sales statistics...')
        daily_licensee_sales = calc_daily_sales(items, daily_licensee_sales)

        # Save augmented sales to licensee-specific files by month.
        print('Saving augmented sales...')
        items['month'] = items['sale_date'].apply(lambda x: x.isoformat()[:7])
        save_licensee_items_by_month(
            items,
            licensees_dir,
            subset='sale_detail_id',
            verbose=False,
            # FIXME: Pass item date columns and types.
            # parse_dates=list(set(date_fields + supp_date_fields)),
            # dtype={**supp_types, **item_types},
        )
        midpoint_end = datetime.now()
        print('Curated sales file in:', midpoint_end - midpoint_start)

    # Compile the sales statistics.
    print('Compiling licensee sales statistics...')
    stats = stats_to_df(daily_licensee_sales)

    # Save the compiled statistics.
    min_date = stats['date'].min()
    max_date = stats['date'].max()
    stats_file = f'{sales_dir}/sales-by-licensee-{min_date}-to-{max_date}.xlsx'
    stats.to_excel(stats_file, index=False)

    # Save the statistics by month.
    save_stats_by_month(stats, sales_dir, 'sales-by-licensee')

    # Future work: Calculate and save aggregate statistics.

    # Finish curating sales.
    end = datetime.now()
    print('✓ Finished curating sales in', end - start)


# === Test ===
if __name__ == '__main__':
    pass

    # Specify where your data lives.
    # base = 'D:\\data\\washington\\'
    # data_dir = f'{base}\\CCRS PRR (3-6-23)\\CCRS PRR (3-6-23)\\'
    # stats_dir = f'{base}\\ccrs-stats\\'
    # curate_ccrs_sales(
    #     data_dir,
    #     stats_dir,
    #     reverse=False,
    #     first_file=0,
    #     last_file=1,
    # )
