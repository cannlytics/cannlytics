"""
Get Results Oregon
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


# TODO: Read the datafile from HuggingFace.

# Read Oregon lab results.
datafile = "D:\data\public-records\Oregon\Oregon\Oregon data 5-7-24 (rich)\Anonymized Test Data Feb 2021 to April 2024.csv"
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
oregon_results = pd.read_csv(datafile, usecols=columns.keys())
oregon_results.rename(columns=columns, inplace=True)
oregon_results['month'] = oregon_results['year'].astype(str) + '-' + oregon_results['month'].astype(str)
oregon_results['date'] = pd.to_datetime(oregon_results['month'], format='%Y-%m', errors='coerce')
print('Number of Oregon tests:', len(oregon_results))

# Restrict to passed tests.
oregon_results = oregon_results[oregon_results['status'] == True]

# Pivot the data to get results for each sample.
pivoted_results = oregon_results.pivot_table(
    index=['sample_id', 'producer_id', 'lab_id', 'product_type', 'date'],
    columns='test_name',
    values='result',
    aggfunc='first'
).reset_index()
pivoted_results['month'] = pivoted_results['date'].dt.to_period('M')
print('Number of Oregon test samples:', len(pivoted_results))

# Restrict to flower.
flower_types = ['Buds', 'Buds (by strain)',]
oregon_flower = pivoted_results[pivoted_results['product_type'].isin(flower_types)]
print('Number of Oregon flower samples:', len(oregon_flower))

# Calculate the total cannabinoids.
oregon_flower['total_thc'] = oregon_flower['Total THC (mg/g)'] * 0.1
oregon_flower['total_cbd'] = oregon_flower['Total CBD (mg/g; cannot fail)'] * 0.1
oregon_flower['total_cannabinoids'] = oregon_flower['total_thc'] + oregon_flower['total_cbd']

# Calculate the ratios.
oregon_flower['thc_cbd_ratio'] = oregon_flower['total_thc'] / oregon_flower['total_cbd']

# Visualize market share by lab by month as a timeseries.
market_share = oregon_flower.groupby(['month', 'lab_id']).size().unstack().fillna(0)
market_share = market_share.div(market_share.sum(axis=1), axis=0)
market_share.plot.area(
    title='Market Share by Lab by Month in Oregon',
    figsize=(13, 8),
    legend=None,
)
plt.xlabel('')
plt.savefig(f'{assets_dir}/or-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize tests per capita by month.
or_population = {
    2023: 4_233_358,
    2022: 4_239_379,
    2021: 4_256_465,
    2020: 4_245_044,
    2019: 4_216_116,
}
oregon_flower['year'] = oregon_flower['date'].dt.year
oregon_flower['population'] = oregon_flower['year'].map(or_population)
fig, ax = plt.subplots(figsize=(13, 8))
or_tests_per_capita = oregon_flower.groupby('month').size() / (oregon_flower.groupby('month')['population'].first() / 100_000)
or_tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Oregon')
ax.set_ylabel('Tests per 100,000 People')
plt.show()

# Visualize average total THC by month over time.
oregon_flower['total_thc'] = oregon_flower['total_thc'].astype(float)
average_total_thc = oregon_flower.groupby('month')['total_thc'].mean()
fig, ax = plt.subplots(figsize=(13, 8))
average_total_thc.index = average_total_thc.index.to_timestamp()
ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
ax.scatter(oregon_flower['date'], oregon_flower['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total THC (%)')
ax.set_title('Average Total THC by Month in Oregon')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(0, 45)
plt.savefig(f'{assets_dir}/or-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize average total CBD by month over time.
oregon_flower['total_cbd'] = oregon_flower['total_cbd'].astype(float)
sample = oregon_flower.loc[oregon_flower['total_cbd'] < 1]
average_total_cbd = sample.groupby('month')['total_cbd'].mean()
fig, ax = plt.subplots(figsize=(13, 8))
average_total_cbd.index = average_total_cbd.index.to_timestamp()
ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
ax.scatter(sample['date'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total CBD (%)')
ax.set_title('Average Total CBD by Month in Oregon in Low CBD Samples (<1%)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(0, 0.75)
plt.savefig(f'{assets_dir}/or-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
