"""
Analyze Cannabis Lab Results | Massachusetts
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2024
Updated: 3/13/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# External imports:
from matplotlib import ticker
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import matplotlib.dates as mdates
from matplotlib import cm
import numpy as np
import pandas as pd
import seaborn as sns
from adjustText import adjust_text


# === Setup ===

# Setup plotting style.
plt.style.use('fivethirtyeight')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.family': 'Times New Roman',
    'font.size': 24,
})

assets_dir = './presentation/images/figures'


# === Get the data ===

# Read MA lab results.
datafiles = [
    r"D:\data\massachusetts\TestingTHC-THCA-YeastMold-Apr-Dec2021-FINAL.csv",
    r"D:\data\massachusetts\TestingTHC-THCA-YeastMold-2023-Jan-June-FINAL.csv",
    r"D:\data\massachusetts\TestingTHC-THCA-YeastMold-2023-Jul-Sep-FINAL.csv",
]
ma_results = []
for datafile in datafiles:
    ma_results.append(pd.read_csv(datafile))
ma_results = pd.concat(ma_results)

# Coalesce similarly named columns.
ma_results['lab'] = ma_results['TestingLabId'].combine_first(ma_results['TestingLab'])
ma_results['strain_name'] = ma_results['StrainName'].combine_first(ma_results['Strain'])
ma_results = ma_results.drop(columns=[
    'TestingLabId',
    'TestingLab',
    'StrainName',
    'Strain',
])

# Rename certain columns.
ma_results = ma_results.rename(columns={
    'ProductCategory': 'product_type',
    'PackageLabel': 'label',
    'TestType': 'test_type',
    'TestResult': 'test_result',
    'TestPerformedDate': 'date_tested',
})

# Add a date column.
ma_results['date'] = pd.to_datetime(ma_results['date_tested'])
ma_results['month_year'] = ma_results['date'].dt.to_period('M')

# Creating a pivot table
pivot_df = ma_results.pivot_table(
    index=['label', 'date_tested', 'lab'],
    columns='test_type',
    values='test_result',
    aggfunc='first',
).reset_index()
pivot_df.columns.name = None  
pivot_df.rename({
    'THC (%) Raw Plant Material': 'delta_9_thc',
    'THCA (%) Raw Plant Material': 'thca',
    'Total THC (%) Raw Plant Material': 'total_thc',
    'Total Yeast and Mold (CFU/g) Raw Plant Material': 'yeast_and_mold'
}, axis=1, inplace=True)
pivot_df['date'] = pd.to_datetime(pivot_df['date_tested'])
pivot_df['month_year'] = pivot_df['date'].dt.to_period('M')
print(len(pivot_df))

print(pivot_df.head())


# === Visualize the number of tests per month ===

# Count the number of tests per month.
monthly_tests = pivot_df.groupby('month_year').size().reset_index(name='n_tests')

# Plot the number of tests per month.
fig, ax = plt.subplots()
monthly_tests.plot(x='month_year', y='n_tests', kind='bar', ax=ax, color='k')
ax.set_title('Number of MA Cannabis Tests per Month')
ax.set_xlabel('Month')
ax.set_ylabel('Number of Tests')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.show()

# Calculate the number of detects.
sample = pivot_df.loc[pivot_df['yeast_and_mold'].notnull()]
detects = sample.loc[sample['yeast_and_mold'] > 0]
detects.sort_values('yeast_and_mold', ascending=False, inplace=True)

# Calculate the maximum yeast and mold detection.
print('Maximum yeast and mold detection:', detects['yeast_and_mold'].max())

# Calculate the most frequent value.
print('Most frequent yeast and mold detection:', detects['yeast_and_mold'].mode())

# Histogram
filtered_df = pivot_df.dropna(subset=['yeast_and_mold'])
filtered_df.loc[
    (filtered_df['yeast_and_mold'] <= 15_000) &
    (filtered_df['yeast_and_mold'] > 100)
]['yeast_and_mold'].hist(
    bins=100,
    alpha=0.75,
    density=True,
)
plt.axvline(10_000, color='r', linestyle='dashed', linewidth=1)
plt.xlabel('Yeast and Mold Counts')
plt.ylabel('Frequency')
plt.title('Histogram of Yeast and Mold Detections below 10,000')
plt.legend(['State Limit (10,000)', 'Yeast and Mold Counts'])
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.xlim(0, 15_000)
plt.show()

# Histogram
filtered_df = pivot_df.dropna(subset=['yeast_and_mold'])
filtered_df.loc[filtered_df['yeast_and_mold'] > 10_000]['yeast_and_mold'].hist(
    bins=1000,
    alpha=0.75,
    density=True,
)
plt.axvline(10_000, color='r', linestyle='dashed', linewidth=1)
plt.xlabel('Yeast and Mold Counts')
plt.ylabel('Frequency')
plt.title('Histogram of Yeast and Mold Detections above 10,000')
plt.legend(['State Limit (10,000)', 'Yeast and Mold Counts'])
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.xlim(0, 500_000)
plt.show()


# === Failure Analysis ===

# Identify failures.
fails = filtered_df.loc[filtered_df['yeast_and_mold'] > 10_000]
print(fails[['label', 'date_tested', 'lab', 'yeast_and_mold']])


# FIXME: Visualize failure rates.
pivot_df['fail'] = pivot_df['yeast_and_mold'] > 10_000
fail_counts = pivot_df['fail'].value_counts()
fail_percentages = (fail_counts / fail_counts.sum()) * 100
colors = cm.coolwarm(pivot_df['fail'].value_counts(normalize=True))
ax = pivot_df['fail'].value_counts().plot(
    kind='bar',
    color=[colors[-1], colors[0]]
)
ax.get_yaxis().set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.xticks(
    ticks=[0, 1],
    labels=['Below 10,000 CFU/g', 'Above 10,000 CFU/g'],
    rotation=0,
)
for i, (count, percentage) in enumerate(zip(fail_counts, fail_percentages)):
    ax.text(i, count, f'{percentage:.1f}%', color='black', ha='center', va='bottom')
plt.ylabel('Number of Samples')
plt.title('Total Yeast and Mold Detections in MA in 2021', pad=24)
plt.xlabel('Pass/Fail')
plt.savefig(f'presentation/images/figures/ma-yeast-and-mold-failure-rate-2021.png', bbox_inches='tight', dpi=300)
plt.show()
failure_rate = len(fails) / len(pivot_df)
print('Failure rate: %0.2f%%' % (failure_rate * 100))

# FIXME: Visualize failure rate by lab.
samples_tested_by_lab = pivot_df['lab'].value_counts()
failures_by_lab = pivot_df.groupby('lab')['fail'].sum()
failure_rate_by_lab = pivot_df.groupby('lab')['fail'].mean()
failure_rate_by_lab = failure_rate_by_lab.sort_values()
plt.figure(figsize=(18, 16/1.618))
ax = sns.barplot(
    x=failure_rate_by_lab.index,
    y=failure_rate_by_lab.values * 100,
    palette='coolwarm'
)
for i, p in enumerate(ax.patches):
    lab = failure_rate_by_lab.index[i]
    ax.annotate(
        f'{failures_by_lab[lab]:,.0f} / {samples_tested_by_lab[lab]:,.0f}',
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center',
        va='bottom',
        fontsize=24,
        color='black',
        xytext=(0, 3),
        textcoords='offset points'
    )
plt.ylabel('Failure Rate (%)', fontsize=28, labelpad=10)
plt.xlabel('')
plt.title('Total Yeast and Mold Failure Rate by Lab in MA in 2021', fontsize=34)
plt.xticks(rotation=45)
plt.figtext(
    0,
    -0.075,
    'Note: Statistics are calculated from 31,613 package lab tests for total yeast and mold performed between 4/1/2021 and 12/31/2021 in Massachusetts. The number of tests above the state limit, 10,000 CFU/g, and the total number of tests are shown for each lab.',
    ha='left',
    fontsize=24,
    wrap=True
)
plt.tight_layout()
plt.savefig(f'presentation/images/figures/ma-yeast-and-mold-failure-rate-by-lab-2021.png', bbox_inches='tight', dpi=300)
plt.show()


# === Method Analysis ===

def determine_method(x):
    """Determine the method of testing based on the value.
    If the value is divisible by 10 and has no decimal component, it's `plating`.
    Otherwise, it's considered `qPCR`.
    """
    if pd.isna(x):
        return None
    # Check if the number is a whole number and divisible by 10
    if x % 10 == 0 and x == int(x):
        return 'plating'
    else:
        return 'qPCR'


# Determine the method of testing.
pivot_df['method'] = pivot_df['yeast_and_mold'].apply(determine_method)
test_count_per_method = pivot_df['method'].value_counts()

# Example analysis: Average yeast_and_mold results per method
average_results_per_method = pivot_df.groupby('method')['yeast_and_mold'].mean()

print(test_count_per_method)
print(average_results_per_method)

# Histogram
filtered_df = pivot_df.dropna(subset=['yeast_and_mold'])
subsample = filtered_df.loc[
    (filtered_df['yeast_and_mold'] <= 15_000) &
    (filtered_df['yeast_and_mold'] > 100)
]
plating_values = subsample.loc[subsample['method'] == 'plating']['yeast_and_mold']
qpcr_values = subsample.loc[subsample['method'] == 'qPCR']['yeast_and_mold']
plating_values.hist(
    bins=100,
    alpha=0.75,
    density=True,
    label='Plating',
)
qpcr_values.hist(
    bins=100,
    alpha=0.75,
    density=True,
    label='qPCR',
)
plt.axvline(10_000, color='r', linestyle='dashed', linewidth=1, label='State Limit (10,000)')
plt.xlabel('Yeast and Mold Counts')
plt.ylabel('Frequency')
plt.title('Histogram of Yeast and Mold Detections below 10,000')
# plt.legend(['State Limit (10,000)', 'Yeast and Mold Counts'])
plt.legend()
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.xlim(0, 15_000)
plt.show()

# Histogram
filtered_df = pivot_df.dropna(subset=['yeast_and_mold'])
subsample = filtered_df.loc[filtered_df['yeast_and_mold'] > 10_000]
plating_values = subsample.loc[subsample['method'] == 'plating']['yeast_and_mold']
qpcr_values = subsample.loc[subsample['method'] == 'qPCR']['yeast_and_mold']
plating_values.hist(
    bins=1000,
    alpha=0.75,
    density=True,
    label='Plating',
)
qpcr_values.loc [
    qpcr_values != 200001
].hist(
    bins=1000,
    alpha=0.75,
    density=True,
    label='qPCR',
)
plt.axvline(10_000, color='r', linestyle='dashed', linewidth=1, label='State Limit (10,000)')
plt.xlabel('Yeast and Mold Counts')
plt.ylabel('Frequency')
plt.title('Histogram of Yeast and Mold Detections above 10,000')
plt.legend()
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.xlim(0, 500_000)
plt.show()


# === Benford's Law Analysis ===


# Function to extract the first significant digit
def first_significant_digit(number):
    return int(str(number).split('.')[0][0])

# 1. Extracting first significant digit from yeast_and_mold values
subsample = pivot_df.dropna(subset=['yeast_and_mold'])
subsample = subsample.loc[
    (subsample['yeast_and_mold'] <= 200_000) &
    (subsample['yeast_and_mold'] > 0)
]
subsample['first_digit'] = subsample['yeast_and_mold'].dropna().apply(first_significant_digit)

# 2. Generate Benford's Law distribution for the first significant digit
digits = range(1, 10)
benford = [np.log10(1 + 1/d) * 100 for d in digits]

# 3. Generate a random sample and extract first significant digit
np.random.seed(420)
random_sample = np.random.uniform(
    0,
    100000,
    size=len(subsample['yeast_and_mold'].dropna()),
)
random_first_digit = [first_significant_digit(num) for num in random_sample]

# Frequency counts of the first digits
actual_counts = subsample['first_digit'].value_counts(normalize=True).sort_index() * 100
random_counts = pd.Series(random_first_digit).value_counts(normalize=True).sort_index() * 100

# 4. Plot the distributions
plt.figure(figsize=(10, 6))
plt.plot(digits, benford, 'o-', label='Benford\'s Law')
plt.plot(actual_counts.index, actual_counts, 's-', label='Yeast and Mold')
plt.plot(random_counts.index, random_counts, 'd-', label='Random Sample')
plt.xticks(digits)
plt.xlabel('First Significant Digit')
plt.ylabel('Percentage')
plt.title('First Significant Digit Distribution Comparison')
plt.legend()
plt.grid(True)
plt.show()

# # 4. Plot the distributions
qpcr = subsample.loc[subsample['method'] == 'qPCR']
plating = subsample.loc[subsample['method'] == 'plating']
plating_counts = plating['first_digit'].value_counts(normalize=True).sort_index() * 100
qpcr_counts = qpcr['first_digit'].value_counts(normalize=True).sort_index() * 100
plt.figure(figsize=(10, 6))
plt.plot(digits, benford, 'o-', label='Benford\'s Law')
plt.plot(plating_counts.index, plating_counts, 's-', label='Plating')
plt.plot(qpcr_counts.index, qpcr_counts, 'd-', label='qPCR')
plt.xticks(digits)
plt.xlabel('First Significant Digit')
plt.ylabel('Percentage')
plt.title('First Significant Digit Distribution Comparison')
plt.legend()
plt.grid(True)
plt.show()


from scipy.stats import chisquare

# Convert percentages back to counts
total_qpcr = len(qpcr.dropna(subset=['first_digit']))
total_plating = len(plating.dropna(subset=['first_digit']))

qpcr_observed_counts = (qpcr_counts / 100) * total_qpcr
plating_observed_counts = (plating_counts / 100) * total_plating

# Benford's expected percentages for the first digit
benford_percentages = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

# Convert Benford's percentages to expected counts for each method
benford_expected_qpcr = benford_percentages * total_qpcr
benford_expected_plating = benford_percentages * total_plating

# Perform Chi-squared test for qPCR
chi2_stat_qpcr, p_val_qpcr = chisquare(f_obs=qpcr_observed_counts, f_exp=benford_expected_qpcr)

# Perform Chi-squared test for Plating
chi2_stat_plating, p_val_plating = chisquare(f_obs=plating_observed_counts, f_exp=benford_expected_plating)

print(f"qPCR Chi-squared Stat: {chi2_stat_qpcr}, p-value: {p_val_qpcr}")
print(f"Plating Chi-squared Stat: {chi2_stat_plating}, p-value: {p_val_plating}")

# Comparing the Chi-squared statistics and p-values
# A lower p-value indicates a higher statistical significance of deviation from Benford's Law
lower_deviation = 'Plating' if p_val_qpcr < p_val_plating else 'qPCR'
print(f"The method with lower deviation from Benford's Law is {lower_deviation}")


# === Summary Statistics ===

# TODO: Calculate the number of producers in each state dataset.


# TODO: Calculate the number of tests per producer per week / month / year in each state.








def plot_metric_over_time(metric, metric_name, y_label, color='skyblue'):
    """
    General function to plot any calculated metric over time.
    """
    plt.figure(figsize=(15, 8))
    metric.plot(color=color)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.title(f'{metric_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Get a sample.
sample = pivot_df.copy()
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')
sample['date_tested'] = pd.to_datetime(sample['date_tested'])
sample = sample.loc[sample['date_tested'] >= pd.to_datetime('2023-01-01')]

# Visualize the number of tests over time.
sample['count'] = 1
num_tests = sample.resample('M', on='date_tested')['count'].sum()
plot_metric_over_time(num_tests, 'Number of Tests', 'Number of Tests')

# Visualize the cost of tests over time (assuming $20 per test).
cost_of_tests = num_tests * 20
plot_metric_over_time(cost_of_tests, 'Cost of Tests', 'Cost ($)', 'green')

# Visualize the cost of failures over time (assuming $35,000 per failure).
sample['failure'] = sample['yeast_and_mold'] > 10_000
failures_per_month = sample.resample('M', on='date_tested')['failure'].sum()
cost_of_failures = failures_per_month * 35_000
plot_metric_over_time(cost_of_failures, 'Cost of Failures', 'Cost ($)', 'red')

# Estimate the cost of testing in 2023.
total_cost_of_tests = cost_of_tests.sum()
avg_monthly_cost = cost_of_tests.mean()
estimate_2023 = total_cost_of_tests + (avg_monthly_cost * 3)
print(f'Estimated cost of testing in 2023: ${estimate_2023 / 1_000_000:,.0f} million')

# Estimate the cost of total yeast and mold failures in 2023.
total_cost_of_failures = cost_of_failures.sum()
avg_monthly_cost = cost_of_failures.mean()
estimate_2023 = total_cost_of_failures + (avg_monthly_cost * 3)
print(f'Estimated cost of total yeast and mold failures in 2023: ${estimate_2023 / 1_000_000:,.0f} million')


# === Timeseries Analysis ===

def plot_timeseries(
        df,
        title,
        x='date_tested',
        y='total_thc',
        y_label='Total THC (%)',
        outfile=None,
        y_min=0,
        y_max=15_000,
        ma=30,
        dot_color='royalblue',
        line_color='navy',
    ):
    """
    Plot the timeseries data with dots for actual values and separate trend lines 
    for periods before and after the compliance date.
    """
    plt.figure(figsize=(15, 8))
    df[x] = pd.to_datetime(df[x])
    
    # Plot actual THC values as dots
    sns.scatterplot(
        data=df,
        x=x,
        y=y,
        color=dot_color,
        s=75,
        alpha=0.6,
    )

    # Plot weekly moving average.
    df[f'{ma}_day_avg'] = df[y].rolling(
        window=ma,
        min_periods=1
    ).mean()
    sns.lineplot(
        data=df,
        x=x,
        y=f'{ma}_day_avg',
        color=line_color,
        label=f'{ma}-day Moving Average'
    )

    # Calculate positions for the desired number of ticks (e.g., 5 ticks)
    selected_dates = ['2023-01-01', '2023-04-01', '2023-07-01', '2023-10-01']  # Example dates
    plt.xticks(ticks=pd.to_datetime(selected_dates), labels=selected_dates)

    # Add title and labels
    plt.title(title, pad=20)
    plt.xlabel('Date')
    plt.ylabel(y_label)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.ylim(y_min, y_max)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    if outfile is None:
        outfile = f'{assets_dir}/{y.replace("_", "-")}-timeseries.pdf'
    plt.savefig(outfile, dpi=300, bbox_inches='tight', transparent=True)
    plt.show()


# Get the data.
sample = pivot_df.copy()
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')
sample['year'] = pd.to_datetime(sample['date_tested']).dt.year
sample = sample.loc[sample['year'] == 2023]

# Plot trend lines and timeseries
plot_timeseries(
    sample.copy().loc[
        (sample['yeast_and_mold'] > 100) &
        (sample['yeast_and_mold'] < 10_000)
    ],
    title='Yeast and Mold Values Over Time in MA',
    x='date_tested',
    y='yeast_and_mold',
    y_label='Yeast and Mold (CFU/g)',
    outfile=None,
    y_min=100,
    y_max=10_000,
    ma=30,
)

# Plot trend lines and timeseries
plot_timeseries(
    sample.copy().loc[
        (sample['yeast_and_mold'] > 10_000) &
        (sample['yeast_and_mold'] < 500_000)
    ],
    title='Yeast and Mold Values Over Time in MA',
    x='date_tested',
    y='yeast_and_mold',
    y_label='Yeast and Mold (CFU/g)',
    outfile=None,
    y_min=10_000,
    y_max=500_000,
    ma=30,
    dot_color='firebrick',
    line_color='darkred',
)

# Plot trend lines and timeseries by lab.
labs = list(pivot_df['lab'].unique())
lab_colors = sns.color_palette('tab10', n_colors=len(labs))
for i, lab in enumerate(labs):
    y_min, y_max = 100, 500_000
    lab_sample = sample.copy().loc[
        (sample['yeast_and_mold'] > y_min) &
        (sample['yeast_and_mold'] < y_max) &
        (sample['lab'] == lab)
    ]
    if len(lab_sample) < 100:
        continue
    print(len(lab_sample))
    plot_timeseries(
        lab_sample,
        title='Yeast and Mold Values Over Time in MA',
        x='date_tested',
        y='yeast_and_mold',
        y_label='Yeast and Mold (CFU/g)',
        outfile=None,
        y_min=y_min,
        y_max=y_max,
        ma=30,
        dot_color=lab_colors[i],
        line_color=lab_colors[i],
    )


# === Lab Failure Analysis ===

def calculate_failure_rate(df, threshold=10_000, period='W'):
    """
    Calculate the failure rate based on the 'yeast_and_mold' threshold.
    """
    df['failure'] = df['yeast_and_mold'] >= threshold
    df['date_tested'] = pd.to_datetime(df['date_tested'])
    return df.groupby(df['date_tested'].dt.to_period(period))['failure'].mean() * 100


def plot_failure_rates(df, color, threshold=10_000, period='W'):
    """
    Plot the failure rates over time with a moving average.
    """
    plt.figure(figsize=(15, 8))
    failure_rate = calculate_failure_rate(df, threshold, period=period)
    failure_rate.index = failure_rate.index.to_timestamp()
    
    # Plot the failure rates
    plt.plot(
        failure_rate.index,
        failure_rate,
        # label=f'Lab {lab}',
        color=color
    )

    # Calculate and plot horizontal lines for the mean, 25th percentile, and 75th percentile
    mean_rate = failure_rate.mean()
    percentile_25 = failure_rate.quantile(0.25)
    percentile_75 = failure_rate.quantile(0.75)

    plt.axhline(y=mean_rate, color='green', linestyle='--', label='Mean')
    plt.axhline(y=percentile_25, color='blue', linestyle=':', label='25th Percentile')
    plt.axhline(y=percentile_75, color='red', linestyle='-.', label='75th Percentile')
    
    # Add title and labels.
    plt.title('Failure Rates Over Time by Lab')
    plt.xlabel('Date')
    plt.ylabel('Failure Rate (%)')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Get the data.
sample = pivot_df.copy()
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')
sample['year'] = pd.to_datetime(sample['date_tested']).dt.year
sample = sample.loc[sample['year'] == 2023]

# Assuming 'pivot_df' and 'sample' are defined and prepared as per your previous code
labs = list(pivot_df['lab'].unique())
lab_colors = sns.color_palette('tab10', n_colors=len(labs))
for i, lab in enumerate(labs):
    lab_sample = sample[(sample['lab'] == lab) & (sample['yeast_and_mold'].notna())]
    if len(lab_sample) >= 1_000:
        print('N = ', len(lab_sample))
        plot_failure_rates(lab_sample.copy(), lab_colors[i])


# === Overall failure rate analysis ===

def plot_failure_rates(df, color, threshold=10_000, period='W'):
    """
    Plot the failure rates over time, segmenting the data to avoid drawing lines across gaps.
    """
    plt.figure(figsize=(15, 8))

    # Define your data periods explicitly
    periods = [
        (pd.to_datetime('2021-04-01'), pd.to_datetime('2021-12-31')),
        (pd.to_datetime('2023-01-01'), pd.to_datetime('2023-09-30')),
    ]

    for start_date, end_date in periods:
        # Filter the dataframe for the current period
        period_df = df[(df['date_tested'] >= start_date) & (df['date_tested'] <= end_date)]
        failure_rate = calculate_failure_rate(period_df, threshold, period=period)
        failure_rate.index = failure_rate.index.to_timestamp()

        # Plot the failure rates for the current period
        plt.plot(failure_rate.index, failure_rate, color=color)

    # Calculate and plot horizontal lines for the mean, 25th percentile, and 75th percentile
    mean_rate = failure_rate.mean()
    percentile_25 = failure_rate.quantile(0.25)
    percentile_75 = failure_rate.quantile(0.75)
    plt.axhline(y=mean_rate, color='green', linestyle='--', label='Mean')
    plt.axhline(y=percentile_25, color='blue', linestyle=':', label='25th Percentile')
    plt.axhline(y=percentile_75, color='red', linestyle='-.', label='75th Percentile')

    # Add title and labels.
    plt.title('Failure Rates Over Time')
    plt.xlabel('Date')
    plt.ylabel('Failure Rate (%)')
    plt.tight_layout()
    plt.show()

# Assuming 'pivot_df' is your DataFrame with 'date_tested' and 'yeast_and_mold' columns
sample = pivot_df.copy()
sample['date_tested'] = pd.to_datetime(sample['date_tested'])
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')

# Plot overall failure rate.
plot_failure_rates(
    sample.loc[
        pd.to_datetime(sample['date_tested']) >= pd.to_datetime('2021-07-01')
    ],
    'k'
)


# === Detection Rate Analysis ===

def calculate_detection_rate(df, threshold=100, period='W'):
    """
    Calculate the detection rate based on the 'yeast_and_mold' threshold.
    """
    df['detected'] = df['yeast_and_mold'] > threshold
    df['date_tested'] = pd.to_datetime(df['date_tested'])
    return df.groupby(df['date_tested'].dt.to_period(period))['detected'].mean() * 100


def plot_detection_rates(df, color, threshold=100, period='W'):
    """
    Plot the detection rates over time, segmenting the data to avoid drawing lines across gaps.
    """
    plt.figure(figsize=(15, 8))

    periods = [
        (pd.to_datetime('2021-04-01'), pd.to_datetime('2021-12-31')),
        (pd.to_datetime('2023-01-01'), pd.to_datetime('2023-09-30')),
    ]

    for start_date, end_date in periods:
        period_df = df[(df['date_tested'] >= start_date) & (df['date_tested'] <= end_date)]
        detection_rate = calculate_detection_rate(period_df, threshold, period=period)
        detection_rate.index = detection_rate.index.to_timestamp()

        plt.plot(detection_rate.index, detection_rate, color=color)

    # Calculate and add aesthetic lines for mean, 25th, and 75th percentiles
    overall_rate = calculate_detection_rate(df, threshold, period)
    mean_rate = overall_rate.mean()
    percentile_25 = overall_rate.quantile(0.25)
    percentile_75 = overall_rate.quantile(0.75)
    plt.axhline(y=mean_rate, color='green', linestyle='--', label='Mean')
    plt.axhline(y=percentile_25, color='blue', linestyle=':', label='25th Percentile')
    plt.axhline(y=percentile_75, color='red', linestyle='-.', label='75th Percentile')

    plt.title('Detection Rates Over Time')
    plt.xlabel('Date')
    plt.ylabel('Detection Rate (%)')
    plt.legend()
    plt.tight_layout()
    plt.show()


# Visualize detection rates over time.
sample = pivot_df.copy()
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')
sample['date_tested'] = pd.to_datetime(sample['date_tested'])
sample = sample.loc[sample['date_tested'] >= pd.to_datetime('2021-07-01')]
plot_detection_rates(sample.copy(), 'k')


def plot_detection_rates(df, color, lab_name, threshold=100, period='W'):
    """
    Plot the detection rates over time.
    """
    plt.figure(figsize=(15, 8))
    detection_rate = calculate_detection_rate(df, threshold, period=period)
    detection_rate.index = detection_rate.index.to_timestamp()
    
    # Plot the detection rates
    plt.plot(detection_rate.index, detection_rate, label=f'Lab {lab_name}', color=color)

    # Calculate and plot horizontal lines for the mean, 25th percentile, and 75th percentile
    mean_rate = detection_rate.mean()
    percentile_25 = detection_rate.quantile(0.25)
    percentile_75 = detection_rate.quantile(0.75)

    plt.axhline(y=mean_rate, color='green', linestyle='--', label='Mean')
    plt.axhline(y=percentile_25, color='blue', linestyle=':', label='25th Percentile')
    plt.axhline(y=percentile_75, color='red', linestyle='-.', label='75th Percentile')
    
    # Add title and labels
    plt.title(f'Detection Rates Over Time: {lab_name}')
    plt.xlabel('Date')
    plt.ylabel('Detection Rate (%)')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Visualize detection rate by lab.
sample['date_tested'] = pd.to_datetime(sample['date_tested'])
sample['yeast_and_mold'] = pd.to_numeric(sample['yeast_and_mold'], errors='coerce')
labs = list(sample['lab'].unique())
lab_colors = sns.color_palette('tab10', n_colors=len(labs))
for i, lab in enumerate(labs):
    lab_sample = sample[(sample['lab'] == lab) & (sample['yeast_and_mold'].notna())]
    if len(lab_sample) >= 100:
        plot_detection_rates(lab_sample, lab_colors[i], lab)

