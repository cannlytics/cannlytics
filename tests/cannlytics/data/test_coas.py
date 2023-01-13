"""
CoADoc Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2022
Updated: 9/10/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:  A rigorous test of CoADoc parsing.
"""
# Standard imports.
import os

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas import CoADoc
from cannlytics.data.data import create_hash


# Specify where your data lives.
DATA_DIR = '.datasets/coas/Flore COA'
TEMP_PATH = '.datasets/coas/tmp'

# Initialize a parser.
parser = CoADoc()

# Create the output data directory before beginning.
datafile_dir = f'{DATA_DIR}/datafiles'
if not os.path.exists(datafile_dir):
    os.makedirs(datafile_dir)

# Iterate over PDF directory.
all_data = []
for path, subdirs, files in os.walk(DATA_DIR):
    for name in files:

        # Only parse PDFs.
        if not name.endswith('.pdf'):
            continue

        # [✓] TEST: Parse CoA PDFs one by one.
        try:
            filename = os.path.join(path, name)
            coa_data = parser.parse(filename, temp_path=TEMP_PATH)
            all_data.extend(coa_data)
            print('Parsed:', filename)
        except:
            print('Error:', filename)

# Format the data as a DataFrame.
data = pd.DataFrame(all_data)

# [✓] TEST: Create hashes.
coa_df = data.where(pd.notnull(data), None)
coa_df['results_hash'] = coa_df['results'].apply(
    lambda x: create_hash(x),
)
coa_df['sample_hash'] = coa_df.loc[:, coa_df.columns != 'sample_hash'].apply(
    lambda x: create_hash(x.to_dict()),
    axis=1,
)
data_hash = create_hash(coa_df)

# [✓] TEST: Standardize and save the CoA data.
outfile = f'{datafile_dir}/{data_hash}.xlsx'
parser.save(coa_df, outfile)
print('Saved CoA data:', outfile)
