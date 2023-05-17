"""
Get All of SC Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/8/2022
Updated: 7/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect all of SC Labs' publicly published lab results.

Algorithm:

    1. Discover all SC Labs public clients by scanning:

      https://client.sclabs.com/client/{client}/

    2. Iterate over pages for each client, collecting samples until
    the 1st sample and active page are the same:

        https://client.sclabs.com/client/{client}/?page={page}

    3. (a) Get the sample details for each sample found.
       (b) Save the sample details.

Data Sources:
    
    - SC Labs Test Results
    URL: <https://client.sclabs.com/>

Note:

    This script has been DEPRECATED. It was used to collect the initial
    archive of California lab results.

"""
# Standard imports.
from datetime import datetime
import math
from time import sleep

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas.sclabs import (
    get_sc_labs_sample_details,
    get_sc_labs_test_results,
)
from cannlytics.firebase import initialize_firebase, update_documents

# Specify where your data lives.
DATA_DIR = '../../../.datasets/lab_results'
RAW_DATA = '../../../.datasets/lab_results/raw_data/sc_labs'

# Future work: Figure out a more efficient way to find all producer IDs.
PAGES = range(1, 12_000)
PRODUCER_IDS = list(PAGES)
PRODUCER_IDS.reverse()

# Alternatively, uncomment to read in the known producer IDs.
# from sc_labs_producer_ids import PRODUCER_IDS

# Iterate over potential client pages and client sample pages.
start = datetime.now()
clients = []
errors = []
test_results = []
for _id in PRODUCER_IDS:
    results = get_sc_labs_test_results(_id)
    if results:
        test_results += results
        print('Found all samples for producer:', _id)
        clients.append(_id)
    sleep(3)

# Save the results, just in case.
data = pd.DataFrame(test_results)
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
data.to_excel(datafile, index=False)
end = datetime.now()
print('Sample collection took:', end - start)

# Read in the saved test results (useful for debugging).
start = datetime.now()
data = pd.read_excel(datafile)

# Get the sample details for each sample found.
errors = []
rows = []
subset = data.loc[data['results'].isnull()]
total = len(subset)
for index, values in subset.iterrows():
    if not math.isnan(values['results']):
        continue
    percent = round((index  + 1) * 100 / total, 2)
    sample = values['lab_results_url'].split('/')[-2]
    details = get_sc_labs_sample_details(sample)
    rows.append({**values.to_dict(), **details})
    if details['results']:
        print('Results found (%.2f%%) (%i/%i):' % (percent, index + 1, total), sample)
    else:
        print('No results found (%.2f%%) (%i/%i):' % (percent, index + 1, total), sample)
    sleep(3)

    # Save every 500 samples just in case.
    if index % 500 == 0 and index != 0:
        data = pd.DataFrame(rows)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
        data.to_excel(datafile, index=False)
        print('Saved data:', datafile)

# Save the final results.
data = pd.DataFrame(rows)
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
data.to_excel(datafile, index=False)
end = datetime.now()
print('Detail collection took:', end - start)

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
