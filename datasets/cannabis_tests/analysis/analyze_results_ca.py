"""
Analyze Results | California
Copyright (c) 2023-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2023
Updated: 6/3/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
import os
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import CoADoc, get_result_value
from cannlytics.firebase import initialize_firebase
from cannlytics.lims.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import pandas as pd

# Internal imports:
from parse_results import get_pdf_files, parse_coa_pdfs

# Initialize cache.
cache_path = 'D://data/.cache/results-ca.jsonl'
cache = Bogart(cache_path)

# Get all of the PDFs.
pdf_dir = 'D://data/california/results/pdfs'
pdfs = get_pdf_files(pdf_dir)

# DEV: Cut the PDFS in half.
import random
random.seed(42)
pdfs = pdfs[:len(pdfs) // 2]
pdfs = random.sample(pdfs, len(pdfs))

# Parse the PDFs.
all_results = parse_coa_pdfs(pdfs, cache=cache, reverse=True)

# Fill missing state.
STATE = 'CA'
all_results = pd.DataFrame(all_results)
all_results['lab_state'] = all_results['lab_state'].fillna(STATE)
all_results['producer_state'] = all_results['producer_state'].fillna(STATE)

# # FIXME: Get the results for known compounds.
# for a in cannabinoids + terpenes:
#     print('Augmenting:', a)
#     all_results[a] = all_results['results'].apply(lambda x: get_result_value(x, a))

# Save all of the parsed data.
data_dir = 'D://data/california/results/datasets'
date = pd.Timestamp.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'ca-results-{date}.xlsx')
parser = CoADoc()
try:
    parser.save(all_results, outfile)
except:
    all_results.to_excel(outfile, index=False)
# TODO: Copy outfile to latest file.

print(f'Saved {len(all_results)} {STATE} results: {outfile}')


#-----------------------------------------------------------------------
# Refactor: Aggregate all lab results.
#-----------------------------------------------------------------------

# # Aggregate CA results.
# datafiles = []
# data_dirs = [
#     # "D://data/california/results/datasets/sclabs",
#     "D://data//california/results/datasets/flower-company",
#     "D://data/california/results/datasets",
# ]
# for data_dir in data_dirs:
#     files = os.listdir(data_dir)
#     files = [os.path.join(data_dir, x) for x in files if x.endswith('.xlsx')]
#     files = [x for x in files if 'all' not in x and 'urls' not in x]
#     datafiles.extend(files)
# print('Number of datafiles:', len(datafiles))
# all_results = []
# for datafile in datafiles:
#     print('Reading:', datafile)
#     try:
#         data = pd.read_excel(datafile)
#     except:
#         print('Error reading:', datafile)
#         continue
#     all_results.append(data)
# all_results = pd.concat(all_results, ignore_index=True)
# all_results.sort_values('coa_parsed_at', ascending=False, inplace=True)
# all_results.drop_duplicates(subset=['sample_id', 'results_hash'], keep='first', inplace=True)
# all_results = all_results.loc[all_results['results'] != '[]']
# print('Number of results:', len(all_results))

# # Get the results for known compounds.
# for a in cannabinoids + terpenes:
#     print('Augmenting:', a)
#     all_results[a] = all_results['results'].apply(lambda x: get_result_value(x, a))

# # Save the results.
# date = pd.Timestamp.now().strftime('%Y-%m-%d')
# outfile = os.path.join(data_dir, f'all-ca-results-{date}.xlsx')
# all_results.to_excel(outfile, index=False)
# print(f'Saved {len(all_results)} CA results:', outfile)


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

# FIXME: Refactor into re-usable functions.

# Use a local cache to keep track of lab results in Firestore,
# PDFs in Google Cloud Storage, and which datafiles are in Cloud Storage.
# cache_dir = 'D://data/california/cache'
# cache_file = os.path.join(cache_dir, 'results-ca.json')
# if os.path.exists(cache_file):
#     with open(cache_file, 'r') as f:
#         cache = json.load(f)
# else:
#     cache = {}
#     os.makedirs(cache_dir, exist_ok=True)

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
# FIXME:
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
        # FIXME:
        # cache.setdefault('datafiles', []).append(filename)

# Upload PDFs to Google Cloud Storage.
# Checks if the file has been uploaded according to the local cache.
print('Number of unique COA PDFs:', len(coa_pdfs))
for sample_hash, pdf_path in coa_pdfs.items():
    print('Uploading:', pdf_path)
    pdf_hash = cache.hash_file(pdf_path)

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
        # FIXME:
        # cache.setdefault('pdfs', []).append(pdf_hash)

# Upload the raw data to Firestore.
# Checks if the data has been uploaded according to the local cache.
refs, updates = [], []
collection = 'results'
for _, obs in all_results.iterrows():
    doc_id = obs['sample_hash']
    if doc_id not in cache.get('results', []):
        refs.append(f'{collection}/{doc_id}')
        updates.append(obs.to_dict())
        # FIXME:
        # cache.setdefault('results', []).append(doc_id)
# if refs:
#     update_documents(refs, updates, database=db)
#     print('Uploaded %i results to Firestore.' % len(refs))

# TODO: Save the statistics to Firestore.

# Save the updated cache
# with open(cache_file, 'w') as f:
#     json.dump(cache, f)
#     print('Saved cache:', cache_file)
