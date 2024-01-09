"""
Get MD Lab Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2023
Updated: 1/8/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Collect all public Maryland lab result data.

Data Sources:
    
    - Public records request from the Maryland Medical Cannabis Commission (MMCC).

"""
# Standard imports:
from datetime import datetime
import os
import re

# External imports:
from cannlytics.utils import snake_case
import numpy as np
import pandas as pd


# Constants.
STATE = 'MD'


# === Latest CSV Extraction ===

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

# FIXME?
# # Standardize the columns.
# std = pd.DataFrame(pivot_df)
# std['product_subtype'] = None
# analytes = get_unique_analytes(pivot_df)
# elements_to_remove = ['TestPassed', 'TestingFacilityId', 'TestYear', 'StrainName']
# analytes = [x for x in analytes if x not in elements_to_remove]
# for analyte in analytes:
#     std[analyte] = np.nan
# skip_columns = ['PackageId', 'TestingFacilityId', 'TestPassed',
#                 'TestYear', 'StrainName']
# for index, row in pivot_df.iterrows():
#     for col in pivot_df.columns:
#         if col not in skip_columns:
#             if pd.notna(row[col]):
#                 analyte = col.split('(')[0].strip()
#                 subtype = col.split(')')[-1].strip()
#                 std.at[index, 'product_subtype'] = subtype
#                 std.at[index, analyte] = row[col]
# std = std[[col for col in std.columns if "(" not in col]]


# === Test ===
# [✓] Tested: 2023-09-27 by Keegan Skeate <keegan@cannlytics>
if __name__ == "__main__":
    pass

    # # Extract all data from the PRR PDF.
    # pdf_path = "../data/md/raw/public-records-request-md-2023-06-30.pdf"
    # extract_data_from_pdf(pdf_path)
    # dataset_folder = os.path.join(os.path.dirname(pdf_path), ".datasets")
    # aggregate_datasets(dataset_folder, "../data/md/raw/md-lab-results-2023-06-30.csv")

    # # Aggregate Maryland results from the PRR CSVs.
    # data_dir = r'D:\data\maryland\prr'
    # stats_dir = '../data/md'
    # md_results = get_results_md(data_dir, stats_dir)
    # print('Aggregated %i MD lab results.' % len(md_results))
