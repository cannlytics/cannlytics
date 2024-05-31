"""
Analyze Cannabis Lab Results | Nevada
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/30/2024
Updated: 5/30/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""

# Standard imports:
import os

# External imports:
from dotenv import dotenv_values
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Define where figures will be saved.
assets_dir = 'D://data/nevada/results/assets'

# Read curated Nevada lab result data.
stats_dir = 'D://data/nevada/results/datasets'
datafile = f'{stats_dir}/nv-results-latest.csv'
results = pd.read_csv(datafile)
print('Number of Nevada results:', len(results))

# TODO: Calculate lab market share by month.
results = results.dropna(subset=['date_tested'])
results['month'] = results['date_tested'].dt.to_period('M')
market_share = results.groupby(['month', 'lab']).size().unstack().fillna(0)
market_share = market_share.div(market_share.sum(axis=1), axis=0)

# TODO: Save the figure as an interactive HTML figure.
market_share.plot.area(
    title='Market Share by Lab by Month in Nevada',
    figsize=(13, 8),
)
plt.xlabel('')
plt.savefig(f'{assets_dir}/nv-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# TODO: Calculate tests per capita by month.
nv_population = {
    2023: 3_194_176,
    2022: 3_177_421,
    2021: 3_146_632,
    2020: 3_115_840,
    2019: 3_090_771,
}
results['year'] = results['date_tested'].dt.year
results['population'] = results['year'].map(nv_population)
nv_tests_per_capita = results.groupby('month').size() / (results.groupby('month')['population'].first() / 100_000)

# TODO: Save the figure as an interactive HTML figure.
fig, ax = plt.subplots(figsize=(13, 8))
nv_tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Nevada')
ax.set_ylabel('Tests per 100,000 People')
plt.show()

# Visualize average total THC by month over time.
results['total_thc'] = results['total_thc'].astype(float)
average_total_thc = results.groupby('month')['total_thc'].mean()

# TODO: Save the figure as an interactive HTML figure.
fig, ax = plt.subplots(figsize=(13, 8))
average_total_thc.index = average_total_thc.index.to_timestamp()
ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
ax.scatter(results['date_tested'], results['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total THC (%)')
ax.set_title('Average Total THC by Month in Nevada')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(10, 35)
plt.savefig(f'{assets_dir}/nv-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize average total CBD by month over time.
results['total_cbd'] = results['total_cbd'].astype(float)
sample = results.loc[results['total_cbd'] < 1]
average_total_cbd = sample.groupby('month')['total_cbd'].mean()

# TODO: Save the figure as an interactive HTML figure.
fig, ax = plt.subplots(figsize=(13, 8))
average_total_cbd.index = average_total_cbd.index.to_timestamp()
ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
ax.scatter(sample['date_tested'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total CBD (%)')
ax.set_title('Average Total CBD by Month in Nevada  in Low CBD Samples (<1%)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(0, 0.33)
plt.savefig(f'{assets_dir}/nv-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Visualize average total terpenes by month over time.
results['total_terpenes'] = results['total_terpenes'].astype(float)
average_total_terpenes = results.groupby('month')['total_terpenes'].mean()

# TODO: Save the figure as an interactive HTML figure.
fig, ax = plt.subplots(figsize=(13, 8))
average_total_terpenes.index = average_total_terpenes.index.to_timestamp()
ax.plot(average_total_terpenes.index, average_total_terpenes.values, label='Monthly Average Total Terpenes', color='royalblue', lw=5)
ax.scatter(results['date_tested'], results['total_terpenes'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
ax.set_xlabel('')
ax.set_ylabel('Total Terpenes (%)')
ax.set_title('Average Total Terpenes by Month in Nevada')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
plt.xticks(rotation=45)
plt.ylim(0, 4.5)
plt.xlim(results['date_tested'].min(), pd.to_datetime('2021-04-01'))
plt.savefig(f'{assets_dir}/nv-total-terpenes.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

# Optional: Save the figure as an interactive HTML figure.
# # Visualize total THC to total CBD in a scatter plot with a trend line.
# plt.scatter(results['total_thc'], results['total_cbd'])
# plt.xlabel('Total THC')
# plt.ylabel('Total CBD')
# plt.title('Total THC vs. Total CBD in Nevada')
# plt.show()

# TODO: Save the figure as an interactive HTML figure.
# Visualize total cannabinoids to total terpenes in a scatter plot with a trend line.
sample = results[
    (results['total_cannabinoids'] <= 40) &
    (results['total_cannabinoids'] > 0) &
    (results['total_terpenes'] > 0) &
    (results['total_terpenes'] <= 4.5)
]
X = sample[['total_terpenes']].dropna().values
y = sample[['total_cannabinoids']].dropna().values
model = LinearRegression(fit_intercept=False).fit(X, y)
slope = model.coef_[0][0]
avg_total_terpenes = sample['total_terpenes'].mean()
avg_total_cannabinoids = sample['total_cannabinoids'].mean()
fig, ax = plt.subplots(figsize=(13, 8))
plt.scatter(X, y, label='Data points')
plt.plot(X, model.predict(X), color='red', linewidth=2, label='Fit (through origin)')
plt.ylabel('Total Cannabinoids (%)')
plt.xlabel('Total Terpenes (%)')
plt.title('Total Cannabinoids to Total Terpenes in Cannabis Flower in Nevada', pad=20)
plt.text(0.75, 0.75, f'Estimated Ratio: {slope:.0f} to 1', transform=plt.gca().transAxes, fontsize=24, verticalalignment='top')
plt.text(0.05, 0.95, f'Avg. Total Cannabinoids: {avg_total_cannabinoids:.2f}%', transform=plt.gca().transAxes, fontsize=24, verticalalignment='top')
plt.text(0.05, 0.875, f'Avg. Total Terpenes: {avg_total_terpenes:.2f}%', transform=plt.gca().transAxes, fontsize=24, verticalalignment='top')
plt.ylim(0, 50)
plt.xlim(0, 4.5)
plt.savefig(f'{assets_dir}/nv-total-cannabinoids-to-terpenes.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()


# TODO: Upload figures to Firebase Storage, keeping track of references.


# TODO: Upload statistics to Firestore, with references to figures.


