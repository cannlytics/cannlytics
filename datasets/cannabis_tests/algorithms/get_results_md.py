"""
Get MD Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2023
Updated: 1/12/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Collect all public Maryland lab result data.

Data Sources:
    
    - Public records request from the Maryland Medical Cannabis Commission (MMCC).

"""
# Standard imports:
import os

# External imports:
import pandas as pd


# Constants.
STATE = 'MD'


# Get the data files.
data_dir = 'D:\data\maryland\md-prr-2024-01-02'
datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir)]

# Read all of the data.
all_data = []
for datafile in datafiles:

    # Read the segment of data.
    df = pd.read_csv(datafile)

    # Pivot the dataframe.
    pivot_df = df.pivot_table(
        index=[
            'TestPerformedDate',
            'PackageId',
            'StrainName',
            'TestingFacilityId',
            'ProductCategoryName',
        ],
        columns='TestTypeName',
        values='TestResultLevel',
        aggfunc='first'
    ).reset_index()
    pivot_df = pd.DataFrame(pivot_df)

    # Determine the "status" based on the "TestPassed" column.
    status = df.groupby('PackageId')['TestPassed'].apply(lambda x: 'Fail' if False in x.values else 'Pass')
    pivot_df = pivot_df.merge(status, left_on='PackageId', right_index=True)

    # Record the data.
    all_data.append(pivot_df)

# Aggregate all lab results.
results = pd.concat(all_data, ignore_index=True)
print('Aggregated %i MD lab results.' % len(results))
datafile = '../data/lab_results/md-lab-results-2024-01-02.csv'
results.to_csv(datafile, index=False)
