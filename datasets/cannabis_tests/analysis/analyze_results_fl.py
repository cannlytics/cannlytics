"""
Analyze Results | Florida
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/19/2024
Updated: 3/19/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
from dotenv import dotenv_values
import json
import gc
import os

# External imports:
from cannlytics.utils.utils import hash_file
from cannlytics.data.coas import CoADoc
from cannlytics.firebase import (
    initialize_firebase,
    create_short_url,
    get_file_url,
    update_documents,
    upload_file,
)
import pandas as pd
import os


#-----------------------------------------------------------------------
# Parse all FL COAs.
#-----------------------------------------------------------------------

data_dirs = [
    # FIXME: Labs without parsing algorithms:
    # r"D:\data\florida\results\pdfs\moderncanna",
    # r"D:\data\florida\results\pdfs\mtl",
    # r"D:\data\florida\results\pdfs\green-scientific-labs",
    # Labs with parsing algorithms:
    r"D:\data\florida\results\pdfs\terplife",
    r"D:\data\florida\results\pdfs\acs",
    r"D:\data\florida\results\pdfs\fl-medical-trees",
    r"D:\data\florida\results\pdfs/jungleboys",
    # Kaycha Labs:
    r"D:\data\florida\results\pdfs\MMTC-2015-0001",
    r"D:\data\florida\results\pdfs\MMTC-2015-0002",
    r"D:\data\florida\results\pdfs\MMTC-2015-0003",
    r"D:\data\florida\results\pdfs\MMTC-2015-0004",
    r"D:\data\florida\results\pdfs\MMTC-2015-0005",
    r"D:\data\florida\results\pdfs\MMTC-2016-0006",
    r"D:\data\florida\results\pdfs\MMTC-2016-0007",
    r"D:\data\florida\results\pdfs\MMTC-2017-0008",
    r"D:\data\florida\results\pdfs\MMTC-2017-0009",
    r"D:\data\florida\results\pdfs\MMTC-2017-0010",
    r"D:\data\florida\results\pdfs\MMTC-2017-0011",
    r"D:\data\florida\results\pdfs\MMTC-2017-0012",
    r"D:\data\florida\results\pdfs\MMTC-2017-0013",
    r"D:\data\florida\results\pdfs\MMTC-2018-0014",
    r"D:\data\florida\results\pdfs\MMTC-2019-0015",
    r"D:\data\florida\results\pdfs\MMTC-2019-0016",
    r"D:\data\florida\results\pdfs\MMTC-2019-0017",
    r"D:\data\florida\results\pdfs\MMTC-2019-0018",
    r"D:\data\florida\results\pdfs\MMTC-2019-0019",
    r"D:\data\florida\results\pdfs\MMTC-2019-0020",
    r"D:\data\florida\results\pdfs\MMTC-2019-0021",
    r"D:\data\florida\results\pdfs\MMTC-2019-0022",
]


# DEV: Find all of the already parsed and failed PDFs.
parsed_files, failed_files = [], []
logs_files = []
for logs_file in logs_files:
    with open(logs_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'Parsed:' in line:
                parsed_files.append(line.split('Parsed:')[1].strip())
            if 'Failed to parse:' in line:
                failed_files.append(line.split('Failed to parse:')[1].strip())

print('Parsed:', len(parsed_files))
print('Failed:', len(failed_files))


# Find all COA PDFs.
# TODO: Handle images as well.
pdfs = []
min_file_size = 21_000
for data_dir in data_dirs:
    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith('.pdf'):
                file_path = os.path.join(root, filename)

                # DEV: Skip already parsed files.
                # if file_path in parsed_files:
                #     continue

                # DEV: Skip failed files.
                if file_path in failed_files:
                    continue

                # DEV: Skip files that are too small.
                file_size = os.path.getsize(file_path)
                if file_size >= min_file_size:
                    pdfs.append(file_path)

# Define where data should live,
output_dir = 'D://data/florida/results/datasets'

# Parse each COA.
parser = CoADoc()
all_data = []
print(f'Parsing {len(pdfs)} COAs...')
for i, doc in enumerate(reversed(pdfs)):
    gc.collect()
    try:
        coa_data = parser.parse(doc, verbose=True)
        print(coa_data)
        if isinstance(coa_data, list):
            all_data.append(coa_data[0])
        elif isinstance(coa_data, dict):
            all_data.append(coa_data)
        else:
            print(f'No data found: {doc}')
            continue
        print(f'Parsed: {doc}')
    except Exception as e:
        print('Failed to parse:', doc)
        print(e)

    # Save a segment of the results.
    if i % 100 == 0 and i > 0:
        all_results = pd.DataFrame(all_data[-100:])
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
        outfile = os.path.join(output_dir, f'fl-results-{timestamp}.xlsx')
        all_results.replace(r'\\u0000', '', regex=True, inplace=True)
        all_results.to_excel(outfile, index=False)
        print(f'Saved {len(all_results)} parsed COAs: {outfile}')

# Save all of the data.
date = datetime.now().strftime('%Y-%m-%d')
outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
all_results = pd.DataFrame(all_data)
all_results.replace(r'\\u0000', '', regex=True, inplace=True)
parser.save(all_results, outfile)
print('Saved %i COA data:' % len(all_results), outfile)


#-----------------------------------------------------------------------
# Read all lab results.
#-----------------------------------------------------------------------

import os
import pandas as pd


# Aggregate lab results.
data_dir = "D://data/florida/results/datasets"
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
        print('Failed to read:', datafile)
        continue
    all_results.append(data)
all_results = pd.concat(all_results, ignore_index=True)
all_results.sort_values('coa_parsed_at', ascending=False, inplace=True)
all_results.drop_duplicates(subset=['sample_hash', 'results_hash'], keep='first', inplace=True)
all_results = all_results.loc[all_results['results'] != '[]']
print('Number of unique results:', len(all_results))

# Fill missing `producer_state` with FL.
all_results['producer_state'] = all_results['producer_state'].fillna('FL')

# Save the results locally.
date = pd.Timestamp.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'all-fl-results-{date}.xlsx')
all_results.to_excel(outfile, index=False)
print('Saved aggregate Florida lab results:', outfile)


#-----------------------------------------------------------------------
# TODO: Calculate statistics.
#-----------------------------------------------------------------------

from cannlytics.data.coas import get_result_value
from cannlytics.lims.compounds import cannabinoids, terpenes


# Find al unique terpenes and cannabinoids and see if there are any new compounds.
unidentified_compounds = set()
for index, row in all_results.iterrows():
    results = json.loads(row['results'])
    for result in results:
        if result.get('analysis') == 'cannabinoids' or result.get('analysis') == 'terpenes':
            unidentified_compounds.add(result['key'])
unidentified_compounds = unidentified_compounds - set(cannabinoids + terpenes)
print('Unidentified compounds:', len(unidentified_compounds))

# Get the results for each cannabinoid and terpene.
for a in cannabinoids + terpenes:
    print('Augmenting:', a)
    all_results[a] = all_results['results'].apply(
        lambda x: get_result_value(x, a, key='key')
    )

# TODO: Ensure totals are calculated:
# - total_cannabinoids
# - total_thc
# - total_cbd
# - total_terpenes

# TODO: Calculate averages, medians, standard deviations, and percentiles
# for cannabinoids and terpenes.
# Time series:
# - daily
# - weekly
# - monthly
# - quarterly
# - yearly


#-----------------------------------------------------------------------
# Upload COA PDFs to Google Cloud Storage.
#-----------------------------------------------------------------------

# Use a local cache to keep track of lab results in Firestore,
# PDFs in Google Cloud Storage, and which datafiles are in Cloud Storage.
cache_dir = 'D://data/florida/cache'
cache_file = os.path.join(cache_dir, 'cache.json')
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cache = json.load(f)
else:
    cache = {}
    os.makedirs(cache_dir, exist_ok=True)

# Match COA PDFs with the results.
pdf_dir = 'D://data/florida/results/pdfs'
coa_pdfs = {}
for index, result in all_results.iterrows():

    # Get the name of the PDF.
    identifier = result['coa_pdf']
    if identifier == 'download.pdf':
        lab_results_url = result['lab_results_url']
        identifier = lab_results_url.split('=')[-1].split('?')[0]
    
    # Find the matching PDF.
    for root, _, files in os.walk(pdf_dir):
        for filename in files:
            if identifier in filename:
                pdf_path = os.path.join(root, filename)
                coa_pdfs[result['sample_hash']] = pdf_path
                break

# Initialize Firebase.
config = dotenv_values('.env')
db = initialize_firebase()
bucket_name = config['FIREBASE_STORAGE_BUCKET']
firebase_api_key = config['FIREBASE_API_KEY']

# Upload datafiles to Google Cloud Storage.
# Checks if the file has been uploaded according to the local cache.
for datafile in datafiles:
    filename = os.path.split(datafile)[-1]
    if filename not in cache.get('datafiles', []):
        file_ref = f'data/results/florida/datasets/{filename}'
        # upload_file(
        #     destination_blob_name=file_ref,
        #     source_file_name=datafile,
        #     bucket_name=bucket_name,
        # )
        print('Uploaded:', file_ref)
        cache.setdefault('datafiles', []).append(filename)

# Upload PDFs to Google Cloud Storage.
# Checks if the file has been uploaded according to the local cache.
print('Number of unique COA PDFs:', len(coa_pdfs))
for sample_hash, pdf_path in coa_pdfs.items():
    print('Uploading:', pdf_path)
    pdf_hash = hash_file(pdf_path)

    if pdf_hash not in cache.get('pdfs', []):

        # Upload the file.
        file_ref = f'data/results/florida/pdfs/{pdf_hash}.pdf'
        # upload_file(
        #     destination_blob_name=file_ref,
        #     source_file_name=pdf_path,
        #     bucket_name=bucket_name,
        # )

        # # Get download URL and create a short URL.
        # download_url, short_url = None, None
        # try:
        #     download_url = get_file_url(file_ref, bucket_name=bucket_name)
        #     short_url = create_short_url(
        #         api_key=firebase_api_key,
        #         long_url=download_url,
        #         project_name=db.project
        #     )
        # except Exception as e:
        #     print('Failed to get download URL:', e)

        # # Keep track of the file reference and download URLs.
        # all_results.loc[all_results['sample_hash'] == sample_hash, 'file_ref'] = file_ref
        # all_results.loc[all_results['sample_hash'] == sample_hash, 'download_url'] = download_url
        # all_results.loc[all_results['sample_hash'] == sample_hash, 'short_url'] = short_url

        # Cache the PDF.
        cache.setdefault('pdfs', []).append(pdf_hash)

# Upload the raw data to Firestore.
# Checks if the data has been uploaded according to the local cache.
refs, updates = [], []
collection = 'results'
for _, obs in all_results.iterrows():
    doc_id = obs['sample_hash']
    if doc_id not in cache.get('results', []):
        refs.append(f'{collection}/{doc_id}')
        updates.append(obs.to_dict())
        cache.setdefault('results', []).append(doc_id)
# if refs:
#     update_documents(refs, updates, database=db)
#     print('Uploaded %i results to Firestore.' % len(refs))

# TODO: Save the statistics to Firestore.

# Save the updated cache
with open(cache_file, 'w') as f:
    json.dump(cache, f)
    print('Saved cache:', cache_file)
