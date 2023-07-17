"""
Curate CCRS Inventory
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/1/2023
Updated: 5/30/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml>

"""
# Standard imports:
from datetime import datetime
import gc
import os
from typing import Optional

# External imports:
from cannlytics.data.ccrs import (
    CCRS_DATASETS,
    anonymize,
    get_datafiles,
    merge_datasets,
    save_dataset,
    unzip_datafiles,
)
from cannlytics.utils import camel_to_snake, rmerge, sorted_nicely
import pandas as pd


def read_items(
        datafile: str,
        item_cols: list,
        item_types: dict,
        date_fields: list,
    ):
    """Read CCRS inventory items and format accordingly."""
    items = pd.read_csv(
        datafile,
        sep='\t',
        encoding='utf-16',
        parse_dates=date_fields,
        usecols=item_cols,
        dtype=item_types,
    )
    return items.rename(columns={
        'CreatedBy': 'inventory_created_by',
        'UpdatedBy': 'inventory_updated_by',
        'CreatedDate': 'inventory_created_at',
        'updatedDate': 'inventory_updated_at',
        'UpdatedDate': 'inventory_updated_at',
        'Name': 'inventory_name',
    })


def read_licensees(data_dir: str):
    """Read CCRS licensees data and format accordingly."""
    licensees = pd.read_csv(
        f'{data_dir}/Licensee_0/Licensee_0/Licensee_0.csv',
        sep='\t',
        encoding='utf-16',
        usecols=['LicenseeId', 'Name', 'DBA'],
        dtype={
            'LicenseeId': 'string',
            'Name': 'string',
            'DBA': 'string',
        },
    )
    columns = {'Name': 'licensee_name', 'DBA': 'licensee_dba'}
    return licensees.rename(columns, axis=1)


def merge_lab_results(
        results_file: str,
        directory: str,
        on: Optional[str] = 'inventory_id',
        target: Optional[str] = 'lab_result_id',
        verbose: Optional[bool] = True,
    ) -> pd.DataFrame:
    """Merge lab results with items in a given directory."""

    # Read the lab results.
    lab_results = pd.read_excel(results_file)

    # Clean the lab results
    # lab_results.rename(columns={
    #     'inventory_id': 'InventoryId',
    #     'lab_result_id': target,
    # }, inplace=True)
    lab_results[on] = lab_results[on].astype(str)

    # Iterate over all datafiles in the directory.
    matched = pd.DataFrame()
    datafiles = sorted_nicely(os.listdir(directory))
    for datafile in datafiles:

        # Skip temporary files.
        if datafile.startswith('~$'):
            continue

        # Merge the lab results with the datafile.
        data = pd.read_excel(os.path.join(directory, datafile))
        data[on] = data[on].astype(str)
        match = rmerge(
            data,
            lab_results,
            on=on,
            how='left',
            validate='m:1',
        )
        match = match.loc[~match[target].isna()]
        matched = pd.concat([matched, match], ignore_index=True)
        if verbose:
            print('Matched', len(matched), 'lab results...')
    
    # Return the matched lab results.
    return matched


def merge_licensees(items, licensees):
    """Merge licensees with inventory items using `LicenseeId`."""
    return rmerge(
        items,
        licensees,
        on='LicenseeId',
        how='left',
        validate='m:1',
    )


def merge_products(items, product_files):
    """Merge products with inventory items using `ProductId`."""
    return merge_datasets(
        items,
        product_files,
        dataset='products',
        on='ProductId',
        target='InventoryType',
        how='left',
        # FIXME: This may not be right.
        validate='m:1',
        rename={
            'CreatedDate': 'product_created_at',
            'updatedDate': 'product_updated_at',
            'UpdatedDate': 'product_updated_at',
            'ExternalIdentifier': 'product_external_id',
            'LicenseeId': 'producer_licensee_id',
            'Name': 'product_name',
            'Description': 'product_description',
        },
    )


def merge_strains(items, strain_files):
    """Merge strains with inventory items using `StrainId`."""
    items = merge_datasets(
        items,
        strain_files,
        dataset='strains',
        on='StrainId',
        target='strain_name',
        how='left',
        validate='m:1',
        rename={
            'Name': 'strain_name',
            'CreatedDate': 'strain_created_date',
        },
        drop=['CreatedBy', 'UpdatedBy', 'UpdatedDate'],
        dedupe=True,
    )
    missing = (items['strain_name'] == False) | (items['strain_name'] == 'False')
    items.loc[missing, 'strain_name'] = items.loc[missing, 'StrainType']
    items.loc[missing, 'StrainType'] = None
    return items


def merge_areas(items, area_files):
    """Merge areas with inventory items using `AreaId`."""
    return merge_datasets(
        items,
        area_files,
        dataset='areas',
        on='AreaId',
        target='AreaId',
        how='left',
        validate='m:1',
        rename={'Name': 'area_name'},
        drop=['LicenseeId', 'IsQuarantine', 'ExternalIdentifier',
        'IsDeleted', 'CreatedBy', 'CreatedDate', 'UpdatedBy', 'UpdatedDate']
    )


def curate_ccrs_inventory(data_dir, stats_dir):
    """Curate CCRS inventory by merging additional datasets."""

    print('Curating inventory...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(data_dir)

    # Create stats directory if it doesn't already exist.
    inventory_dir = os.path.join(stats_dir, 'inventory')
    if not os.path.exists(inventory_dir): os.makedirs(inventory_dir)

    # Read licensees data.
    licensees = read_licensees(data_dir)

    # Define all fields.
    fields = CCRS_DATASETS['inventory']['fields']
    date_fields = CCRS_DATASETS['inventory']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}

    # Note: `IsDeleted` throws a `ValueError` if defined as a bool.
    item_types['IsDeleted'] = 'string'

    # Get all datafiles.
    inventory_files = get_datafiles(data_dir, 'Inventory_')
    product_files = get_datafiles(data_dir, 'Product_')
    strain_files = get_datafiles(data_dir, 'Strains_')
    area_files = get_datafiles(data_dir, 'Areas_')

    # Curate inventory datafiles.
    print(len(inventory_files), 'datafiles to curate.')
    print('Estimated runtime:', len(inventory_files) * 0.25 + 1.5, 'hours')
    for i, datafile in enumerate(inventory_files):

        # Read in the items.
        print('Augmenting:', datafile)
        items = read_items(datafile, item_cols, item_types, date_fields)

        # Merge licensee data.
        print('Merging licensee data...')
        items = merge_licensees(items, licensees)

        # Merge product data.
        print('Merging product data...')
        items = merge_products(items, product_files)

        # Merge strain data.
        print('Merging strain data...')
        items = merge_strains(items, strain_files)

        # Merge area data.
        print('Merging area data...')
        items = merge_areas(items, area_files)

        # Standardize column names.
        items.rename(
            columns={col: camel_to_snake(col) for col in items.columns},
            inplace=True
        )

        # Anonymize the data.
        items = anonymize(items)

        # Save the curated inventory data.
        print('Saving curated inventory data...')
        outfile = os.path.join(inventory_dir, f'inventory_{i}.xlsx')
        items.to_excel(outfile, index=False)
        print('Curated inventory datafile:', i + 1, '/', len(inventory_files))

        # Perform garbage cleaning.
        gc.collect()

    # Merge and save inventory data with curated lab result data.
    try:
        print('Merging lab results...')
        inventory_dir = os.path.join(stats_dir, 'inventory')
        inventory_files = sorted_nicely(os.listdir(inventory_dir))
        lab_results_dir = os.path.join(stats_dir, 'lab_results')
        results_file = os.path.join(lab_results_dir, 'lab_results_0.xlsx')
        matched = merge_lab_results(results_file, inventory_dir)
        matched.rename(columns=lambda x: camel_to_snake(x), inplace=True)
        save_dataset(matched, lab_results_dir, 'inventory_lab_results')
        print('Merged inventory items with curated lab results.')
    except:
        print('Failed to merge lab results. Curate lab results first.')

    # Complete curation.
    end = datetime.now()
    print('✓ Finished curating inventory in', end - start)


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    data_dir = f'{base}\\CCRS PRR (6-6-23)\\CCRS PRR (6-6-23)\\'
    stats_dir = f'{base}\\ccrs-stats\\'
    curate_ccrs_inventory(data_dir, stats_dir)
