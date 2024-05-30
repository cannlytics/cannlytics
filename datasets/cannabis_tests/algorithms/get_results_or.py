"""
Get Results Oregon
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/29/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Nevada lab result data obtained through public records requests.

"""
# Standard imports:
import os

# External imports:
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
    df['date'] = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    return df

def pivot_data(data):
    """Pivot the data to get results for each sample."""
    results = data.pivot_table(
        index=['sample_id', 'producer_id', 'lab_id', 'product_type', 'date'],
        columns='test_name',
        values='result',
        aggfunc='first'
    ).reset_index()
    results['month'] = results['date'].dt.to_period('M')
    return results

def augment_calculations(df):
    """Augment the DataFrame with additional calculated fields."""
    # Calculate total cannabinoids.
    df['total_thc'] = df['Total THC (mg/g)'] * 0.1
    df['total_cbd'] = df['Total CBD (mg/g; cannot fail)'] * 0.1
    df['total_cannabinoids'] = df['total_thc'] + df['total_cbd']

    # Calculate the THC to CBD ratio.
    df['thc_cbd_ratio'] = df['total_thc'] / df['total_cbd']

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
# [✓] Tested: 2024-05-28 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

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
        'delta_8_thc': ['Delta-8 THC (%RSD)', 'Delta-8 THC (RPD)', 'Delta-8 THC (mg/g)'],
        'delta_9_thc': ['THC (%RSD)', 'THC (RPD)', 'Delta-9 THC (mg/g)'],
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
        'date',
        'month',
    ]
    numeric_cols = results.columns.difference(non_numeric)
    for col in numeric_cols:
        results[col] = pd.to_numeric(results[col], errors='coerce')
    print('Converted columns to numeric.')


    # TODO: Save the results.
    # Note: Add copyright and sources sheets.

    
    # DEV:
    analyte = 'delta_8_thc'
    upper_limit = 10000
    lower_limit = 0
    sample = results.loc[(results[analyte] > lower_limit) & (results[analyte] < upper_limit)]
    sample[analyte].hist(bins=100)
    plt.xlim(lower_limit, upper_limit)
    plt.show()

    # TODO: Read the datafile from HuggingFace.




# === Analyze Oregon lab results ===

# # Visualize market share by lab by month as a timeseries.
# market_share = results.groupby(['month', 'lab_id']).size().unstack().fillna(0)
# market_share = market_share.div(market_share.sum(axis=1), axis=0)
# market_share.plot.area(
#     title='Market Share by Lab by Month in Oregon',
#     figsize=(13, 8),
#     legend=None,
# )
# plt.xlabel('')
# plt.savefig(f'{assets_dir}/or-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize tests per capita by month.
# or_population = {
#     2023: 4_233_358,
#     2022: 4_239_379,
#     2021: 4_256_465,
#     2020: 4_245_044,
#     2019: 4_216_116,
# }
# results['year'] = results['date'].dt.year
# results['population'] = results['year'].map(or_population)
# fig, ax = plt.subplots(figsize=(13, 8))
# or_tests_per_capita = results.groupby('month').size() / (results.groupby('month')['population'].first() / 100_000)
# or_tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Oregon')
# ax.set_ylabel('Tests per 100,000 People')
# plt.show()

# # Visualize average total THC by month over time.
# results['total_thc'] = results['total_thc'].astype(float)
# average_total_thc = results.groupby('month')['total_thc'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_thc.index = average_total_thc.index.to_timestamp()
# ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
# ax.scatter(results['date'], results['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total THC (%)')
# ax.set_title('Average Total THC by Month in Oregon')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 45)
# plt.savefig(f'{assets_dir}/or-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize average total CBD by month over time.
# results['total_cbd'] = results['total_cbd'].astype(float)
# sample = results.loc[results['total_cbd'] < 1]
# average_total_cbd = sample.groupby('month')['total_cbd'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_cbd.index = average_total_cbd.index.to_timestamp()
# ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
# ax.scatter(sample['date'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total CBD (%)')
# ax.set_title('Average Total CBD by Month in Oregon in Low CBD Samples (<1%)')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 0.75)
# plt.savefig(f'{assets_dir}/or-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()
