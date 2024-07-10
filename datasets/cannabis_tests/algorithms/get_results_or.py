"""
Get Results Oregon
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/30/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Oregon lab result data obtained through public records requests.

Data Sources:
    
    - Public records request by Jamie Toth.

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics.data import save_with_copyright
from cannlytics.utils import snake_case
from cannlytics.utils.constants import ANALYTES
from dotenv import dotenv_values
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Define standard columns.
columns = {
    'LabId': 'lab_id',
    'SampleCreatedByLicenseId': 'producer_id',
    'SampleId': 'sample_id',
    'MonthOfTest': 'month',
    'YearOfTest': 'year',
    'ProductType': 'product_type',
    'TestName': 'test_name',
    'Result': 'result',
    'PassFail': 'status',
}

# Define the data types for each column.
dtype_spec = {
    'LabId': str,
    'SampleCreatedByLicenseId': str,
    'SampleId': str,
    'MonthOfTest': str,
    'YearOfTest': str,
    'ProductType': str,
    'TestName': str,
    'Result': float,
    'PassFail': str,
}

def read_and_standardize_csv(file_path, columns, dtype_spec):
    """Read a CSV file and standardize the column names."""
    try:
        df = pd.read_csv(file_path, dtype=dtype_spec, low_memory=False)
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def collect_data(datafile, columns, dtype_spec):
    """Collect data from the specified CSV file."""
    df = read_and_standardize_csv(datafile, columns, dtype_spec)
    df['month'] = df['year'].astype(str) + '-' + df['month'].astype(str)
    df['date_tested'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    return df

def pivot_data(data):
    """Pivot the data to get results for each sample."""
    results = data.pivot_table(
        index=['sample_id', 'producer_id', 'lab_id', 'product_type', 'date_tested'],
        columns='test_name',
        values='result',
        aggfunc='first'
    ).reset_index()
    results['month'] = results['date_tested'].dt.to_period('M')
    results['year'] = results['date_tested'].dt.year
    return results

def augment_calculations(
        df,
        cannabinoids=None,
        terpenes=None,
        delta_9_thc='delta_9_thc',
        thca='thca',
        cbd='cbd',
        cbda='cbda',
    ):
    """Augment the DataFrame with additional calculated fields."""
    # Calculate total cannabinoids.
    if cannabinoids is not None:
        df['total_cannabinoids'] = round(df[cannabinoids].sum(axis=1), 2)

    # Calculate total terpenes.
    if terpenes is not None:
        df['total_terpenes'] = round(df[terpenes].sum(axis=1), 2)

    # Calculate the total THC to total CBD ratio.
    df['total_thc'] = round(df[delta_9_thc] + 0.877 * df[thca], 2)
    df['total_cbd'] = round(df[cbd] + 0.877 * df[cbda], 2)
    df['thc_cbd_ratio'] = round(df['total_thc'] / df['total_cbd'], 2)

    # Calculate the total cannabinoids to total terpenes ratio.
    if cannabinoids is not None and terpenes is not None:
        df['cannabinoids_terpenes_ratio'] = round(df['total_cannabinoids'] / df['total_terpenes'], 2)

    # Return the augmented data.
    return df

def standardize_analyte_names(df, analyte_mapping):
    """Standardize analyte names."""
    results.columns = [col.split('(')[0].strip() for col in results.columns]
    df.columns = [analyte_mapping.get(snake_case(col), snake_case(col)) for col in df.columns]
    return df

def combine_similar_columns(df, similar_columns):
    """Combine similar columns with different spellings or capitalization."""
    for target_col, col_variants in similar_columns.items():
        if target_col not in df.columns:
            df[target_col] = pd.NA
        for col in col_variants:
            if col in df.columns:
                df[target_col] = df[target_col].combine_first(df[col])
                df.drop(columns=[col], inplace=True)
    return df

def convert_mg_g_to_percentage(df):
    """Convert mg/g values to percentage for specified columns."""
    mg_g_columns = [col for col in df.columns if '(mg/g)' in col]
    for col in mg_g_columns:
        df[col] = df[col] / 10
        df.rename(columns={col: col.replace('(mg/g)', '').strip()}, inplace=True)
    return df

# === Test ===
# [✓] Tested: 2024-05-30 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # TODO: Read the datafile from HuggingFace.

    # Read Oregon lab results.
    datafile = "D:\data\public-records\Oregon\Oregon\Oregon data 5-7-24 (rich)\Anonymized Test Data Feb 2021 to April 2024.csv"
    data = collect_data(datafile, columns, dtype_spec)
    print('Number of Oregon tests:', len(data))

    # Pivot the data to get results for each sample.
    results = pivot_data(data)
    print('Number of Oregon test samples:', len(results))

    # Divide any value in a column with mg/g by 10 to get a percentage.
    results = convert_mg_g_to_percentage(results)
    print('Converted mg/g values to percentages.')

    # Combine similar columns.
    similar_columns = {
        'cbd': ['CBD (%RSD)', 'CBD (RPD)', 'Total CBD (mg/g; cannot fail)'],
        'delta_8_thc': ['Delta 8 THC', 'Delta-8 THC', 'Delta-8 THC (%RSD)', 'Delta-8 THC (RPD)', 'Delta-8 THC (mg/g)'],
        'delta_9_thc': ['Delta 9 THC', 'Delta-9 THC', 'THC (%RSD)', 'THC (RPD)', 'Delta-9 THC (mg/g)'],
        'moisture_content': ['Moisture Content (%)', 'R&D Test: Moisture Content', 'Subcontracted Test - Moisture Content'],
        'mycotoxins': ['Mycotoxins (pass/fail)', 'R&D Test: Mycotoxins', 'Subcontracted Test - Mycotoxins'],
    }
    results = combine_similar_columns(results, similar_columns)
    print('Combined similar columns.')

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    print('Standardized analyte names.')

    # Drop nuisance columns.
    drop = [
        'heavy_metals',
        'pesticides',
        'potency',
        'randd_test',
        'randd_test_heavy_metals',
        'randd_test_microbiological_contaminants',
        'randd_test_moisture_content',
        'randd_test_mycotoxins',
        'randd_test_pesticides',
        'randd_test_potency',
        'randd_test_solvents',
        'randd_test_water_activity',
        'solvents',
        'tentatively_identified_compounds',
        'microbiological_contaminants',
    ]
    results = results.drop(columns=drop, errors='ignore')

    # Ensure all numeric columns are numeric.
    non_numeric = [
        'sample_id',
        'producer_id',
        'lab_id',
        'product_type',
        'date_tested',
        'month',
        'year',
    ]
    numeric_cols = results.columns.difference(non_numeric)
    for col in numeric_cols:
        results[col] = pd.to_numeric(results[col], errors='coerce')
    print('Converted columns to numeric.')

    # Augment additional calculated metrics.
    cannabinoids = ['delta_8_thc', 'delta_9_thc', 'thca', 'cbd']
    results['total_cbd'] = results['cbd']
    results['total_cannabinoids'] = round(results[cannabinoids].sum(), 2)
    results['thc_cbd_ratio'] = round(results['total_thc'] / results['total_cbd'], 2)
    print('Augmented fields.')

    # Sort the columns.
    numeric_cols = results.columns.difference(non_numeric)
    numeric_cols_sorted = sorted(numeric_cols)
    results = results[non_numeric + numeric_cols_sorted]

    # Save the results with copyright and sources sheets.
    stats_dir = 'D://data/oregon/results/datasets'
    date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(stats_dir): os.makedirs(stats_dir)
    outfile = f'{stats_dir}/or-results-{date}.xlsx'
    save_with_copyright(
        results,
        outfile,
        dataset_name='Oregon Cannabis Lab Results',
        author='Jamie Toth (data acquisition), Keegan Skeate (curation)',
        publisher='Cannlytics',
        sources=['Oregon Liquor and Cannabis Commission', 'Jamie Toth'],
        source_urls=['https://www.oregon.gov/olcc/marijuana/pages/default.aspx', 'https://jamietoth.com'],
    )
    print('Saved Oregon lab results:', outfile)
