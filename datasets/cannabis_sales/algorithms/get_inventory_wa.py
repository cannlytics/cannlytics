"""
Curate CCRS Inventory
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/1/2023
Updated: 7/28/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.box.com/s/d0g3mhtdyohhi4ic3zucekpnz017fy9o>

"""
# Standard imports:
from datetime import datetime
import gc
import os
from typing import Optional

# External imports:
from cannlytics.data.ccrs import (
    CCRS,
    CCRS_DATASETS,
    CURATED_CCRS_DATASETS,
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


def read_products(
        datafile: str,
        # item_cols: list,
        # item_types: dict,
        # date_fields: list,
    ):
    """Read CCRS inventory items and format accordingly."""
    fields = CCRS_DATASETS['products']['fields']
    parse_dates = CCRS_DATASETS['products']['date_fields']
    use_cols = list(fields.keys()) + parse_dates
    fields['UnitWeightGrams'] = 'string'
    fields['IsDeleted'] = 'string'
    fields['CreatedDate'] = 'string'
    fields['UpdatedDate'] = 'string'
    products = pd.read_csv(
        datafile,
        sep='\t',
        encoding='utf-16',
        parse_dates=parse_dates,
        usecols=use_cols,
        dtype=fields,
    )
    products = products.rename(columns={
        'CreatedBy': 'product_created_by',
        'UpdatedBy': 'product_updated_by',
        'CreatedDate': 'product_created_at',
        'updatedDate': 'product_updated_at',
        'UpdatedDate': 'product_updated_at',
        'Name': 'product_name',
        'Description': 'product_description',
        'LicenseeId': 'producer_license_number',
        'ExternalIdentifier': 'product_external_id',
    })
    products.rename(columns=lambda x: camel_to_snake(x), inplace=True)
    return products


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


def merge_licensees(items, licensees):
    """Merge licensees with inventory items using `LicenseeId`."""
    return rmerge(
        items,
        licensees,
        on='LicenseeId',
        how='left',
        validate='m:1',
    )


def merge_lab_results(
        manager: CCRS,
        results_file: str,
        directory: str,
        on: Optional[str] = 'inventory_id',
        target: Optional[str] = 'lab_result_id',
        verbose: Optional[bool] = True,
    ) -> pd.DataFrame:
    """Merge lab results with items in a given directory."""

    # Read the standardized lab results.
    lab_results = pd.read_excel(results_file)
    lab_results.rename(columns={
        'inventory_id': on,
        'lab_result_id': target,
    }, inplace=True)
    lab_results[on] = lab_results[on].astype(str)

    # Get inventory item fields.
    fields = CURATED_CCRS_DATASETS['inventory']['fields']
    parse_dates = CURATED_CCRS_DATASETS['inventory']['date_fields']
    use_cols = list(fields.keys()) + parse_dates

    # Iterate over all datafiles in the directory.
    matched = pd.DataFrame()
    datafiles = sorted_nicely(os.listdir(directory))
    for datafile in datafiles:
        if datafile.startswith('~$') or not datafile.endswith('.xlsx'):
            continue

        # Read the standardized inventory.
        filename = os.path.join(directory, datafile)
        data = pd.read_excel(
            filename,
            dtype=fields,
            parse_dates=parse_dates,
            usecols=use_cols,
        )
        data[on] = data[on].astype(str)
        
        # Merge the lab results with the datafile.
        match = rmerge(
            data,
            lab_results,
            on=on,
            how='left',
            validate='m:1',
        )

        # Record rows with matching lab results.
        match = match.loc[~match[target].isna()]
        matched = pd.concat([matched, match], ignore_index=True)
        if verbose:
            manager.create_log('Matched ' + str(len(matched)) + 'lab results...')
    
    # Return the matched lab results.
    return matched


def merge_lab_results_with_products(
        manager: CCRS,
        products,
        results_file: str,
        on: Optional[str] = 'ProductId',
        target: Optional[str] = 'lab_result_id',
        verbose: Optional[bool] = True,
    ):
    """Merge lab results with products data."""
    lab_results = pd.read_excel(results_file)
    lab_results[on] = lab_results[on].astype(str)
    merged_data = rmerge(
        products,
        lab_results,
        on=on,
        how='left',
        validate='m:1',
    )
    merged_data = merged_data.loc[~merged_data[target].isna()]
    if verbose: manager.create_log('Matched ' +  str(len(merged_data)) + ' lab results with products...')
    return merged_data


def merge_products(items, product_files):
    """Merge products with inventory items using `ProductId`."""
    items = merge_datasets(
        items,
        product_files,
        dataset='products',
        on='ProductId',
        target='InventoryType',
        how='left',
        # FIXME: This mapping may not be right.
        validate='m:m',
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
    # FIXME: Merge products with lab results.
    # items = merge_lab_results_with_products(manager, items, results_file)
    return items


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
            'CreatedDate': 'strain_created_at',
        },
        drop=['CreatedBy', 'UpdatedBy', 'UpdatedDate'],
        dedupe=True,
    )
    missing = (items['strain_name'] == False) | (items['strain_name'] == 'False')
    items.loc[missing, 'strain_name'] = items.loc[missing, 'StrainType']
    items.loc[missing, 'StrainType'] = None
    return items


def curate_ccrs_inventory(manager: CCRS, data_dir: str, stats_dir: str):
    """Curate CCRS inventory by merging additional datasets."""
    manager.create_log('Curating inventory...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(data_dir)

    # Create stats directory if it doesn't already exist.
    inventory_dir = os.path.join(stats_dir, 'inventory')
    if not os.path.exists(inventory_dir): os.makedirs(inventory_dir)

    # Read licensees data.
    licensees = read_licensees(data_dir)

    # Define all fields.
    # Note: `IsDeleted` throws a `ValueError` if defined as a bool.
    fields = CCRS_DATASETS['inventory']['fields']
    date_fields = CCRS_DATASETS['inventory']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    item_types['IsDeleted'] = 'string'

    # Get all datafiles.
    inventory_files = get_datafiles(data_dir, 'Inventory_')
    product_files = get_datafiles(data_dir, 'Product_')
    strain_files = get_datafiles(data_dir, 'Strains_')
    area_files = get_datafiles(data_dir, 'Areas_')

    # Curate inventory datafiles.
    manager.create_log(str(len(inventory_files)) + ' datafiles to curate.')
    manager.create_log('Estimated runtime: ' + str(len(inventory_files) * 0.25 + 1.5) + ' hours')
    for i, datafile in enumerate(inventory_files):

        # Read in the items.
        manager.create_log('Augmenting: ' + datafile)
        items = read_items(datafile, item_cols, item_types, date_fields)

        # Merge licensee data.
        manager.create_log('Merging licensee data...')
        items = merge_licensees(items, licensees)

        # Merge product data.
        manager.create_log('Merging product data...')
        items = merge_products(items, product_files)

        # Merge strain data.
        manager.create_log('Merging strain data...')
        items = merge_strains(items, strain_files)

        # Merge area data.
        manager.create_log('Merging area data...')
        items = merge_areas(items, area_files)

        # Standardize column names.
        manager.create_log('Standardizing...')
        items.rename(
            columns={col: camel_to_snake(col) for col in items.columns},
            inplace=True
        )

        # Anonymize the data.
        manager.create_log('Anonymizing...')
        items = anonymize(items)

        # Save the curated inventory data.
        manager.create_log('Saving curated inventory data...')
        outfile = os.path.join(inventory_dir, f'inventory_{i}.xlsx')
        items.to_excel(outfile, index=False)
        manager.create_log('Curated inventory datafile: ' + str(i + 1) + '/' + str(len(inventory_files)))

        # Perform garbage cleaning.
        gc.collect()

    # Merge and save inventory data with curated lab result data.
    try:
        manager.create_log('Merging lab results...')
        inventory_dir = os.path.join(stats_dir, 'inventory')
        inventory_files = sorted_nicely(os.listdir(inventory_dir))
        lab_results_dir = os.path.join(stats_dir, 'lab_results')
        results_file = os.path.join(lab_results_dir, 'lab_results_0.xlsx')
        matched = merge_lab_results(manager, results_file, inventory_dir)
        matched.rename(columns=lambda x: camel_to_snake(x), inplace=True)
        save_dataset(matched, lab_results_dir, 'inventory_lab_results')
        manager.create_log('Merged inventory items with curated lab results.')
    except:
        manager.create_log('Failed to merge lab results. Curate lab results first.')

    # FIXME: Attach lab results to products.
    matched = pd.DataFrame()
    lab_results_dir = os.path.join(stats_dir, 'lab_results')
    inventory_results_file = results_file = os.path.join(lab_results_dir, 'inventory_lab_results_0.xlsx')
    lab_results = pd.read_excel(inventory_results_file)
    augmented_inventory_files = sorted_nicely(os.listdir(inventory_dir))
    augmented_inventory_files = [os.path.join(inventory_dir, f) for f in augmented_inventory_files if not f.startswith('~$')]
    for i, product_file in enumerate(product_files):

        # Read products.
        products = read_products(product_file)

        # TODO: Match products with inventory.
        products.rename(columns={'product_id': 'ProductId'}, inplace=True)
        # for inventory_file in augmented_inventory_files:
        #     inventory = pd.read_excel(
        #         inventory_file
        #     )

        # FIXME: This is not working.
        products = merge_datasets(
            products,
            augmented_inventory_files,
            dataset='inventory',
            on='ProductId',
            target='inventory_id',
            how='left',
            validate='m:1',
            rename={
                'CreatedBy': 'inventory_created_by',
                'UpdatedBy': 'inventory_updated_by',
                'CreatedDate': 'inventory_created_at',
                'updatedDate': 'inventory_updated_at',
                'UpdatedDate': 'inventory_updated_at',
                'Name': 'inventory_name',
            },
        )

        # Merge the lab results with the products.
        match = rmerge(
            products,
            lab_results,
            on='product_id',
            how='left',
            validate='m:1',
        )
        match = match.loc[~match['lab_result_id'].isna()]
        matched = pd.concat([matched, match], ignore_index=True)
        manager.create_log('Matched ' + str(len(matched)) + ' lab results with products...')

    # Save the matched product lab results.
    save_dataset(matched, lab_results_dir, 'product_lab_results')

    # Complete curation.
    end = datetime.now()
    manager.create_log('✓ Finished curating inventory in ' + str(end - start))


# === Test ===
# [ ] Tested:
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D://data/washington/'
    data_dir = f'{base}/June 2023 CCRS Monthly Reports/June 2023 CCRS Monthly Reports/'
    stats_dir = f'{base}/ccrs-stats/'
    manager = CCRS()
    curate_ccrs_inventory(manager, data_dir, stats_dir)
