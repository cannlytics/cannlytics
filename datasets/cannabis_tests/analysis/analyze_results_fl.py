"""
Analyze Results | Florida
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/19/2024
Updated: 6/15/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
from typing import List
from dotenv import dotenv_values
import json
import gc
import os

# External imports:
from cannlytics.data import save_with_copyright
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import (
    CoADoc,
    get_result_value,
    standardize_results,
)
from cannlytics.data.coas.parsing import get_coa_files, parse_coa_pdfs
from cannlytics.firebase import (
    initialize_firebase,
    create_short_url,
    get_file_url,
    update_documents,
    upload_file,
)
from cannlytics.compounds import cannabinoids, terpenes
from cannlytics.utils.utils import hash_file
import pandas as pd

# Internal imports:
from analyze_results import calc_results_stats, calc_aggregate_results_stats


def analyze_results_fl(
    cache_path: str,
    pdf_dir: str,
    reverse: bool = False,
) -> pd.DataFrame:
    """
    Analyze Florida lab results.

    Args:
        cache_path (str): The path to the cache file.
        pdf_dir (str): The directory where the PDFs are stored.
        reverse (bool): Whether to reverse the order of the results.

    Returns:
        pd.DataFrame: The analyzed results.
    """
    # Initialize cache.
    cache = Bogart(cache_path)

    # Get all of the PDFs.
    pdfs = get_coa_files(pdf_dir)

    # Sort the PDFs by modified date
    pdfs.sort(key=os.path.getmtime)

    # Parse the PDFs.
    parse_coa_pdfs(pdfs, cache=cache, reverse=reverse)


# === Test ===
if __name__ == '__main__':
    
    # Parse all of the COAs.
    analyze_results_fl(
        cache_path = 'D://data/.cache/results-fl.jsonl',
        pdf_dir = 'D://data/florida/results/pdfs',
        reverse=True,
    )

    # Read the cache.
    results = Bogart('D://data/.cache/results-fl.jsonl').to_df()
    print('Read %i results from cache.' % len(results))

    # TODO: Figure out why there are duplicates.

    # Drop duplicates.
    results = results.drop_duplicates(subset=['sample_hash'])

    # TODO: Identify the same COA parsed multiple ways.
    multiple_coas = results['coa_pdf'].value_counts()
    print('Multiple COAs:', multiple_coas[multiple_coas > 1])

    # FIXME: Handle:
    # - `download.pdf`
    # - `DA20618004-002.pdf`

    # Standardize the data.
    # TODO: Add pesticides, heavy metals, residual solvents, etc.
    state = 'FL'
    cannabinoid_keys = list(cannabinoids.keys())
    terpene_keys = list(terpenes.keys())
    compounds = cannabinoid_keys + terpene_keys
    results = standardize_results(results, compounds)
    results['lab_state'] = results['lab_state'].fillna(state)
    results['producer_state'] = results['producer_state'].fillna(state)

    # Calculate results statistics.
    results = calc_results_stats(
        results,
        cannabinoid_keys=cannabinoid_keys,
        terpene_keys=terpene_keys,
    )

    # Calculate aggregate statistics.
    stats = calc_aggregate_results_stats(
        results,
        cannabinoid_keys=cannabinoid_keys,
        terpene_keys=terpene_keys,
    )

    # # Save all of the data.
    # output_dir = 'D://data/florida/results/datasets'
    # date = datetime.now().strftime('%Y-%m-%d')
    # outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
    # results.replace(r'\\u0000', '', regex=True, inplace=True)
    # save_with_copyright(
    #     results,
    #     outfile,
    #     dataset_name='Florida Cannabis Lab Results',
    #     author='Keegan Skeate',
    #     publisher='Cannlytics',
    #     sources=['Kaycha Labs', 'TerpLife Labs'],
    #     source_urls=['https://yourcoa.com', 'https://www.terplifelabs.com'],
    # )
    # print('Saved %i COA data:' % len(results), outfile)


#-----------------------------------------------------------------------
# Upload COA PDFs to Google Cloud Storage and data to Firestore.
#-----------------------------------------------------------------------

# # TODO: Re-write using Bogart cache.

# # Use a local cache to keep track of lab results in Firestore,
# # PDFs in Google Cloud Storage, and which datafiles are in Cloud Storage.
# cache_dir = 'D://data/florida/cache'
# cache_file = os.path.join(cache_dir, 'results-fl.json')
# if os.path.exists(cache_file):
#     with open(cache_file, 'r') as f:
#         cache = json.load(f)
# else:
#     cache = {}
#     os.makedirs(cache_dir, exist_ok=True)

# # Match COA PDFs with the results.
# pdf_dir = 'D://data/florida/results/pdfs'
# coa_pdfs = {}
# for index, result in all_results.iterrows():

#     # Get the name of the PDF.
#     identifier = result['coa_pdf']
#     if identifier == 'download.pdf':
#         lab_results_url = result['lab_results_url']
#         identifier = lab_results_url.split('=')[-1].split('?')[0]
    
#     # Find the matching PDF.
#     for root, _, files in os.walk(pdf_dir):
#         for filename in files:
#             if identifier in filename:
#                 pdf_path = os.path.join(root, filename)
#                 coa_pdfs[result['sample_hash']] = pdf_path
#                 break

# # Initialize Firebase.
# config = dotenv_values('.env')
# db = initialize_firebase()
# bucket_name = config['FIREBASE_STORAGE_BUCKET']
# firebase_api_key = config['FIREBASE_API_KEY']

# # Upload datafiles to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# for datafile in datafiles:
#     filename = os.path.split(datafile)[-1]
#     if filename not in cache.get('datafiles', []):
#         file_ref = f'data/results/florida/datasets/{filename}'
#         # upload_file(
#         #     destination_blob_name=file_ref,
#         #     source_file_name=datafile,
#         #     bucket_name=bucket_name,
#         # )
#         print('Uploaded:', file_ref)
#         cache.setdefault('datafiles', []).append(filename)

# # Upload PDFs to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# print('Number of unique COA PDFs:', len(coa_pdfs))
# for sample_hash, pdf_path in coa_pdfs.items():
#     print('Uploading:', pdf_path)
#     pdf_hash = hash_file(pdf_path)

#     if pdf_hash not in cache.get('pdfs', []):

#         # Upload the file.
#         file_ref = f'data/results/florida/pdfs/{pdf_hash}.pdf'
#         # upload_file(
#         #     destination_blob_name=file_ref,
#         #     source_file_name=pdf_path,
#         #     bucket_name=bucket_name,
#         # )

#         # # Get download URL and create a short URL.
#         # download_url, short_url = None, None
#         # try:
#         #     download_url = get_file_url(file_ref, bucket_name=bucket_name)
#         #     short_url = create_short_url(
#         #         api_key=firebase_api_key,
#         #         long_url=download_url,
#         #         project_name=db.project
#         #     )
#         # except Exception as e:
#         #     print('Failed to get download URL:', e)

#         # # Keep track of the file reference and download URLs.
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'file_ref'] = file_ref
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'download_url'] = download_url
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'short_url'] = short_url

#         # Cache the PDF.
#         cache.setdefault('pdfs', []).append(pdf_hash)

# # Upload the raw data to Firestore.
# # Checks if the data has been uploaded according to the local cache.
# refs, updates = [], []
# collection = 'results'
# for _, obs in all_results.iterrows():
#     doc_id = obs['sample_hash']
#     if doc_id not in cache.get('results', []):
#         refs.append(f'{collection}/{doc_id}')
#         updates.append(obs.to_dict())
#         cache.setdefault('results', []).append(doc_id)
# # if refs:
# #     update_documents(refs, updates, database=db)
# #     print('Uploaded %i results to Firestore.' % len(refs))

# # TODO: Save the statistics to Firestore.

# # Save the updated cache
# with open(cache_file, 'w') as f:
#     json.dump(cache, f)
#     print('Saved cache:', cache_file)
