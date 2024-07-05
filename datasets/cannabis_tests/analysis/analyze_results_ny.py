"""
Analyze Results | New York
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/26/2024
Updated: 6/26/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
import base64
from datetime import datetime
import json
import os
import shutil
import tempfile
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import CoADoc
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import get_coa_files, parse_coa_pdfs
from cannlytics.firebase import initialize_firebase
from cannlytics.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import pandas as pd
import pdfplumber


#-----------------------------------------------------------------------
# Find all COA PDFs.
#-----------------------------------------------------------------------

# Constants:
pdf_dir = 'D://data/new-york'

# Get all of the PDFs.
pdfs = get_coa_files(pdf_dir)
pdfs.sort(key=os.path.getmtime)
print('Found %i PDFs.' % len(pdfs))

# Initialize COA parsing.
parser = CoADoc()
cache = Bogart('D://data/.cache/results-ny.jsonl')
verbose = True
all_results = []


#-----------------------------------------------------------------------
# DEV: Identify all labs
#-----------------------------------------------------------------------

# Extract text from all PDFs.
extracted_data = []
for pdf_file in pdfs:
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = pdf.pages[0].extract_text() + '\n'
            extracted_data.append({'file': pdf_file, 'text': text})
    except:
        pass

# Find all COAs from a specific lab.
coas = {}
unidentified_coas = []
labs = [
    'Phyto-farma Labs',
    'Phyto-Farma Labs',
    'Kaycha Labs',
    'Keystone State Testing',
    'Green Analytics',
]
for data in extracted_data:
    for lab in labs:
        if lab in data['text']:
            lab_coas = coas.get(lab, [])
            lab_coas.append(data['file'])
            coas[lab] = lab_coas
            break
    else:
        unidentified_coas.append(data['file'])
print('Number of unidentified COAs:', len(unidentified_coas))

# DEV: Look at the first page of a PDF.
if unidentified_coas:
    pdf = pdfplumber.open(unidentified_coas[0])
    page = pdf.pages[0]
    im = page.to_image(resolution=300)
    im.debug_tablefinder()

# Count COAs per lab.
for lab, lab_coas in coas.items():
    print(lab, len(lab_coas))


#-----------------------------------------------------------------------
# Parse Kaycha Labs COAs.
#-----------------------------------------------------------------------

from cannlytics.data.coas.algorithms.kaycha import parse_kaycha_coa

# Parse COAs.
lab_coas = coas['Kaycha Labs']
for pdf in lab_coas:
    if not os.path.exists(pdf):
        if verbose: print(f'PDF not found: {pdf}')
        continue
    pdf_hash = cache.hash_file(pdf)
    if cache is not None:
        if cache.get(pdf_hash):
            if verbose: print('Cached:', pdf)
            all_results.append(cache.get(pdf_hash))
            continue
    try:
        coa_data = parse_kaycha_coa(parser, pdf)
        all_results.append(coa_data)
        if cache is not None: cache.set(pdf_hash, coa_data)
        print('Parsed:', pdf)
    except:
        print('Error:', pdf)


#-----------------------------------------------------------------------
# Parse Keystone State Testing COAs.
#-----------------------------------------------------------------------

from cannlytics.data.coas.algorithms.keystone import parse_keystone_coa

lab_coas = coas['Keystone State Testing']
for pdf in lab_coas:
    pdf_hash = cache.hash_file(pdf)
    if cache is not None:
        if cache.get(pdf_hash):
            if verbose: print('Cached:', pdf)
            all_results.append(cache.get(pdf_hash))
            continue
    try:
        coa_data = parse_keystone_coa(parser, pdf)
        all_results.append(coa_data)
        if cache is not None: cache.set(pdf_hash, coa_data)
        print('Parsed:', pdf)
    except Exception as e:
        print('Error:', pdf)
        print(e)


#-----------------------------------------------------------------------
# Parse Phyto-farma Labs COAs.
#-----------------------------------------------------------------------

from cannlytics.data.coas.algorithms.phytofarma import parse_phyto_farma_coa

# Parse Phyto-Farma Labs COAs.
lab_coas = coas['Phyto-Farma Labs'] + coas['Phyto-farma Labs']
for pdf in lab_coas:
    pdf_hash = cache.hash_file(pdf)
    if cache is not None:
        if cache.get(pdf_hash):
            if verbose: print('Cached:', pdf)
            all_results.append(cache.get(pdf_hash))
            continue
    try:
        coa_data = parse_phyto_farma_coa(parser, pdf)
        all_results.append(coa_data)
        if cache is not None: cache.set(pdf_hash, coa_data)
        print('Parsed:', pdf)
    except Exception as e:
        print('Error:', pdf)
        print(e)


#-----------------------------------------------------------------------
# TODO: Parse Green Analytics COAs.
#-----------------------------------------------------------------------

# lab_coas = coas['Green Analytics']
lab_coas = [
    'D://data/new-york\\NYSCannabis\\pdfs\\1c3sh5h-coa-1.pdf',
    'D://data/new-york\\NYSCannabis\\pdfs\\1cp4tdr-coa-1.pdf',
    'D://data/new-york\\NYSCannabis\\pdfs\\1c91onw-coa-1.pdf'
]


#-----------------------------------------------------------------------
# Optional: Parse the COAs with AI.
#-----------------------------------------------------------------------

def encode_image(image_path):
        """Encode an image as a base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')



#-----------------------------------------------------------------------
# TODO: Analyze results.
#-----------------------------------------------------------------------

from cannlytics.data.coas import standardize_results
from cannlytics.compounds import cannabinoids, terpenes
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter
import seaborn as sns

# Setup.
assets_dir = r'C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\165-labels\presentation\images\figures'
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 24,
})


def format_date(x, pos):
    try:
        return pd.to_datetime(x).strftime('%b %d, %Y')
    except ValueError:
        return ''


# Read results.
cache = Bogart('D://data/.cache/results-ny.jsonl')
results = cache.to_df()
print('Number of results:', len(results))

# Standardize results.
compounds = list(cannabinoids.keys()) + list(terpenes.keys())
# # DEV:
# compounds = [
#     'delta_9_thc',
#     'thca',
#     'alpha_humulene',
#     'beta_caryophyllene',
#     'beta_pinene',
#     'd_limonene',
# ]
results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
results['week'] = results['date'].dt.to_period('W').astype(str)
results['month'] = results['date'].dt.to_period('M').astype(str)
results = standardize_results(results, compounds)

# Sort the results by date.
results = results.sort_values('date')

# TODO: Look at values of any terpenes not yet observed.


#-----------------------------------------------------------------------
# Lab analysis
#-----------------------------------------------------------------------

# # FIXME: Visualize the number of results by lab over time.
# weekly_tests = results.groupby(['week', 'lab']).size().reset_index(name='count')
# pivot_table = weekly_tests.pivot_table(values='count', index='week', columns='lab', aggfunc='sum').fillna(0)
# plt.figure(figsize=(15, 8))
# colors = sns.color_palette('tab20', n_colors=len(pivot_table.columns))
# bottom = pd.Series([0] * len(pivot_table.index), index=pivot_table.index)
# for lab, color in zip(pivot_table.columns, colors):
#     plt.bar(
#         pivot_table.index,
#         pivot_table[lab],
#         bottom=bottom,
#         label=lab,
#         color=color,
#         edgecolor='grey',  # Add border
#         alpha=0.8,  # Add transparency
#     )
#     bottom += pivot_table[lab]
# plt.title('Number of Lab Results by Lab', pad=10)
# plt.xlabel('Week')
# plt.ylabel('Number of Results')
# plt.xticks(rotation=45)
# ticks = plt.gca().get_xticks()
# plt.gca().set_xticks(ticks[::4])  # Show every 4th xtick
# plt.legend(loc='upper right', title='Lab', ncol=2)
# plt.tight_layout()
# plt.savefig(os.path.join(assets_dir, 'lab-timeseries.png'))
# plt.show()

# This one is good:
sample = results.dropna(subset=['date'])
plt.figure(figsize=(18, 8))
ax = sns.countplot(data=sample, x='week', hue='lab', palette='tab10')
plt.title('Number of Lab Results by Lab', pad=10)
plt.xlabel('')
plt.ylabel('Number of Results')
plt.xticks(rotation=45)
ticks = ax.get_xticks()
ax.set_xticks(ticks[::4])
ax.set_xticklabels([format_date(item.get_text(), None) for item in ax.get_xticklabels()])
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'lab-timeseries.png'))
plt.show()


#-----------------------------------------------------------------------
# Producer analysis
#-----------------------------------------------------------------------

# Assign standard producer names.
producer_names = {
    'Hudson Valley Cannabis LLC': 'Hudson Cannabis',
    'MFNY Processor LLC': 'MFNY',
    '': 'Unknown',
    'Hepworth Ag, INC': 'Hepworth Ag',
    'Processing': 'Unknown',
    'MFNY PROCESSOR LLC': 'MFNY',
    'Hudson Valley Hemp Company': 'Hudson Cannabis',
    'Hepworth Ag, Inc.': 'Hepworth Ag',
    'NYHO Labs LLC': 'NYHO Labs',
    'Hudson Valley Hemp Company, LLC': 'Hudson Cannabis',
    'Cirona Labs': 'Cirona Labs',
    'Hudson Cannabis c/o Hudson Valley Hemp Company, LLC': 'Hudson Cannabis',
    'Milton, NY, 12547, US': 'Unknown',
}
results['producer_dba'] = results['producer'].map(producer_names)

# FIXME: Visualize the number of results by producer over time.
# results['week'] = results['date'].dt.to_period('W').dt.start_time
# weekly_tests = results.groupby(['week', 'dba']).size().reset_index(name='count')
# pivot_table = weekly_tests.pivot_table(values='count', index='week', columns='dba', aggfunc='sum').fillna(0)
# plt.figure(figsize=(21, 9))
# colors = sns.color_palette('tab20', n_colors=len(pivot_table.columns))
# bottom = None
# for dba, color in zip(pivot_table.columns, colors):
#     plt.bar(
#         pivot_table.index,
#         pivot_table[dba],
#         bottom=bottom,
#         label=dba,
#         color=color,
#         edgecolor='grey',  # Add border
#         alpha=0.8,  # Add transparency
#     )
#     if bottom is None:
#         bottom = pivot_table[dba]
#     else:
#         bottom += pivot_table[dba]
# plt.title('Number of Lab Results by Producer', pad=10)
# plt.xlabel('Week')
# plt.ylabel('Number of Results')
# plt.xticks(rotation=45)
# ticks = plt.gca().get_xticks()
# plt.gca().set_xticks(ticks[::4])  # Show every 4th xtick
# plt.legend(loc='upper right', title='Producer', ncol=2)
# plt.tight_layout()
# plt.savefig(os.path.join(assets_dir, 'producer-timeseries.png'))
# plt.show()

# This one is good.
sample = results.dropna(subset=['date'])
plt.figure(figsize=(18, 8))
ax = sns.countplot(data=sample, x='week', hue='producer_dba', palette='tab10')
plt.title('Number of Lab Results by Producer', pad=10)
plt.xlabel('')
plt.ylabel('Number of Results')
plt.xticks(rotation=45)
ticks = ax.get_xticks()
ax.set_xticks(ticks[::4])
ax.set_xticklabels([format_date(item.get_text(), None) for item in ax.get_xticklabels()])
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'producer-timeseries.png'))
plt.show()


#-----------------------------------------------------------------------
# Product type analysis
#-----------------------------------------------------------------------

# Assign product types.
flower_types = [
    'Plant, Flower - Cured',
    'Flower',
]
preroll_types = [
    'Plant, Preroll',
]
infused_preroll_types = [
    'Plant, Enhanced Preroll',
]
concentrate_types = [
    'Concentrate',
    'Derivative',
    'Concentrates & Extract, Vape Cartridge',
    'Concentrates & Extract, Live Rosin',
    'Concentrates & Extract, Concentrate',
    'Concentrates & Extract, Rosin',
    'Concentrates & Extract, Distillate'
]
edible_types = [
    'Edible',
    'Ingestible, Gummy',
    'Ingestible, Edibles',
]


def assign_product_type(x):
    if x in flower_types:
        return 'Flower'
    if x in concentrate_types:
        return 'Concentrate'
    if x in edible_types:
        return 'Edible'
    if x in preroll_types:
        return 'Preroll'
    if x in infused_preroll_types:
        return 'Infused Preroll'
    return 'Other'


# Assign standard product type.
results['standard_product_type'] = results['product_type'].apply(assign_product_type)

# Define a consistent color palette.
product_type_palette = {
    'Flower': '#2ca02c',        # green
    'Concentrate': '#ff7f0e',   # orange
    'Edible': '#8c564b',        # brown
    'Preroll': '#1f77b4',       # blue
    'Infused Preroll': '#9467bd', # purple
    'Other': '#d62728'          # red
}

# Visualize the number of results by product type over time
sample = results.dropna(subset=['date'])
sample.sort_values('date', inplace=True)
plt.figure(figsize=(18, 8))
ax = sns.countplot(data=sample, x='week', hue='standard_product_type', palette=product_type_palette)
plt.title('Number of Lab Results by Product Type', pad=10)
plt.xlabel('')
plt.ylabel('Number of Results')
plt.xticks(rotation=45)
ticks = ax.get_xticks()
ax.set_xticks(ticks[::4])
# FIXME:
ax.set_xticklabels([format_date(item.get_text(), None) for item in ax.get_xticklabels()])
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'product-type-timeseries.png'))
plt.show()

# Visualize the proportions of product types in a pie chart
plt.figure(figsize=(12, 12))
results['standard_product_type'].value_counts().plot.pie(
    autopct='%1.1f%%',
    startangle=90,
    colors=[product_type_palette[key] for key in results['standard_product_type'].value_counts().index]
)
plt.title('Proportions of Product Types')
plt.ylabel('')
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'product-type-pie.png'))
plt.show()

# Visualize total cannabinoids and total terpenes in a scatter plot
sample = results.loc[results['standard_product_type'] != 'Other']
plt.figure(figsize=(18, 8))
ax = sns.scatterplot(
    data=sample,
    y='total_cannabinoids',
    x='total_terpenes',
    hue='standard_product_type',
    palette=product_type_palette,
    s=200
)
plt.title('Total Cannabinoids to Total Terpenes', pad=10)
plt.ylabel('Total Cannabinoids (%)')
plt.xlabel('Total Terpenes (%)')
plt.xlim(0, 10.5)
plt.ylim(0, 100)
legend = ax.legend(title='Product Type', bbox_to_anchor=(1.05, 1), loc='upper left')
for leg_entry in legend.legendHandles:
    leg_entry.set_sizes([200])
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'cannabinoids-to-terpenes.png'))
plt.show()


# Optional: Visualize total THC to CBD.


#-----------------------------------------------------------------------
# Timeseries analysis.
#-----------------------------------------------------------------------

import statsmodels.api as sm

# Look at the trend in THCA in flower.
compound = 'thca'
sample = results[results['standard_product_type'] == 'Flower']
avg = results.groupby(['month', 'standard_product_type'])[compound].mean().reset_index()
avg['month'] = pd.to_datetime(avg['month'], errors='coerce')
flower_data = avg[avg['standard_product_type'] == 'Flower']
flower_data = flower_data.dropna(subset=[compound, 'month'])
flower_data['month_num'] = range(len(flower_data))
X = sm.add_constant(flower_data['month_num'])
y = flower_data[compound]
model = sm.OLS(y, X).fit()
slope = model.params['month_num']
direction = '+' if slope > 0 else '-'
plt.figure(figsize=(13, 8))
plt.plot(flower_data['month'], flower_data[compound], 'bo-', label='Avg. THCA by month', linewidth=2)
plt.plot(flower_data['month'], model.predict(X), 'r-', label=f'Trend: {direction}{slope:.2f}% per month', linewidth=2)
plt.scatter(sample['date'], sample[compound], color='lightblue', s=80)
plt.title('Trend of THCA in Flower in New York', pad=10)
plt.xlabel('')
plt.ylabel('THCA')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'average-thca-by-month.png'))
plt.show()

                                                                                                                                       
#-----------------------------------------------------------------------
#  Visualize terpene ratios.
#-----------------------------------------------------------------------

# Function to create scatter plots
def create_scatter_plot(x_col, y_col, title, x_label, y_label, filename):
    plt.figure(figsize=(18, 8))
    ax = sns.scatterplot(
        data=results,
        x=x_col,
        y=y_col,
        hue='standard_product_type',
        palette=product_type_palette,
        s=200
    )
    plt.title(title, pad=10)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    legend = ax.legend(title='Product Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    for leg_entry in legend.legendHandles:
        leg_entry.set_sizes([200])
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, filename))
    plt.show()


# Visualize the ratio of `alpha_humulene` to `beta_caryophyllene`
create_scatter_plot(
    y_col='alpha_humulene',
    x_col='beta_caryophyllene',
    title='Ratio of Alpha-Humulene to Beta-Caryophyllene by Product Type',
    y_label='Alpha-Humulene',
    x_label='Beta-Caryophyllene',
    filename='alpha_humulene_to_beta_caryophyllene.png'
)

# Visualize the ratio of `beta_pinene` to `d_limonene`
create_scatter_plot(
    y_col='beta_pinene',
    x_col='d_limonene',
    title='Ratio of Beta-Pinene to D-Limonene by Product Type',
    y_label='Beta-Pinene',
    x_label='D-Limonene',
    filename='beta_pinene_to_d_limonene.png'
)


#-----------------------------------------------------------------------
# Regression analysis on THCA.
#-----------------------------------------------------------------------

from patsy import dmatrices

# Run a regression on THCA in flower.
compound = 'thca'
product_type = 'Flower'
sample = results[results['standard_product_type'] == product_type]
sample['month'] = pd.to_datetime(sample['month'], errors='coerce')
sample = sample.dropna(subset=['month'])
sample['month_num'] = sample['month'].rank(method='dense').astype(int) - 1
y, X = dmatrices('thca ~ month_num + C(lab) + C(dba)', data=sample, return_type='dataframe')
model = sm.OLS(y, X).fit()
print(model.summary().as_latex())


#-----------------------------------------------------------------------
# TODO: Save the results.
#-----------------------------------------------------------------------

# Save the results.
last_test_date = results['date'].max().strftime('%Y-%m-%d')
outfile = f'D://data/new-york/ny-results-{last_test_date}.xlsx'
results.to_excel(outfile, index=False)
print('Saved:', outfile)
