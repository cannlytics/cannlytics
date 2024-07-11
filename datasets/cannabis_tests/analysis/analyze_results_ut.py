"""
Analyze Results | Utah
Copyright (c) 2023-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/4/2024
Updated: 7/9/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
import os
from typing import List
from zipfile import ZipFile

# External imports:
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Internal imports:
from cannlytics import __version__
from cannlytics.data.cache import Bogart
from cannlytics.data.coas.parsing import get_coa_files
from cannlytics.data.coas import CoADoc
from cannlytics.data.coas.algorithms.utah import parse_utah_coa
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import find_unique_analytes


#-----------------------------------------------------------------------
# Find all of the COA PDFs.
#-----------------------------------------------------------------------

def unzip_folder(folder, destination, remove=True):
    """Unzip a folder.
    Args:
        pdf_dir (str): The directory where the folder is stored.
        folder (str): The name of the folder to unzip.
    """
    os.makedirs(destination, exist_ok=True)
    with ZipFile(folder) as zip_ref:
        zip_ref.extractall(destination)
    if remove:
        os.remove(folder)


# Unzip all of the folders.
pdf_dir = r'D:\data\public-records\Utah'
folders = [os.path.join(pdf_dir, x) for x in os.listdir(pdf_dir) if x.endswith('.zip')]
for folder in folders:
    unzip_folder(folder, pdf_dir)
    print('Unzipped:', folder)

# Get all of the PDFs.
pdfs = get_coa_files(pdf_dir)
pdfs.sort(key=os.path.getmtime)
print('Found %i PDFs.' % len(pdfs))


#-----------------------------------------------------------------------
# Parse Utah Department of Agriculture and Food COAs.
#-----------------------------------------------------------------------

def parse_coa_pdfs(
        pdfs,
        algorithm=None,
        parser=None,
        cache=None,
        data=None,
        verbose=True,
    ) -> List[dict]:
    """Parse a list of COA PDFs.
    Args:
        pdfs (List[str]): A list of PDFs to parse.
        algorithm (function): The parsing algorithm to use.
        parser (object): The parser object to use.
        cache (object): The cache object to use.
        data (List[dict]): The data to append to.
        verbose (bool): Whether to print verbose output.
    Returns:
        List[dict]: The parsed data.
    """
    if data is None:
        data = []
    if parser is None:
        parser = CoADoc()
    for pdf in pdfs:
        if not os.path.exists(pdf):
            if verbose: print(f'PDF not found: {pdf}')
            continue
        if cache is not None:
            pdf_hash = cache.hash_file(pdf)
            if cache is not None:
                if cache.get(pdf_hash):
                    if verbose: print('Cached:', pdf)
                    data.append(cache.get(pdf_hash))
                    continue
        try:
            if algorithm is not None:
                coa_data = algorithm(parser, pdf)
            else:
                coa_data = parser.parse(pdf)
            data.append(coa_data)
            if cache is not None:
                cache.set(pdf_hash, coa_data)
            print('Parsed:', pdf)
        except:
            print('Error:', pdf)
    return data


# Initialize COA parsing.
cache = Bogart('D://data/.cache/results-ut.jsonl')

# DEV: Clear the cache.
cache.clear()

# Parse COAs.
all_results = parse_coa_pdfs(
    pdfs,
    algorithm=parse_utah_coa,
    cache=cache,
)

# Read results.
results = cache.to_df()
print('Number of results:', len(results))

# Standardize time.
results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
results['week'] = results['date'].dt.to_period('W').astype(str)
results['month'] = results['date'].dt.to_period('M').astype(str)
results = results.sort_values('date')

# Standardize compounds.
# Note: Removes nuisance analytes.
analytes = find_unique_analytes(results)
nuisance_analytes = [
    'det_detected',
    'global_shortages_of_laboratory_suppliesto',
    'here_recorded_may_not_be_used_as_an_endorsement_for_a_product',
    'information_see',
    'information_see_https_totoag_utah_govto_2021_to_04_to_29_toudaf_temporarily_adjusts_medical_cannabis_testing_protocols_due_to',
    'nd_not_detected',
    'notes',
    'notes_sample_was_tested_as_received_the_cannabinoid_results_were_not_adjusted_for_moisture_content',
    'phtatpthso_togtoaegn_utetashti_nggo_vwto_2_a_0_s',
    'recorded_the_results_here_recorded_may_not_be_used_as_an_endorsement_for_a_product',
    'results_pertain_only_to_the_test_sample_listed_in_this_report',
    'see_https_totoag_utah_govto_2021_to_04_to_29_toudaf_temporarily_adjusts_medical_cannabis_testing_protocols_due_to_global',
    'shortages_of_laboratory_suppliesto',
    'tac_2500000',
    'tac_t',
    'this_report_may_not_be_reproduced_except_in_its_entirety',
    'total_cbd',
    'total_thc',
]
analytes = analytes - set(nuisance_analytes)
# TODO: Alphabetize the analytes.
analytes = sorted(list(analytes))
results = standardize_results(results, analytes)

# Save the results.
last_test_date = results['date'].max().strftime('%Y-%m-%d')
outfile = f'D://data/utah/ut-results-{last_test_date}.xlsx'
latest = f'D://data/utah/ut-results-latest.csv'
results.to_excel(outfile, index=False)
results.to_csv(latest, index=False)
print('Saved:', outfile)
print('Saved:', latest)

# Print out features.
features = {x: 'string' for x in results.columns}
print('Number of features:', len(features))
print('Features:', features)


#-----------------------------------------------------------------------
# Analyze Utah results.
#-----------------------------------------------------------------------

def format_date(x, pos):
    try:
        return pd.to_datetime(x).strftime('%b %#d, %Y')
    except ValueError:
        return ''

# Setup.
assets_dir = r'C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\165-labels\presentation\images\figures'
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 24,
})

# FIXME: Read the curated results.

# # Read results.
# results = cache.to_df()
# print('Number of results:', len(results))

# # Standardize time.
# results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
# results['week'] = results['date'].dt.to_period('W').astype(str)
# results['month'] = results['date'].dt.to_period('M').astype(str)
# results = results.sort_values('date')

# # Standardize compounds.
# analytes = find_unique_analytes(results)
# results = standardize_results(results, analytes)



#-----------------------------------------------------------------------
# Lab analysis
#-----------------------------------------------------------------------

# Visualize the number of tests by date.
plt.figure(figsize=(18, 8))
ax = sns.countplot(data=results.dropna(subset=['month']), x='month', color='skyblue')
plt.title('Number of Tests by Date in Utah', pad=10)
plt.xlabel('')
plt.ylabel('Number of Tests')
plt.xticks(rotation=45)
ticks = ax.get_xticks()
ax.set_xticks(ticks[::4])  # Adjust the interval as needed
ax.set_xticklabels([format_date(item.get_text(), None) for item in ax.get_xticklabels()])
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'ut-lab-timeseries.png'))
plt.show()


#-----------------------------------------------------------------------
# Producer analysis
#-----------------------------------------------------------------------

# Assign standard producer names.
producer_names = {
    'Harvest of Utah': 'Harvest',
    'True North of Utah': 'True North',
    'Tryke': 'Tryke',
    'Standard Wellness of Utah': 'Standard Wellness',
    'Tryke Companies of Utah': 'Tryke',
    'Tryke Companies of\nUtah': 'Tryke',
    'Pure Plan': 'Pure Plan',
    'Riverside Farm': 'Riverside Farm',
    'Riverside Farms': 'Riverside Farm',
    'Wholesome Ag': 'Wholesome Ag',
    'Zion Cultivars': 'Zion Cultivars',
    'Zion Cultivators': 'Zion Cultivars',
    'Dragonfly Greenhouse': 'Dragonfly',
    'Dragonfly Processing': 'Dragonfly',
    'UMC Program': 'UMC Program',
    'Zion Alchemy': 'Zion Alchemy',
    'Wasatch Extraction': 'Wasatch Extraction',
    'Standard Wellness of Utah Great Salt Lake 1/8': 'Standard Wellness',
    'Tryke Companies of Utah Who Dat Orange': 'Tryke',
}
results['producer_dba'] = results['producer'].map(producer_names)

# Aggregate data by month and DBA
monthly_tests = results.groupby(['month', 'producer_dba']).size().reset_index(name='count')

# Plotting the time series line plot
colors = sns.color_palette('tab20', n_colors=len(monthly_tests['producer_dba'].unique()))
pivot_table = monthly_tests.pivot_table(values='count', index='month', columns='producer_dba', aggfunc='sum').fillna(0)
plt.figure(figsize=(21, 9))
bottom = None
for dba in pivot_table.columns:
    plt.bar(
        pivot_table.index,
        pivot_table[dba],
        bottom=bottom,
        label=dba,
        color=colors.pop(0),
        edgecolor='grey',
        alpha=0.8,
    )
    if bottom is None:
        bottom = pivot_table[dba]
    else:
        bottom += pivot_table[dba]
plt.title('Number of Tests by Producer by Month in Utah', pad=10)
plt.xlabel('')
plt.ylabel('Number of Tests')
plt.xticks(rotation=45)
ticks = plt.gca().get_xticks()
plt.gca().set_xticks(ticks[::3])  # Show every 3rd xtick
plt.legend(loc='upper left', title='Producer', ncol=2)
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'ut-producer-timeseries.png'))
plt.show()


#-----------------------------------------------------------------------
# Timeseries analysis.
#-----------------------------------------------------------------------

import statsmodels.api as sm

# Look at the trend in THCA in flower.
compound = 'thca'
sample = results.loc[results['date'] >= pd.to_datetime('2024-01-01')]
avg = sample.groupby(['month'])[compound].mean().reset_index()
avg['month'] = pd.to_datetime(avg['month'], errors='coerce')
avg = avg.dropna(subset=[compound, 'month'])
avg['month_num'] = range(len(avg))
X = sm.add_constant(avg['month_num'])
y = avg[compound]
model = sm.OLS(y, X).fit()
slope = model.params['month_num']
direction = '+' if slope > 0 else '-'
plt.figure(figsize=(13, 8))
plt.plot(avg['month'], avg[compound], 'bo-', label='Avg. THCA by month', linewidth=2)
plt.plot(avg['month'], model.predict(X), 'r-', label=f'Trend: {direction}{slope:.2f}% per month', linewidth=2)
plt.scatter(sample['date'], sample[compound], color='lightblue', s=80)
plt.title('Trend of THCA in Utah Cannabis Flower', pad=10)
plt.xlabel('')
plt.ylabel('THCA')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'ut-average-thca-by-month.png'))
plt.show()


#-----------------------------------------------------------------------
#  Visualize terpene ratios.
#-----------------------------------------------------------------------

from adjustText import adjust_text

# Read in NY data and compare to UT data.
ny_cache = Bogart('D://data/.cache/results-ny.jsonl')
ny_results = ny_cache.to_df()
ny_flower_types = [
    'Plant, Flower - Cured',
    'Flower',
]
ny_flower = ny_results.loc[ny_results['product_type'].isin(ny_flower_types)]
ny_flower = standardize_results(ny_flower, analytes)
ny_flower['state'] = 'NY'
ny_flower['date'] = pd.to_datetime(ny_flower['date_tested'], format='mixed')
ny_flower['week'] = ny_flower['date'].dt.to_period('W').astype(str)
ny_flower['month'] = ny_flower['date'].dt.to_period('M').astype(str)

# Create the sample.
results['state'] = 'UT'
# sample = results.loc[results['date'] >= pd.to_datetime('2024-01-01')]
sample = results.copy()
sample = pd.concat([sample, ny_flower])
# sample = sample.loc[sample['date'] >= pd.to_datetime('2024-01-01')]

# Function to create scatter plots
def create_scatter_plot(x_col, y_col, title, x_label, y_label, filename, annotate=False):
    plt.figure(figsize=(18, 8))
    ax = sns.scatterplot(
        data=sample,
        x=x_col,
        y=y_col,
        hue='state',
        s=200
    )
    plt.title(title, pad=10)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    legend = ax.legend(title='Product Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    for leg_entry in legend.legendHandles:
        leg_entry.set_sizes([200])

    # Annotate 3 samples with beta_pinene to d_limonene ratio greater than 0.5
    if annotate:
        texts = []
        random_state = 420_000
        high_ratio_samples = sample[sample['beta_pinene'] / sample['d_limonene'] > 0.75] \
            .sample(n=5, random_state=random_state)
        for i, row in high_ratio_samples.iterrows():
            if pd.notna(row[x_col]) and pd.notna(row[y_col]):
                texts.append(ax.text(
                    row[x_col],
                    row[y_col],
                    row['product_name'],
                    fontsize=24,
                    color='crimson',
                ))
        adjust_text(texts, only_move={'points': 'xy', 'texts': 'xy'}, arrowprops=dict(arrowstyle='-', color='grey'))

    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, filename))
    plt.show()


# Visualize the ratio of `beta_pinene` to `d_limonene`
create_scatter_plot(
    y_col='beta_pinene',
    x_col='d_limonene',
    title='Ratio of Beta-Pinene to D-Limonene in New York and Utah Cannabis Flower',
    y_label='Beta-Pinene',
    x_label='D-Limonene',
    filename='ut-beta-pinene-to-d-limonene.png',
    annotate=True
)

# Visualize the ratio of `alpha_humulene` to `beta_caryophyllene`
create_scatter_plot(
    y_col='alpha_humulene',
    x_col='beta_caryophyllene',
    title='Ratio of Alpha-Humulene to Beta-Caryophyllene in New York and Utah Cannabis Flower',
    y_label='Alpha-Humulene',
    x_label='Beta-Caryophyllene',
    filename='ut-alpha-humulene-to-beta-caryophyllene.png',
    annotate=False
)
