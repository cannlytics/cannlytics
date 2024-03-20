"""
Analyze California Cannabis Lab Results
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2023
Updated: 3/19/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
import ast
import json
import matplotlib.pyplot as plt
import seaborn as sns

# External imports:
from cannlytics.data.coas import get_result_value
from cannlytics.utils import convert_to_numeric
import pandas as pd
import statsmodels.api as sm


#-----------------------------------------------------------------------
# Read all lab results.
#-----------------------------------------------------------------------

import os
import pandas as pd


# Aggregate SC Labs results.
data_dir = r"D:\data\california\lab_results\datasets\sclabs"
datafiles = os.listdir(data_dir)
datafiles = [os.path.join(data_dir, x) for x in datafiles if x.endswith('.xlsx')]
datafiles = [x for x in datafiles if 'all' not in x and 'urls' not in x]
print('Number of datafiles:', len(datafiles))
all_results = []
for datafile in datafiles:
    print('Reading:', datafile)
    try:
        data = pd.read_excel(datafile)
    except:
        print('Error reading:', datafile)
        continue
    all_results.append(data)
all_results = pd.concat(all_results)
all_results.drop_duplicates(subset=['sample_id', 'results_hash'], inplace=True)
all_results = all_results.loc[all_results['results'] != '[]']
print('Number of SC Labs results:', len(all_results))

# Save SC Labs results.
date = pd.Timestamp.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'all-sc-labs-results-{date}.xlsx')
all_results.to_excel(outfile, index=False)
print(f'Saved {len(all_results)} SC Labs results:', outfile)

    

# # Identify all unique cannabinoids and terpenes.
# cannabinoids = []
# terpenes = []
# for item in emerald['results']:
#     lab_results = ast.literal_eval(item)
#     for result in lab_results:
#         if result['analysis'] == 'cannabinoids':
#             cannabinoids.append(result['name'])
#         elif result['analysis'] == 'terpenes':
#             terpenes.append(result['name'])
# cannabinoids = list(set(cannabinoids))
# terpenes = list(set(terpenes))
# print('Cannabinoids:', cannabinoids)
# print('Terpenes:', terpenes)


# === Setup ===

# Setup plotting style.
plt.style.use('fivethirtyeight')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.family': 'Times New Roman',
    'font.size': 24,
})


# === Read the data ===

# Define California datasets.
CA_LAB_RESULTS = {
    'Flower Company': {
        'datafiles': [
            r"D:\data\california\lab_results\datasets\flower-company\ca-all-results-flower-company.xlsx"
        ],
    },
    'Glass House Farms': {
        'datafiles': [
            r"D:\data\california\lab_results\ca-lab-results-2024-01-24.xlsx",
        ],
    },
    'SC Labs':{
        'datafiles': [
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-23-12-25-04.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-24-01-09-39.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-25-09-39-02.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-25-12-12-21.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-31-09-23-07.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-31-09-25-31.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2023-12-31-14-45-26.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-02-00-39-36.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-02-22-27-08.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-03-06-24-11.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-04-17-48-16.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-04-18-24-00.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-05-02-17-28.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-05-18-01-26.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-05-23-23-15.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-06-15-12-32.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-06-16-25-42.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-06-16-59-56.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-06-17-04-10.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-06-19-47-41.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-08-18-12-08.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-11-18-31-09.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-15-08-42-54.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-17-11-04-10.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-19-00-00-22.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-20-15-57-24.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-21-16-12-00.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-29-02-37-48.xlsx",
            r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-29-07-16-54.xlsx",
        ],
    },
}

# Read all datafiles.
all_results = []
for source in CA_LAB_RESULTS:
    for datafile in CA_LAB_RESULTS[source]['datafiles']:
        try:
            data = pd.read_excel(datafile)
        except:
            print('Error reading:', datafile)
            continue
        all_results.append(data)

# Aggregate results, removing lab results that are being processed (no results).
results = pd.concat(all_results)
print('Number of results before dropping in-progress:', len(results))
results = results.loc[results['results'] != "[]"]
print('Number of results before dropping duplicates:', len(results))
results.drop_duplicates(subset=['sample_id'], inplace=True)
print('Number of results:', len(results))

# Save the data.
date = pd.to_datetime('today').strftime('%Y-%m-%d')
outfile = f"D://data/california/lab_results/datasets/ca-results-{date}.csv"
results.to_csv(outfile, index=False)
print('Saved:', outfile)


# === Timeseries Analysis ===

# Flower company results.
flower_co = pd.read_excel(r"D:\data\california\lab_results\datasets\flower-company\ca-all-results-flower-company.xlsx")

# SC Labs results.
all_results = []
for datafile in reversed(CA_LAB_RESULTS['SC Labs']['datafiles']):
    try:
        data = pd.read_excel(datafile)
    except:
        print('Error reading:', datafile)
        continue
    all_results.append(data)
results = pd.concat(all_results)
print('Number of results before dropping in-progress:', len(results))
results = results.loc[results['results'] != "[]"]
print('Number of results before dropping duplicates:', len(results))
results.drop_duplicates(subset=['sample_id'], inplace=True)
print('Number of results:', len(results))
date = pd.to_datetime('today').strftime('%Y-%m-%d')
outfile = f"D://data/california/lab_results/datasets/ca-results-sclabs-{date}.csv"
results.to_csv(outfile, index=False)
print('Saved:', outfile)
sclabs = results.copy()
sclabs = sclabs.loc[sclabs['lab_state'] == 'CA']

# Glass House Farms results.
glass_house = pd.read_excel(r"D:\data\california\lab_results\ca-lab-results-2024-01-24.xlsx")


# Define when standard method was effective.
# Source: https://cannabis.ca.gov/cannabis-laws/rulemaking/standard-cannabinoids-test-method-and-standardized-operating-procedures/
effective_date = pd.to_datetime('2023-10-01')
compliance_date = pd.to_datetime('2024-01-01')

# TODO: Create a timeseries of average total_cannabinoids, total_thc by week
# for the datasets: `flower_co`, `sclabs`, `glass_house`.
# Annotate the effective date and compliance date with a vertical line.

def preprocess_and_aggregate(df):
    """
    Preprocess the data and aggregate it to calculate weekly averages.
    """
    # Ensure the date column is in datetime format
    df['date'] = pd.to_datetime(df['date_tested'], errors='coerce')

    # Keep only flower samples.
    flower_types = [
        'Flower',
        'Flower, Inhalable',
        'Flower, Product Inhalable',
        'Flower, Medical Inhalable',
        'Plant (Flower - Cured)',
        'Plant (Bulk Flower)',
    ]
    preroll_types = [
        'Pre-roll',
        'Plant (Preroll)',
        'Pre-Roll Cannabis, Product Inhalable',
        'Pre-roll Cannabis, Product Inhalable',
        'Pre-roll Product, Product Inhalable',
        'Pre-roll Product, Inhalable',
        'Pre-Roll Cannabis, Inhalable',
        'Pre-roll Cannabis, Inhalable',
    ]
    sample = df.loc[df['product_type'].isin(flower_types)]

    # Filter relevant columns and remove rows with missing values in these columns
    sample = sample[['date', 'total_cannabinoids', 'total_thc']].dropna()

    # Resample to weekly frequency, calculating the mean of total_cannabinoids and total_thc
    return sample.resample('M', on='date').mean().reset_index()


# Preprocess and aggregate data for each dataset.
flower_co_weekly = preprocess_and_aggregate(flower_co)
sclabs_weekly = preprocess_and_aggregate(sclabs)
glass_house_weekly = preprocess_and_aggregate(glass_house)


def plot_timeseries(df, title):
    """
    Plot the timeseries data with annotations for effective and compliance dates.
    """
    plt.figure(figsize=(15, 8))
    sns.lineplot(x='date', y='total_cannabinoids', data=df, label='Total Cannabinoids')
    sns.lineplot(x='date', y='total_thc', data=df, label='Total THC')
    plt.axvline(x=effective_date, color='#1a1a1a', linestyle='--', lw=2)
    plt.axvline(x=compliance_date, color='#1a1a1a', linestyle='--', lw=2)
    plt.text(
        effective_date,
        plt.gca().get_ylim()[1] - 1,
        'Effective Date',
        color='#1a1a1a',
        ha='right'
    )
    plt.text(
        compliance_date,
        plt.gca().get_ylim()[1] - 2,
        'Compliance Date',
        color='#1a1a1a',
        ha='right',
    )
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Average Value')
    plt.legend(loc='upper left')
    plt.tight_layout()

# Plotting each dataset.
plot_timeseries(flower_co_weekly, 'Flower Company - Average Total Cannabinoids and THC by Month')
plot_timeseries(sclabs_weekly, 'SC Labs - Average Total Cannabinoids and THC by Month')
plot_timeseries(glass_house_weekly, 'Glass House Farms - Average Cannabinoids and THC by Month')
plt.show()


def preprocess_and_aggregate_by_lab(df):
    """
    Preprocess the data and aggregate it to calculate monthly averages of total THC by lab.
    """
    # Ensure the date column is in datetime format
    df['date'] = pd.to_datetime(df['date_tested'], errors='coerce')

    # Filtering for flower types
    flower_types = [
        'Flower', 'Flower, Inhalable', 'Flower, Product Inhalable', 
        'Flower, Medical Inhalable', 'Plant (Flower - Cured)', 'Plant (Bulk Flower)'
    ]
    df = df.loc[df['product_type'].isin(flower_types)]

    # Keep relevant columns
    df = df[['date', 'lab', 'total_cannabinoids']].dropna()

    # Resampling to monthly frequency and grouping by lab
    monthly_avg = df.groupby(['lab']).resample('M', on='date').mean().reset_index()

    return monthly_avg

# Preprocess and aggregate data for flower_co by lab.
flower_co_monthly_by_lab = preprocess_and_aggregate_by_lab(flower_co)

def plot_timeseries_by_lab(df, title):
    """
    Plot the timeseries data of monthly average total THC by lab.
    """
    plt.figure(figsize=(15, 8))
    labs = df['lab'].unique()
    colors = sns.color_palette('tab10', n_colors=len(labs))
    for i, lab in enumerate(labs):
        lab_data = df[df['lab'] == lab]
        sns.lineplot(
            x='date',
            y='total_cannabinoids',
            data=lab_data,
            label=lab,
            color=colors[i],
        )
    plt.axvline(x=effective_date, color='#1a1a1a', linestyle='--', lw=2)
    plt.axvline(x=compliance_date, color='#1a1a1a', linestyle='--', lw=2)
    plt.text(effective_date, plt.gca().get_ylim()[1] - 1, 'Effective Date', color='#1a1a1a', ha='right')
    plt.text(compliance_date, plt.gca().get_ylim()[1] - 2, 'Compliance Date', color='#1a1a1a', ha='right')
    plt.xlim(pd.to_datetime('2023-01-01'), pd.to_datetime('2024-02-01'))
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Average Total Cannabinoids')
    plt.legend(title='Lab', loc='upper left')
    plt.tight_layout()

# Plotting the timeseries for flower_co by lab
plot_timeseries_by_lab(
    flower_co_monthly_by_lab,
    'Flower Company - Average Total Cannabinoids by Lab by Month'
)
plt.show()


# === Chemical Analysis ===

# Define commonly observed cannabinoids and terpenes.
cannabinoids = [
    'thca',
    'cbga',
    'cbca',
    'delta_9_thc',
    'cbg',
    'thcva',
    'cbda',
    'delta_8_thc',
    'thcv',
    'cbd',
    'cbdv',
    'cbdva',
    'cbl',
    'cbn',
    'cbc',
]
terpenes = [
    'beta_caryophyllene',
    'd_limonene',
    'alpha_humulene',
    'beta_myrcene',
    'beta_pinene',
    'alpha_pinene',
    'beta_ocimene',
    'alpha_bisabolol',
    'terpineol',
    'fenchol',
    'linalool',
    'borneol',
    'camphene',
    'terpinolene',
    'fenchone',
    'nerolidol',
    'trans_beta_farnesene',
    'citronellol',
    'sabinene_hydrate',
    'nerol',
    'valencene',
    'sabinene',
    'alpha_phellandrene',
    'delta_3_carene',
    'alpha_terpinene',
    'p_cymene',
    'eucalyptol',
    'gamma_terpinene',
    'isopulegol',
    'camphor',
    'isoborneol',
    'menthol',
    'pulegone',
    'geraniol',
    'geranyl_acetate',
    'alpha_cedrene',
    'caryophyllene_oxide',
    'guaiol',
    'cedrol'
]

# Get the results for each cannabinoid and terpene.
for a in cannabinoids + terpenes:
    print('Augmenting:', a)
    results[a] = results['results'].apply(
        lambda x: get_result_value(x, a, key='key')
    )




# # === Look at the Emerald Cup results ===
# emerald_2023 = results.loc[results['producer'] == 'Emerald Cup 2023']
# emerald_2022 = results.loc[results['producer'] == 'Emerald Cup 2022']
# emerald_2020 = results.loc[results['producer'] == 'Emerald Cup 2020']
# emerald_2023['year'] = 2023
# emerald_2022['year'] = 2022
# emerald_2020['year'] = 2020
# emerald = pd.concat([emerald_2023, emerald_2022, emerald_2020])

# # TODO: Merge with ranking data.
# winners_2022 = pd.read_excel('data/emerald-cup-winners-2022.xlsx')
# winners_2023 = pd.read_excel('data/emerald-cup-winners-2023.xlsx')

# winners_2022['product_name'] = winners_2022['entry_name'].apply(
#     lambda x: x.split(' – ')[-1]
# )


# TODO: See which strain has the highest terpenes.
# 2022:
# Highest Terpene Content – Flower	Woodwide Farms – Mendo Crumble
# Highest Terpene Content – Solventless	Have Hash – Rainbow Belts
# Highest Terpene Content – Solvent (Hydrocarbon)	Errl Hill – Gazberries



# TODO: See which strain has the most diverse terpene profile.
# 2022: Most Unique Terpene Profile	Atrium Cultivation – Juice Z


# TODO: See which strain has the most diverse cannabinoid profile.
# 2022: Most Unique Cannabinoid Profile	Emerald Spirit Botanicals – Pink Boost Goddess



# TODO: Build an ordered probit model to back-cast 2020 winners.


# Most Innovative Product – Consumable	Compound Genetics x Node Labs x The Original Resinator x Industry Processing Solutions – Perzimmon #2 Flower


# TODO: Is there any interesting analysis that can be done with the images?



# === Environment analysis ===

# # Compare indoor vs. outdoor
# indoor = results[results['product_subtype'] == 'Indoor']
# outdoor = results[results['product_subtype'] == 'Full Sun']
# indoor_outdoor_comparison = indoor.describe().join(outdoor.describe(), lsuffix='_indoor', rsuffix='_outdoor')

# # Visualize indoor vs. outdoor cannabis.
# plt.ylabel('Count')
# plt.xlabel('Percent')
# plt.title('Terpene Concentrations in Indoor vs. Full Sun Cannabis in CA')
# indoor['total_terpenes'].hist(bins=40)
# outdoor['total_terpenes'].hist(bins=40)
# plt.legend(['Indoor', 'Outdoor'])
# plt.xlim(0)
# plt.tight_layout()
# # plt.savefig(f'figures/indoor-outdoor-thc.png', bbox_inches='tight', dpi=300)
# plt.show()


# === Chemical Analysis ===

# # Look at total cannabinoids.
# key = 'total_cannabinoids'
# results[key] = pd.to_numeric(results[key], errors='ignore')
# sample = results.dropna(subset=[key])
# sample[key].hist(bins=1000)
# plt.xlim(0, 100)
# plt.show()

# # Look at total terpenes.
# key = 'total_terpenes'
# results[key] = pd.to_numeric(results[key], errors='coerce')
# sample = results.dropna(subset=[key])
# sample[key].hist(bins=40)
# plt.show()

# # Look at moisture content.
# key = 'moisture_content'
# results[key] = pd.to_numeric(results[key], errors='coerce')
# sample = results.dropna(subset=[key])
# sample[key].hist(bins=40)
# plt.show()

# # Look at water activity.
# key = 'water_activity'
# results[key] = pd.to_numeric(results[key], errors='coerce')
# sample = results.dropna(subset=[key])
# sample[key].hist(bins=40)
# plt.show()

# # Look at moisture-adjusted total cannabinoids in flower.
# types = ['Flower', 'Flower, Inhalable']
# sample = results.loc[results['product_type'].isin(types)]
# sample = sample.loc[~sample['total_cannabinoids'].isna()]
# sample = sample.loc[~sample['moisture_content'].isna()]
# sample['wet_total_cannabinoids'] = sample['total_cannabinoids'] / (1 + sample['moisture_content'] * 0.01)
# sample['wet_total_cannabinoids'].hist(bins=1000)
# plt.xlim(0, 100)
# plt.show()

# # Calculate the mean wet total cannabinoids in flower in CA.
# valid = sample['wet_total_cannabinoids'].loc[sample['wet_total_cannabinoids'] < 100]
# valid.mean()


# === Product subtype analysis ===

# # Look at terpene concentrations in concentrate products:
# concentrate_types = [
#     'Badder',
#     'Diamond',
#     'Diamond Infused',
#     'Crushed Diamond',
#     'Liquid Diamonds',
#     'Distillate',
#     'Resin',
#     'Live Resin',
#     'Live Resin Infused',
#     'Live Resin Sauce',
#     'Sauce',
#     'Live Rosin',
#     'Unpressed Hash Green',
#     # 'Fresh Press',
#     # 'Hash Infused',
#     # 'Rosin Infused',
# ]

# # Creating a box plot of total terpenes in concentrates.
# concentrate_data = results.loc[results['product_subtype'].isin(concentrate_types)]
# filtered_data = concentrate_data.loc[~concentrate_data['total_terpenes'].isna()]
# grouped_data = filtered_data.groupby('product_subtype')['total_terpenes'].apply(list)
# mean_terpenes = {subtype: sum(values) / len(values) for subtype, values in grouped_data.items()}
# sorted_subtypes = sorted(mean_terpenes, key=mean_terpenes.get)
# data = [grouped_data[subtype] for subtype in sorted_subtypes]
# labels = sorted_subtypes
# plt.figure(figsize=(15, 11))
# plt.boxplot(data, vert=False, labels=labels)
# plt.xlabel('Total Terpenes (%)', labelpad=20)
# plt.title('Terpene Concentrations in Concentrates in CA', pad=20)
# plt.grid(axis='x', linestyle='--', alpha=0.7)
# plt.tight_layout()
# plt.show()


# === Price analysis ===

# # Clean the price data.
# results['discount_price'] = results['discount_price'].str.replace('$', '').astype(float)
# price_data = results.loc[results['discount_price'] > 0]
# price_data = price_data.loc[~price_data['amount'].isna()]
# price_data['price_per_gram'] = price_data['discount_price'] / price_data['amount']

# # See if THC, terpenes, etc. are correlated with price.
# types = ['Flower', 'Flower, Inhalable']
# # types = [
# #     'Infused Flower/Pre-Roll, Product Inhalable',
# #     'Pre-roll',
# #     'Plant (Preroll)',
# #     'Infused Pre-roll',
# # ]
# # types = [
# #     'Concentrates & Extracts (Other)',
# #     'Concentrates & Extracts (Distillate)',
# #     'Extract',
# #     'Concentrates & Extracts (Diamonds)',
# #     'Concentrates & Extracts (Live Resin)',
# #     'Concentrates & Extracts (Live Rosin)',
# #     'Concentrates & Extracts (Vape)',
# #     'Concentrate, Product Inhalable',
# #     'Distillate',
# # ]
# type_price_data = price_data.loc[price_data['product_type'].isin(types)]
# type_price_data = type_price_data.loc[type_price_data['total_cannabinoids'] < 100]

# # Visualize the relationship between cannabinoids and price.
# plt.figure(figsize=(10, 6))
# sns.regplot(
#     data=type_price_data,
#     x='total_cannabinoids',
#     y='price_per_gram',
# )
# plt.xlabel('Total Cannabinoids')
# plt.ylabel('Price per gram ($)')
# plt.title('Price per gram of flower to total cannabinoids in CA')
# plt.grid(True)
# plt.show()

# # Visualize the relationship between terpenes and price.
# plt.figure(figsize=(10, 6))
# sns.regplot(
#     data=type_price_data,
#     x='total_terpenes',
#     y='price_per_gram',
# )
# plt.xlabel('Total Terpenes')
# plt.ylabel('Price per gram ($)')
# plt.title('Price per gram of flower to total terpenes in CA')
# plt.grid(True)
# plt.show()

# # Price vs. Chemical Properties Regression
# X = type_price_data[['total_cannabinoids', 'total_terpenes']]
# y = type_price_data['price_per_gram']
# X_clean = X.dropna()
# y_clean = y.reindex(X_clean.index)
# X_clean = sm.add_constant(X_clean)
# model = sm.OLS(y_clean, X_clean)
# regression = model.fit()
# print(regression.summary())

# # Look at the average discount.
# results['discount'].hist(bins=40)
# plt.vlines(results['discount'].mean(), 0, 60, color='darkorange')
# plt.show()

# TODO: Look at the average price per product type.



# === Lineage analysis ===

# # Look at the most common parents.
# lineage_data = results['lineage'].dropna()
# unique_parents = pd.Series([parent for lineage in lineage_data for parent in lineage.split(' x ')]).value_counts()
# filtered_strains = unique_parents[unique_parents >= 2]
# plt.figure(figsize=(10, 8))
# filtered_strains.sort_values()[-20:].plot(kind='barh')
# plt.xlabel('Number of Descendants')
# plt.ylabel('')
# plt.title('Number of Descendants by Strain')
# plt.show()


# === Timeseries analysis ===

# # Format the date.
# results['date'] = pd.to_datetime(results['date_tested'])

# TODO: Look at total THC levels over time.


# TODO: Look at total terpene levels over time.



# === Geographic analysis ===

# Note: Mostly missing.

# TODO: Geocode `producer_address`.


# TODO: Compare different regions of CA.
