"""
Get Results Rhode Island
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/25/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Nevada lab result data obtained through public records requests.

"""
# Standard imports:
import os

# External imports:
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
data_dir = r'D:\data\public-records\Rhode Island\Rhode Island'
ri_results = []
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if 'no data' in file.lower():
            continue
        print('Reading:', file)
        datafile = os.path.join(root, file)
        if file.endswith('.csv'):
            df = pd.read_csv(datafile, usecols=columns.keys(), encoding='latin1')  # Use 'latin1' encoding
        elif file.endswith('.xlsx'):
            df = pd.read_excel(datafile, usecols=columns.keys())  # Read .xlsx files correctly
        df.rename(columns=columns, inplace=True)
        ri_results.append(df)
ri_results = pd.concat(ri_results, ignore_index=True)
print('Number of Rhode Island tests:', len(ri_results))

# Extract test_name, units, and product_type from test_type.
ri_results[['test_name', 'units', 'product_type']] = ri_results['test_type'].str.extract(r'(.+?) \((.+?)\) (.+)')

# Restrict to passed tests.
ri_results = ri_results[ri_results['status'] == True]

# Pivot the data to get results for each sample.
pivoted_results = ri_results.pivot_table(
    index=['sample_id', 'producer_license_number', 'lab', 'label', 'date_tested', 'product_type'],
    columns='test_name',
    values='test_result',
    aggfunc='first'
).reset_index()
pivoted_results['date_tested'] = pd.to_datetime(pivoted_results['date_tested'], errors='coerce')
pivoted_results['month'] = pivoted_results['date_tested'].dt.to_period('M')
print('Number of Rhode Island samples:', len(pivoted_results))

# Restrict to flower.
flower_types = [
    'Raw Plant Material',
    'Retest (Raw Plant Material)'
]
ri_flower = pivoted_results[pivoted_results['product_type'].isin(flower_types)]
print('Number of Rhode Island flower samples:', len(ri_flower))

# Calculate the total cannabinoids.
ri_cannabinoids = [
    'CBD',
    'CBDA',
    'Delta-9 THC',
    'THCA',
]
ri_terpenes = [
    'Alpha-Bisabolol',
    'Alpha-Humulene',
    'Alpha-Pinene',
    'Alpha-Terpinene',
    'Beta-Caryophyllene',
    'Beta-Myrcene',
    'Beta-Pinene',
    'Caryophyllene Oxide',
    'Limonene',
    'Linalool',
    'Nerolidol',
]
ri_flower['total_thc'] = ri_flower['Total THC']
ri_flower['total_cbd'] = ri_flower['Total CBD']
ri_flower['total_cannabinoids'] = ri_flower['total_thc'] + ri_flower['total_cbd']
ri_flower['total_terpenes'] = ri_flower[ri_terpenes].sum(axis=1)

# Calculate the total THC to total CBD ratio.
ri_flower['thc_cbd_ratio'] = ri_flower['total_thc'] / ri_flower['total_cbd']

# Calculate the total cannabinoids to total terpenes ratio.
ri_flower['cannabinoids_terpenes_ratio'] = ri_flower['total_cannabinoids'] / ri_flower['total_terpenes']

# Visualize market share by lab by month as a timeseries.
market_share = ri_flower.groupby(['month', 'lab']).size().unstack().fillna(0)
market_share = market_share.div(market_share.sum(axis=1), axis=0)
market_share.plot.area(
    title='Market Share by Lab by Month in Rhode Island',
    figsize=(13, 8),
)
plt.xlabel('')
plt.savefig(f'{assets_dir}/ri-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize tests per capita by month.
ri_population = {
    2023: 1_095_962,
    2022: 1_093_842,
    2021: 1_097_092,
    2020: 1_096_444,
    2019: 1_058_158,
}
ri_flower['year'] = ri_flower['date_tested'].dt.year
ri_flower['population'] = ri_flower['year'].map(ri_population)
tests_per_capita = ri_flower.groupby('month').size() / (ri_flower.groupby('month')['population'].first() / 100_000)
fig, ax = plt.subplots(figsize=(13, 8))
tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Rhode Island')
ax.set_ylabel('Tests per 100,000 People')
plt.show()

# Visualize average total THC by month over time.
ri_flower['date_tested'] = pd.to_datetime(ri_flower['date_tested'])
ri_flower['total_thc'] = ri_flower['total_thc'].astype(float)
ri_flower['month'] = ri_flower['date_tested'].dt.to_period('M')
average_total_thc = ri_flower.groupby('month')['total_thc'].mean()
fig, ax = plt.subplots(figsize=(13, 8))
average_total_thc.index = average_total_thc.index.to_timestamp()
ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
ax.scatter(ri_flower['date_tested'], ri_flower['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total THC (%)')
ax.set_title('Average Total THC by Month in Rhode Island')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(5, 37.5)
plt.savefig(f'{assets_dir}/ri-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize average total CBD by month over time.
ri_flower['total_cbd'] = ri_flower['total_cbd'].astype(float)
sample = ri_flower.loc[ri_flower['total_cbd'] < 1]
average_total_cbd = sample.groupby('month')['total_cbd'].mean()
fig, ax = plt.subplots(figsize=(13, 8))
average_total_cbd.index = average_total_cbd.index.to_timestamp()
ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
ax.scatter(sample['date_tested'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total CBD (%)')
ax.set_title('Average Total CBD by Month in Rhode Island in Low CBD Samples (<1%)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(0, 0.33)
plt.savefig(f'{assets_dir}/ri-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
