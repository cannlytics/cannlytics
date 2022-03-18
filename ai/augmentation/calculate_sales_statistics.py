"""
Calculate Sale Statistics | Cannabis Data Science Meetup Group
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 2/10/2022
Updated: 2/18/2022
License: MIT License <https://opensource.org/licenses/MIT>

Data sources:

    - WA State Traceability Data January 2018 - November 2021
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=1
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=2

Data Guide:

    - Washington State Leaf Data Systems Guide
    https://lcb.wa.gov/sites/default/files/publications/Marijuana/traceability/WALeafDataSystems_UserManual_v1.37.5_AddendumC_LicenseeUser.pdf

TODO:

    - Refactor the script into reusable functions.

"""
# Standard imports.
from datetime import datetime
import gc
import random

# External imports.
import pandas as pd

# Internal imports.
from utils import format_millions


# Specify where the data lives.
DATA_DIR = 'D:\\leaf-data'
DATA_FILE = f'{DATA_DIR}/samples/random-sales-items-2022-02-18.csv'


#--------------------------------------------------------------------------
# Sample the data.
# Approximate runtime:
#--------------------------------------------------------------------------

# Specify the sales items metadata.
sale_items_datasets = [
    {'file_name': f'{DATA_DIR}/SaleItems_0.csv', 'rows': 90_000_001},
    {'file_name': f'{DATA_DIR}/SaleItems_1.csv', 'rows': 90_000_001},
    {'file_name': f'{DATA_DIR}/SaleItems_2.csv', 'rows': 90_000_001},
    {'file_name': f'{DATA_DIR}/SaleItems_3.csv', 'rows': 76_844_111},
]
sales_items_fields = {
    'price_total': 'float',
    'sale_id': 'string',
    'mme_id': 'string',
    'inventory_id': 'string',
    'qty': 'float',
    'uom': 'string',
    'name': 'string',
}
sales_items_date_fields = [
    'created_at',
]

# Specify the time range to calculate statistics.
daily_total_sales = {}
time_range = pd.date_range(start='2021-02-01', end='2021-11-30')

# Read a sample of each chunk of each sales items datafile.
# Optional: Determine the optimal sample size.
start = datetime.now()
random.seed(420)
percent = 0.001
samples = []
for dataset in sale_items_datasets:

    # Read a random portion of each chunk in the dataset.
    number_of_rows = dataset['rows']
    file_name = dataset['file_name']
    sample = pd.read_csv(
        file_name,
        sep='\t',
        encoding='utf-16',
        usecols=list(sales_items_fields.keys()) + sales_items_date_fields,
        dtype=sales_items_fields,
        parse_dates=sales_items_date_fields,
        skiprows=lambda i: i > 0 and random.random() > percent
    )
    sample.rename(
        columns={'name': 'product_name'},
        inplace=True,
    )
    samples.append(sample)
    print('Sampled:', len(sample))

# Combine all samples.
data = pd.concat(samples)

# Save the random sample for future use.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to sample the data:', print(end - start))


#--------------------------------------------------------------------------
# Augment the data with sales data.
# Approximate runtime:
#--------------------------------------------------------------------------

# Read in the random sample.
start = datetime.now()
data = pd.read_csv(DATA_FILE)

# Add sales type from sales data.
chunk_size = 10_000_001
sales_datasets = [
    {'file_name': f'{DATA_DIR}/Sales_0.csv', 'rows': 100_000_001},
    {'file_name': f'{DATA_DIR}/Sales_1.csv', 'rows': 100_000_001},
    {'file_name': f'{DATA_DIR}/Sales_2.csv', 'rows': 28_675_356},
]
sales_fields = {
    'global_id': 'string',
    'type': 'string', # wholesale or retail_recreational
}
sales_columns = list(sales_fields.keys())

# Augment sales items with sales, dataset by dataset.
for dataset in sales_datasets:

    # Read in sales chunk by chunk and merge sales type with the data.
    skip_rows = None
    rows_read = 0
    number_of_rows = dataset['rows']
    file_name = dataset['file_name']
    while rows_read < number_of_rows:

        # Define the chunk size.
        if rows_read > 0:
            skip_rows = [i for i in range(1, rows_read)]

        # Read and merge the chunk of sales.
        samples = pd.read_csv(
            file_name,
            sep='\t',
            encoding='utf-16',
            usecols=sales_columns,
            dtype=sales_fields,
            nrows=chunk_size,
            skiprows=skip_rows,
        )
        data = pd.merge(
            left=data,
            right=samples,
            how='left',
            left_on='sale_id',
            right_on='global_id',
        )
        data.rename(columns={'type_x': 'type'}, inplace=True)
        data.drop(['global_id', 'type_y'], axis=1, inplace=True, errors='ignore')

        # Iterate.
        rows_read += chunk_size
        percent_read = round(rows_read / number_of_rows * 100)
        print('Augmented %s / %s (%i%%) observations from %s' %
              (format_millions(rows_read), format_millions(number_of_rows),
                percent_read, file_name))

        # Save the data.
        data.to_csv(DATA_FILE, index=False)

# Finish cleaning the sales data.
data.rename(columns={
    'name': 'product_name',
    'type': 'sale_type',
}, inplace=True,)

# Save the data.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to augment with sales data:', print(end - start))

#------------------------------------------------------------------------------
# Augment the data with inventory data.
# Approximate runtime:
#------------------------------------------------------------------------------

# Read in the random sample.
start = datetime.now()
data = pd.read_csv(DATA_FILE)

# Merge sale_items inventory_id to inventories inventory_id.
data_file = f'{DATA_DIR}/Inventories_0.csv'
fields = {
    'global_id': 'string',
    'inventory_type_id': 'string',
    'lab_result_id': 'string',
    'strain_id': 'string',
    # TODO: Check if inventory has more reliable quantity and uom measure.
    'qty': 'float',
    'uom': 'string',
    'additives': 'string',
    'serving_num': 'float',
}
rename_columns = {
    'qty': 'inventory_qty',
    'uom': 'inventory_uom',
}
chunk_size = 13_000_000
row_count = 129_920_072
read_rows = 0
skiprows = None
columns = list(fields.keys())
# for field in columns:
#     data[field] = pd.NA
while read_rows < row_count:
    if read_rows:
        skiprows = [i for i in range(1, read_rows)]

    # Read in a shard of data.
    shard = pd.read_csv(
        data_file,
        sep='\t',
        encoding='utf-16',
        usecols=columns,
        dtype=fields,
        skiprows=skiprows,
        nrows=chunk_size,
    )
    shard.rename(columns=rename_columns, inplace=True)

    # Merge data. There many be many sales to 1 inventory.
    shard.drop_duplicates('global_id', keep='last', inplace=True)
    data = pd.merge(
        data,
        shard,
        left_on='inventory_id',
        right_on='global_id',
        how='left',
        validate='m:1',
        suffixes=(None, '_y'),
    )
    try:
        data['inventory_type_id'] = data['inventory_type_id'].fillna(data['inventory_type_id_y'])
        data['lab_result_id'] = data['lab_result_id'].fillna(data['lab_result_id_y'])
        data['strain_id'] = data['strain_id'].fillna(data['strain_id_y'])
        data['inventory_qty'] = data['inventory_qty'].fillna(data['inventory_qty_y'])
        data['inventory_uom'] = data['inventory_uom'].fillna(data['inventory_uom_y'])
    except KeyError:
        pass

    # Remove '_y' columns.
    column_names = list(data.columns)
    drop_columns = ['global_id']
    for name in column_names:
        if name.endswith('_y'):
            drop_columns.append(name)
    try:
        data.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    except TypeError:
        pass

    # Increment to the next shard.
    read_rows += chunk_size
    percent_read = round(read_rows / row_count * 100)
    print('Read %i%% of observations from %s' % (percent_read, data_file))
    print(
        'Identified',
        len(data.loc[~data.inventory_type_id.isnull()]),
        'out of',
        len(data),
        'inventory IDs.'
    )
    if len(data.loc[~data.inventory_type_id.isnull()]) == len(data):
        break

# Save the data.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to augment with inventory data:', print(end - start))

#--------------------------------------------------------------------------
# Augment the data with inventory type data.
# Approximate runtime:
#--------------------------------------------------------------------------

# Read in the random sample.
start = datetime.now()
data = pd.read_csv(DATA_FILE)

# Get inventory type with inventory_type_id to get name and intermediate_type.
data_file = f'{DATA_DIR}/InventoryTypes_0.csv'
fields = {
    'global_id': 'string',
    'name': 'string',
    'intermediate_type': 'string',
}
chunk_size = 28_510_000
row_count = 57_016_229
read_rows = 0
skiprows = None
columns = list(fields.keys())
while read_rows < row_count:
    if read_rows:
        skiprows = [i for i in range(1, read_rows)]

    # Read in a shard of data.
    shard = pd.read_csv(
        data_file,
        sep='\t',
        encoding='utf-16',
        usecols=columns,
        dtype=fields,
        skiprows=skiprows,
        nrows=chunk_size,
    )

    # Merge data. There many be many inventory items with the same inventory type.
    shard.rename(columns={'name': 'inventory_name'}, inplace=True)
    shard.drop_duplicates('global_id', keep='last', inplace=True)
    data = pd.merge(
        data,
        shard,
        left_on='inventory_type_id',
        right_on='global_id',
        how='left',
        validate='m:1',
        suffixes=(None, '_y'),
    )
    try:
        data['intermediate_type'] = data['intermediate_type'].fillna(data['intermediate_type_y'])
        data['inventory_name'] = data['inventory_name'].fillna(data['inventory_name_y'])
    except KeyError:
        pass

    # Remove '_y' columns.
    column_names = list(data.columns)
    drop_columns = ['global_id']
    for name in column_names:
        if name.endswith('_y'):
            drop_columns.append(name)
    try:
        data.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    except TypeError:
        pass

    # Increment to the next shard.
    read_rows += chunk_size
    percent_read = round(read_rows / row_count * 100)
    print('Read %i%% of observations from %s' % (percent_read, data_file))
    print(
        'Identified',
        len(data.loc[~data.intermediate_type.isnull()]),
        'out of',
        len(data),
        'inventory types.'
    )

    if len(data.loc[~data.intermediate_type.isnull()]) == len(data):
        break

# Save the data.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to augment with inventory types:', print(end - start))


#--------------------------------------------------------------------------
# Augment the data with lab results data.
# Approximate runtime: 18s
#--------------------------------------------------------------------------

def read_lab_results(
        columns=None,
        fields=None,
        date_columns=None,
        nrows=None,
        data_dir='../.datasets',
):
    """
    1. Read Leaf lab results.
    2. Sort the data, removing null observations.
    3. Define a lab ID for each observation and remove attested lab results.
    """
    shards = []
    lab_datasets = ['LabResults_0', 'LabResults_1', 'LabResults_2']
    for dataset in lab_datasets:
        lab_data = pd.read_csv(
            f'{data_dir}/{dataset}.csv',
            sep='\t',
            encoding='utf-16',
            usecols=columns,
            dtype=fields,
            parse_dates=date_columns,
            nrows=nrows,
        )
        shards.append(lab_data)
        del lab_data
        gc.collect()
    df = pd.concat(shards)
    del shards
    gc.collect()
    df.dropna(subset=['global_id'], inplace=True)
    df.sort_index(inplace=True)
    df['lab_id'] = df['global_id'].map(lambda x: x[x.find('WAL'):x.find('.')])
    df = df.loc[df.lab_id != '']
    return df

# # Read in the random sample.
# start = datetime.now()
# data = pd.read_csv(DATA_FILE)

# Add lab result data.
lab_result_date_columns = ['created_at']
lab_result_fields = {
    'global_id': 'string',
    'for_mme_id': 'string',
    'cannabinoid_cbc_percent': 'float',
    'cannabinoid_cbc_mg_g': 'float',
    'cannabinoid_cbd_percent': 'float',
    'cannabinoid_cbd_mg_g': 'float',
    'cannabinoid_cbda_percent': 'float',
    'cannabinoid_cbda_mg_g': 'float',
    'cannabinoid_cbdv_percent': 'float',
    'cannabinoid_cbdv_mg_g': 'float',
    'cannabinoid_cbg_percent': 'float',
    'cannabinoid_cbg_mg_g': 'float',
    'cannabinoid_cbga_percent': 'float',
    'cannabinoid_cbga_mg_g': 'float',
    'cannabinoid_cbn_percent': 'float', 
    'cannabinoid_cbn_mg_g': 'float',
    'cannabinoid_d8_thc_percent': 'float',
    'cannabinoid_d8_thc_mg_g': 'float',
    'cannabinoid_d9_thca_percent': 'float',
    'cannabinoid_d9_thca_mg_g': 'float',
    'cannabinoid_d9_thc_percent': 'float',
    'cannabinoid_d9_thc_mg_g': 'float',
    'cannabinoid_thcv_percent': 'float',
    'cannabinoid_thcv_mg_g': 'float',
}
cannabinoid_percents = [
    'cannabinoid_cbc_percent',
    'cannabinoid_cbd_percent',
    'cannabinoid_cbda_percent',
    'cannabinoid_cbdv_percent',
    'cannabinoid_cbg_percent',
    'cannabinoid_cbga_percent',
    'cannabinoid_cbn_percent',
    'cannabinoid_d8_thc_percent',
    'cannabinoid_d9_thca_percent',
    'cannabinoid_d9_thc_percent',
    'cannabinoid_thcv_percent',
]
cannabinoid_mg_g = [
    'cannabinoid_cbc_mg_g',
    'cannabinoid_cbd_mg_g',
    'cannabinoid_cbda_mg_g',
    'cannabinoid_cbdv_mg_g',
    'cannabinoid_cbg_mg_g',
    'cannabinoid_cbga_mg_g',
    'cannabinoid_cbn_mg_g',
    'cannabinoid_d8_thc_mg_g',
    'cannabinoid_d9_thca_mg_g',
    'cannabinoid_d9_thc_mg_g',
    'cannabinoid_thcv_mg_g',
]
rename_columns = {
    'created_at': 'tested_at',
    'for_mme_id': 'producer_mme_id',
}

# Read in all of the lab results.
lab_results = read_lab_results(
    columns=list(lab_result_fields.keys()) + lab_result_date_columns,
    fields=lab_result_fields,
    date_columns=lab_result_date_columns,
    data_dir=DATA_DIR,
)
lab_results.rename(columns=rename_columns, inplace=True)

# Fill missing cannabinoid percents and mg/g values.
# FIXME: Also replace 0's if precent or mg_g is non-zero.
for analyte_percent in cannabinoid_percents:
    analyte = analyte_percent.replace('_percent', '')
    analyte_mg_g = analyte + '_mg_g'
    percent = lab_results[analyte_percent]
    lab_results[analyte_percent].fillna(lab_results[analyte_mg_g] / 10, inplace=True)
    lab_results[analyte_mg_g].fillna(lab_results[analyte_percent] * 10, inplace=True)
    

# Calculate total cannabinoids.
lab_results['total_cannabinoid_percent'] = lab_results[cannabinoid_percents].sum(axis=1)
lab_results['total_cannabinoid_mg_g'] = lab_results[cannabinoid_mg_g].sum(axis=1)

# Merge the data with lab results, assuming each lab result can code to multiple sales.
data = pd.merge(
    data,
    lab_results,
    left_on='lab_result_id',
    right_on='global_id',
    how='left',
    validate='m:1',
    suffixes=(None, '_y'),
)
data.drop(['global_id'], axis=1, inplace=True)

# Save the data.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to augment with lab results:', print(end - start))


#--------------------------------------------------------------------------
# Augment the data with producer licensee data.
# Approximate runtime:
#--------------------------------------------------------------------------

# Read in the random sample.
data = pd.read_csv(DATA_FILE)

# Add licensee data to eac observation.
licensees_file_name = f'{DATA_DIR}/augmented/augmented-washington-state-licensees.csv'
licensee_fields = {
    'global_id': 'string',
    'latitude': 'string',
    'longitude': 'string',
    'name': 'string',
    'postal_code': 'string',
    'type': 'string',
}
rename_columns = {
    'global_id': 'producer_mme_id',
    'latitude': 'producer_latitude',
    'longitude': 'producer_longitude',
    'name': 'producer_name',
    'postal_code': 'producer_postal_code',
    'type': 'producer_type',
}
licensees = pd.read_csv(
    licensees_file_name,
    usecols=list(licensee_fields.keys()),
    dtype=licensee_fields,
)
licensees.rename(columns=rename_columns, inplace=True)
data = pd.merge(
    left=data,
    right=licensees,
    how='left',
    left_on='producer_mme_id',
    right_on='producer_mme_id'
)

# Remove '_y' columns.
column_names = list(data.columns)
drop_columns = []
for name in column_names:
    if name.endswith('_y'):
        drop_columns.append(name)
try:
    data.drop(drop_columns, axis=1, inplace=True, errors='ignore')
except TypeError:
    pass

# Save the data.
data.to_csv(DATA_FILE, index=False)


#--------------------------------------------------------------------------
# TODO: Augment the data with strain name?
# Approximate runtime:
#--------------------------------------------------------------------------

# Read in the random sample.
start = datetime.now()
data = pd.read_csv(DATA_FILE)

# Read in the augmenting data.
data_file = f'{DATA_DIR}/Strains_0.csv'
fields = {
    'global_id': 'string',
    'name': 'string',
}
rename_columns = {'name': 'strain_name'}
columns = list(fields.keys())
shard = pd.read_csv(
    data_file,
    sep='\t',
    encoding='utf-16',
    usecols=columns,
    dtype=fields,
)

# Augment the data.
shard.rename(columns=rename_columns, inplace=True)
shard.drop_duplicates('global_id', keep='last', inplace=True)
data = pd.merge(
    data,
    shard,
    left_on='strain_id',
    right_on='global_id',
    how='left',
    validate='m:1',
    suffixes=(None, '_y'),
)

# Save the data.
data.to_csv(DATA_FILE, index=False)
end = datetime.now()
print('Time to augment with strain names:', print(end - start))


#--------------------------------------------------------------------------
# Analyze the data.
#--------------------------------------------------------------------------

# Read in the random sample.
# data = pd.read_csv(DATA_FILE)

# TODO: Determine wholesale vs retail transactions.
# data = data.loc[data['sale_type'] != 'wholesale']

# TODO: Drop observations with negative prices? or prices > $1000?
# data = data.loc[data.price_total > 0]

# TODO: Estimate the average_price by sample type.


#--------------------------------------------------------------------------
# Visualize the data.
#--------------------------------------------------------------------------

# TODO: Look at the probability density functions (.pdfs) of the data.


# TODO: Create choropleths of average price by zip code for each sample type.
