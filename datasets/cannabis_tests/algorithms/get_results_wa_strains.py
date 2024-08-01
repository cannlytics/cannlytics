

# Standard imports:
import json
import os
import subprocess
from typing import List
import warnings

# External imports:
import pandas as pd
from cannlytics.compounds import pesticides
from cannlytics.data.coas.coas import standardize_results
from cannlytics.utils.utils import snake_case, kebab_case, camel_to_snake
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from cannlytics.data.ccrs import CCRS_DATASETS, get_datafiles
from cannlytics.data.cache import Bogart


def read_ccrs_data(
        datafile,
        dtype: dict,
        usecols: List[str],
        parse_dates: List[str],
        on_bad_lines: str = 'skip',
        sep: str = '\t',
        encoding: str = 'utf-16',
        engine: str = 'python',
        rename = None,
    ) -> pd.DataFrame:
    """Load supplement data from a specified data file."""
    df = pd.read_csv(
        datafile,
        sep=sep,
        encoding=encoding,
        engine=engine,
        parse_dates=parse_dates,
        dtype=dtype,
        usecols=usecols,
        on_bad_lines=on_bad_lines
    )
    if rename:
        df = df.rename(columns=rename)
    return df


def convert_timestamps(obj):
    """
    Recursively convert Timestamp and NaTType objects in a dictionary to strings.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, pd.Timestamp):
                obj[key] = value.isoformat()
            elif isinstance(value, pd._libs.tslibs.nattype.NaTType):
                obj[key] = None
            elif isinstance(value, dict):
                convert_timestamps(value)
            elif isinstance(value, list):
                obj[key] = [convert_timestamps(item) if isinstance(item, (pd.Timestamp, pd._libs.tslibs.nattype.NaTType)) else item for item in value]
    return obj


# Read lab results.
data_dir = 'D://data/washington/stats/lab_results'
datafile = os.path.join(data_dir, 'wa-lab-results-aggregate.xlsx')
results = pd.read_excel(datafile)

# Initialize the cache.
inventory_cache = Bogart('D://data/.cache/results-wa-inventory.jsonl')
products_cache = Bogart('D://data/.cache/results-wa-products.jsonl')
strains_cache = Bogart('D://data/.cache/results-wa-strains.jsonl')

# Isolate the subsample or results.
results['inventory_id'] = results['inventory_id'].astype(str)
inventory_ids = list(results['inventory_id'].unique())
print('Number of inventory items:', len(inventory_ids))
matches = {}

# Iterate over all releases to augment inventory, product, and strain data.
base = 'D://data/washington/'
releases = [
    # 'CCRS PRR (8-4-23)', # Contains all prior releases.
    'CCRS PRR (9-5-23)',
    'CCRS PRR (10-2-23)',
    'CCRS PRR (11-2-23)',
    'CCRS PRR (12-2-23)',
    'CCRS PRR (1-2-24)',
    'CCRS PRR (2-2-24)',
    'CCRS PRR (3-27-24)',
    'CCRS PRR (4-2-24)',
    'CCRS PRR (5-2-24)',
    'CCRS PRR (6-2-24)',
    'CCRS PRR (7-2-24)',
]
for release in releases:
    data_dir = os.path.join(base, release, release)
    print('Augmenting data:', data_dir)

    # Find matching inventory items.
    inventory_files = get_datafiles(data_dir, 'Inventory_')
    inventory_fields = CCRS_DATASETS['inventory']['fields']
    inventory_date_fields = CCRS_DATASETS['inventory']['date_fields']
    item_cols = list(inventory_fields.keys()) + inventory_date_fields
    item_types = {k: inventory_fields[k] for k in inventory_fields if k not in inventory_date_fields}
    item_types['IsDeleted'] = 'string'
    inventory_renames = {
        'CreatedBy': 'inventory_created_by',
        'UpdatedBy': 'inventory_updated_by',
        'CreatedDate': 'inventory_created_at',
        'updatedDate': 'inventory_updated_at',
        'UpdatedDate': 'inventory_updated_at',
        'Name': 'inventory_name',
    }
    for i, datafile in enumerate(inventory_files):
        if len(matches) == len(results):
            print('Matched all inventory items')
            break
        print('Augmenting inventory:', datafile)
        items = read_ccrs_data(
            datafile,
            usecols=item_cols,
            dtype=item_types,
            parse_dates=inventory_date_fields,
            rename=inventory_renames,
        )
        for inventory_id in inventory_ids:
            if inventory_cache.get(inventory_id):
                matches[inventory_id] = inventory_cache.get(inventory_id)
                continue
            # if inventory_id in matches:
            #     continue
            item = items.loc[items['InventoryId'] == inventory_id]
            if len(item) > 0:
                item = item.iloc[0]
                item_dict = item.to_dict()
                item_dict = convert_timestamps(item_dict)
                matches[inventory_id] = item_dict
                print('Matched inventory:', inventory_id)
                inventory_cache.set(inventory_id, item_dict)
    print('Matched inventory items:', len(matches))

    # Match product data.
    product_matches = {}
    product_files = get_datafiles(data_dir, 'Product_')
    product_fields = CCRS_DATASETS['products']['fields']
    product_date_fields = CCRS_DATASETS['products']['date_fields']
    product_cols = list(product_fields.keys()) + product_date_fields
    product_types = {k: product_fields[k] for k in product_fields if k not in product_date_fields}
    product_types['IsDeleted'] = 'string'
    product_types['UnitWeightGrams'] = 'string'
    product_types['CreatedDate'] = 'string'
    product_types['UpdatedDate'] = 'string'
    product_renames = {
        'CreatedDate': 'product_created_at',
        'updatedDate': 'product_updated_at',
        'UpdatedDate': 'product_updated_at',
        'ExternalIdentifier': 'product_external_id',
        'LicenseeId': 'producer_licensee_id',
        'Name': 'product_name',
        'Description': 'product_description',
    }
    for i, datafile in enumerate(product_files):
        if len(product_matches) == len(results):
            print('Matched all products')
            break
        print('Augmenting products:', datafile)
        products = read_ccrs_data(
            datafile,
            usecols=product_cols,
            dtype=product_types,
            parse_dates=product_date_fields,
            rename=product_renames,
        )
        for inventory_id, values in matches.items():
            if products_cache.get(inventory_id):
                obs = matches[inventory_id]
                product = products_cache.get(inventory_id)
                matches[inventory_id] = {**obs, **product}
                product_matches[inventory_id] = product
                continue
            # if inventory_id in product_matches:
            #     continue
            product = products.loc[products['ProductId'] == values['ProductId']]
            if len(product) > 0:
                product = product.iloc[0]
                obs = matches[inventory_id]
                product_dict = product.to_dict()
                product_dict = convert_timestamps(product_dict)
                matches[inventory_id] = {**obs, **product_dict}
                print('Matched product:', inventory_id)
                product_matches[inventory_id] = product_dict
                products_cache.set(inventory_id, product_dict)

    # Match strain data.
    strain_matches = {}
    strain_files = get_datafiles(data_dir, 'Strains_')
    strain_fields = CCRS_DATASETS['strains']['fields']
    strain_date_fields = CCRS_DATASETS['strains']['date_fields']
    strain_cols = list(strain_fields.keys()) + strain_date_fields
    strain_types = {k: strain_fields[k] for k in strain_fields if k not in strain_date_fields}
    strain_types['IsDeleted'] = 'string'
    strain_renames = {
        'Name': 'strain_name',
        'CreatedDate': 'strain_created_at',
    }
    for i, datafile in enumerate(strain_files):
        if len(strain_matches) == len(results):
            print('Matched all strains')
            break
        print('Augmenting strains:', datafile)
        strains = read_ccrs_data(
            datafile,
            usecols=strain_cols,
            dtype=strain_types,
            parse_dates=strain_date_fields,
            rename=strain_renames,
        )
        # TODO: Fix misaligned strain data.
        # missing = (strains['strain_name'] == False) | (strains['strain_name'] == 'False')
        # strains.loc[missing, 'strain_name'] = strains.loc[strains, 'StrainType']
        for inventory_id, values in matches.items():
            # if inventory_id in strain_matches:
            #     continue
            if strains_cache.get(inventory_id):
                strain_matches[inventory_id] = strains_cache.get(inventory_id)
                continue
            strain = strains.loc[strains['StrainId'] == values['StrainId']]
            if len(strain) > 0:
                strain = strain.iloc[0]
                obs = matches[inventory_id]
                strain_dict = strain.to_dict()
                strain_dict = convert_timestamps(strain_dict)
                matches[inventory_id] = {**obs, **strain_dict}
                print('Matched strain:', inventory_id)
                strain_matches[inventory_id] = strain_dict
                strains_cache.set(inventory_id, strain_dict)

    # Optional: Merge area data?
    # area_files = get_datafiles(data_dir, 'Areas_')

    # Break if all of the subsample is matched.
    if len(matches) == len(results):
        print('Matched all results')
        break

# FIXME: Merge inventory, product, and strain data with the results using the cache.

# Merge the inventory data with the subsample.
matches_df = pd.DataFrame.from_dict(matches, orient='index')
matches_df.index.name = 'inventory_id'
matches_df.reset_index(inplace=True, drop=True)
matches_df.columns = [camel_to_snake(col) for col in matches_df.columns]
results = results.merge(
    matches_df,
    on='inventory_id',
    how='left',
    suffixes=['', '_dup']
)
results.drop(columns=[x for x in results.columns if '_dup' in x], inplace=True)

# TODO: Further process the results.

