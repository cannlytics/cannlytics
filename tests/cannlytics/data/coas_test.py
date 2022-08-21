"""
CoADoc Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/1/2022
Updated: 8/20/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:  A rigorous test of CoADoc parsing.
"""
# Standard imports.
from datetime import datetime
import os

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas import CoADoc


# Specify where your data lives.
DATA_DIR = '../../../.datasets/coas/Flore COA'

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
        file_name = os.path.join(path, name)
        coa_data = parser.parse(file_name)
        all_data.extend(coa_data)
        print('Parsed:', file_name)

# Format the data.
data = pd.DataFrame(all_data)

# [✓] TEST: Standardize and save the CoA data.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
outfile = f'{datafile_dir}/coa-data-{timestamp}.xlsx'
data.index = data['sample_id']
parser.save(data, outfile)
print('Saved CoA data:', outfile)
