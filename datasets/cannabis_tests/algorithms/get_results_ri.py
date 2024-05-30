"""
Get Results Rhode Island
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
import numpy as np
import pandas as pd


# Define columns.
columns = {
    'Id': 'sample_id',
    'TestingFacilityName': 'lab',
    'ItemFromFacilityLicenseNumber': 'producer_license_number',
    'SourcePackageLabels': 'label',
    'TestPerformedDate': 'date_tested',
    'TestTypeName': 'test_type',
    'TestResultLevel': 'test_result',
    'OverallPassed': 'status',
}

# Define the data types for each column.
dtype_spec = {
    'Id': str,
    'TestingFacilityName': str,
    'ItemFromFacilityLicenseNumber': str,
    'SourcePackageLabels': str,
    'TestPerformedDate': str,
    'TestTypeName': str,
    'TestResultLevel': float,
    'OverallPassed': bool,
}

def collect_data(data_dir, columns, dtype_spec):
    """Collect data from a directory of CSV and Excel files."""
    results = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if 'no data' in file.lower():
                continue
            print('Reading:', file)
            file_path = os.path.join(root, file)
            if file.endswith('.csv'):
                df = read_and_standardize_csv(file_path, columns, dtype_spec)
            elif file.endswith('.xlsx'):
                df = read_and_standardize_excel(file_path, columns)
            if not df.empty:
                results.append(df)
    return pd.concat(results, ignore_index=True)

def read_and_standardize_csv(file_path, columns, dtype_spec):
    """Read a CSV file and standardize the column names."""
    try:
        df = pd.read_csv(file_path, dtype=dtype_spec, usecols=columns.keys(), encoding='latin1')
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def read_and_standardize_excel(file_path, columns):
    """Read an Excel file and standardize the column names."""
    try:
        df = pd.read_excel(file_path, usecols=columns.keys())
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()


def extract_test_details(data):
    """Extract test_name, units, and product_type from test_type."""
    data[['test_name', 'units', 'product_type']] = data['test_type'].str.extract(r'(.+?) \((.+?)\) (.+)')
    return data

def pivot_data(data):
    """Pivot the data to get results for each sample."""
    results = data.pivot_table(
        index=['sample_id', 'producer_license_number', 'lab', 'label', 'date_tested', 'product_type'],
        columns='test_name',
        values='test_result',
        aggfunc='first'
    ).reset_index()
    results['date_tested'] = pd.to_datetime(results['date_tested'], errors='coerce')
    results['month'] = results['date_tested'].dt.to_period('M')
    return results

def augment_calculations(df):
    """Augment the DataFrame with additional calculated fields."""
    # Define cannabinoids and terpenes.
    cannabinoids = ['CBD', 'CBDA', 'Delta-9 THC', 'THCA']
    terpenes = [
        'Alpha-Bisabolol', 'Alpha-Humulene', 'Alpha-Pinene', 'Alpha-Terpinene',
        'Beta-Caryophyllene', 'Beta-Myrcene', 'Beta-Pinene', 'Caryophyllene Oxide',
        'Limonene', 'Linalool', 'Nerolidol'
    ]

    # Calculate total cannabinoids.
    df['total_thc'] = df['Delta-9 THC'] + (df['THCA'] * 0.877)
    df['total_cbd'] = df['CBD'] + (df['CBDA'] * 0.877)
    df['total_cannabinoids'] = df[cannabinoids].sum(axis=1)

    # Calculate total terpenes.
    df['total_terpenes'] = df[terpenes].sum(axis=1)

    # Calculate the THC to CBD ratio.
    df['thc_cbd_ratio'] = df['total_thc'] / df['total_cbd']

    # Calculate the total cannabinoids to total terpenes ratio.
    df['cannabinoids_terpenes_ratio'] = df['total_cannabinoids'] / df['total_terpenes']

    return df

def standardize_analyte_names(df, analyte_mapping):
    """Standardize analyte names."""
    df.columns = [analyte_mapping.get(snake_case(col), snake_case(col)) for col in df.columns]
    return df

# === Test ===
# [✓] Tested: 2024-05-28 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':
    
    # Collect Rhode Island lab results
    data_dir = r'D:\data\public-records\Rhode Island\Rhode Island'
    data = collect_data(data_dir, columns, dtype_spec)
    print('Number of Rhode Island tests:', len(data))

    # Extract test details
    data = extract_test_details(data)

    # Restrict to passed tests.
    data = data[data['status'] == True]

    # Pivot the data to get results for each sample.
    results = pivot_data(data)
    print('Number of Rhode Island samples:', len(results))

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    print('Standardized analyte names.')

    # Augment additional calculated metrics.
    results = augment_calculations(results)
    print('Augmented fields.')


# === OLD ===

# data_dir = r'D:\data\public-records\Rhode Island\Rhode Island'
# data = []
# for root, dirs, files in os.walk(data_dir):
#     for file in files:
#         if 'no data' in file.lower():
#             continue
#         print('Reading:', file)
#         datafile = os.path.join(root, file)
#         if file.endswith('.csv'):
#             df = pd.read_csv(datafile, usecols=columns.keys(), encoding='latin1')  # Use 'latin1' encoding
#         elif file.endswith('.xlsx'):
#             df = pd.read_excel(datafile, usecols=columns.keys())  # Read .xlsx files correctly
#         df.rename(columns=columns, inplace=True)
#         data.append(df)
# data = pd.concat(data, ignore_index=True)
# print('Number of Rhode Island tests:', len(data))

# # Extract test_name, units, and product_type from test_type.
# data[['test_name', 'units', 'product_type']] = data['test_type'].str.extract(r'(.+?) \((.+?)\) (.+)')

# # Restrict to passed tests.
# data = data[data['status'] == True]

# # Pivot the data to get results for each sample.
# results = data.pivot_table(
#     index=['sample_id', 'producer_license_number', 'lab', 'label', 'date_tested', 'product_type'],
#     columns='test_name',
#     values='test_result',
#     aggfunc='first'
# ).reset_index()
# results['date_tested'] = pd.to_datetime(results['date_tested'], errors='coerce')
# results['month'] = results['date_tested'].dt.to_period('M')
# print('Number of Rhode Island samples:', len(results))

# # Calculate the total cannabinoids.
# ri_cannabinoids = [
#     'CBD',
#     'CBDA',
#     'Delta-9 THC',
#     'THCA',
# ]
# ri_terpenes = [
#     'Alpha-Bisabolol',
#     'Alpha-Humulene',
#     'Alpha-Pinene',
#     'Alpha-Terpinene',
#     'Beta-Caryophyllene',
#     'Beta-Myrcene',
#     'Beta-Pinene',
#     'Caryophyllene Oxide',
#     'Limonene',
#     'Linalool',
#     'Nerolidol',
# ]
# results['total_thc'] = results['Total THC']
# results['total_cbd'] = results['Total CBD']
# results['total_cannabinoids'] = results['total_thc'] + results['total_cbd']
# results['total_terpenes'] = results[ri_terpenes].sum(axis=1)

# # Calculate the total THC to total CBD ratio.
# results['thc_cbd_ratio'] = results['total_thc'] / results['total_cbd']

# # Calculate the total cannabinoids to total terpenes ratio.
# results['cannabinoids_terpenes_ratio'] = results['total_cannabinoids'] / results['total_terpenes']


# === Analyze Rhode Island lab results ===

# # Visualize market share by lab by month as a timeseries.
# market_share = results.groupby(['month', 'lab']).size().unstack().fillna(0)
# market_share = market_share.div(market_share.sum(axis=1), axis=0)
# market_share.plot.area(
#     title='Market Share by Lab by Month in Rhode Island',
#     figsize=(13, 8),
# )
# plt.xlabel('')
# plt.savefig(f'{assets_dir}/ri-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize tests per capita by month.
# ri_population = {
#     2023: 1_095_962,
#     2022: 1_093_842,
#     2021: 1_097_092,
#     2020: 1_096_444,
#     2019: 1_058_158,
# }
# results['year'] = results['date_tested'].dt.year
# results['population'] = results['year'].map(ri_population)
# tests_per_capita = results.groupby('month').size() / (results.groupby('month')['population'].first() / 100_000)
# fig, ax = plt.subplots(figsize=(13, 8))
# tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Rhode Island')
# ax.set_ylabel('Tests per 100,000 People')
# plt.show()

# # Visualize average total THC by month over time.
# results['date_tested'] = pd.to_datetime(results['date_tested'])
# results['total_thc'] = results['total_thc'].astype(float)
# results['month'] = results['date_tested'].dt.to_period('M')
# average_total_thc = results.groupby('month')['total_thc'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_thc.index = average_total_thc.index.to_timestamp()
# ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
# ax.scatter(results['date_tested'], results['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total THC (%)')
# ax.set_title('Average Total THC by Month in Rhode Island')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(5, 37.5)
# plt.savefig(f'{assets_dir}/ri-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize average total CBD by month over time.
# results['total_cbd'] = results['total_cbd'].astype(float)
# sample = results.loc[results['total_cbd'] < 1]
# average_total_cbd = sample.groupby('month')['total_cbd'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_cbd.index = average_total_cbd.index.to_timestamp()
# ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
# ax.scatter(sample['date_tested'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total CBD (%)')
# ax.set_title('Average Total CBD by Month in Rhode Island in Low CBD Samples (<1%)')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 0.33)
# plt.savefig(f'{assets_dir}/ri-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()
