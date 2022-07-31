"""
Get All of MCR Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 7/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect all of MCR Labs' publicly published lab results.

Data Sources:
    
    - MCR Labs Test Results
    URL: <https://reports.mcrlabs.com>

"""
# Standard imports.
from datetime import datetime

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas.mcrlabs import get_mcr_labs_test_results
from cannlytics.firebase import initialize_firebase, update_documents
from cannlytics.utils.utils import to_excel_with_style


# Specify where your data lives.
DATA_DIR = '../../../.datasets/lab_results'

# Get all of the results!
all_results = get_mcr_labs_test_results(
    starting_page=1,
    pause=3,
)

# Save the results to Excel.
data = pd.DataFrame(all_results)
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
datafile = f'{DATA_DIR}/mcr-lab-results-{timestamp}.xlsx'
to_excel_with_style(data, datafile)

# Prepare the data to upload to Firestore.
refs, updates = [], []
for index, obs in data:
    sample_id = obs['sample_id']
    refs.append(f'public/data/lab_results/{sample_id}')
    updates.append(obs.to_dict())

# Initialize Firebase and upload the data to Firestore!
database = initialize_firebase()
update_documents(refs, updates, database=database)
print('Added %i lab results to Firestore!' % len(refs))
