"""
Get MD Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2023
Updated: 6/20/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Collect all public Maryland lab result data.

Data Sources:
    
    - Public records request from the Maryland Medical Cannabis Commission (MMCC).

"""
# Standard imports:
import os

# External imports:
from cannlytics.utils import snake_case, camel_to_snake
from cannlytics.utils.constants import ANALYTES
import pandas as pd



def combine_redundant_columns(df, product_types=None, verbose=False):
    """Combine redundant columns and extract units and product types."""
    combined_results = {}
    for col in df.columns:
        matched = False
        if product_types is not None:
            for product_type in product_types:
                if product_type in col and '(' not in col:
                    base_name = col.split(product_type)[0].strip()
                    if base_name not in combined_results:
                        combined_results[base_name] = df[col]
                        if verbose:
                            print('New column:', base_name)
                    else:
                        combined_results[base_name] = combined_results[base_name].fillna(df[col])
                        if verbose:
                            print('Combined column:', base_name)
                    matched = True
        if matched:
            continue
        if '(' in col and ')' in col:
            base_name = col.split('(')[0].strip()
            if base_name not in combined_results:
                combined_results[base_name] = df[col]
                if verbose:
                    print('New column:', base_name)
            else:
                combined_results[base_name] = combined_results[base_name].fillna(df[col])
                if verbose:
                    print('Combined column:', base_name)
        elif col not in combined_results:
            if verbose:
                print('New column:', col)
            combined_results[col] = df[col]
    return pd.DataFrame(combined_results)


def standardize_analyte_names(df, analyte_mapping):
    """Standardize analyte names."""
    df.columns = [analyte_mapping.get(snake_case(col), snake_case(col)) for col in df.columns]
    return df


# Constants.
STATE = 'MD'

# Get the data files.
data_dir = r'D:\data\public-records\Maryland\md-prr-2024-01-02\md-prr-2024-01-02'
datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir)]

# Read all of the data.
all_data = []
for datafile in datafiles:

    # Read the segment of data.
    df = pd.read_csv(datafile)

    # Pivot the dataframe.
    results = df.pivot_table(
        index=[
            'TestPerformedDate',
            'PackageId',
            'StrainName',
            'TestingFacilityId',
            'ProductCategoryName',
        ],
        columns='TestTypeName',
        values='TestResultLevel',
        aggfunc='first'
    ).reset_index()
    results = pd.DataFrame(results)

    # Determine the "status" based on the "TestPassed" column.
    status = df.groupby('PackageId')['TestPassed'].apply(lambda x: 'Fail' if False in x.values else 'Pass')
    results = results.merge(status, left_on='PackageId', right_index=True)

    # Combine redundant columns
    product_types = [
        'Infused Edible',
        'Infused Non-Edible',
        'Non-Solvent Concentrate',
        'R&D Testing',
        'Raw Plant Material',
        'Solvent Based Concentrate',
        'Sub-Contract',
        'Whole Wet Plant',
    ]
    results = combine_redundant_columns(results, product_types=product_types)

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    columns = {
        'testpassed': 'status',
        'testperformeddate': 'date_tested',
        'packageid': 'package_id',
        'strainname': 'strain_name',
        'testingfacilityid': 'lab_id',
        'productcategoryname': 'product_type'
    }
    results = results.rename(columns=columns)

    # Drop duplicates.
    results = results.drop_duplicates(subset=['package_id'])

    # Record the data.
    # results.set_index('package_id', inplace=True)
    # all_data.append(results.reset_index(drop=True))
    all_data.extend(results.to_dict(orient='records'))
    print('Read %i MD lab results from %s.' % (len(results), datafile))

# Aggregate all lab results.
# all_results = pd.concat([df.set_index('package_id') for df in all_data], ignore_index=True)
# results = pd.concat(all_data, ignore_index=True)
all_results = pd.DataFrame(all_data)
print('Aggregated %i MD lab results.' % len(all_results))
datafile = 'D://data/maryland/md-lab-results-2024-01-02.csv'
all_results.to_csv(datafile, index=False)
