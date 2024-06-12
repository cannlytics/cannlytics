"""
Analyze Results | Florida
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/19/2024
Updated: 6/9/2024
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
from cannlytics.firebase import (
    initialize_firebase,
    create_short_url,
    get_file_url,
    update_documents,
    upload_file,
)
from cannlytics.lims.compounds import cannabinoids, terpenes
from cannlytics.utils.utils import hash_file
import pandas as pd

# Internal imports:
from parse_results import get_pdf_files, parse_coa_pdfs

def analyze_results_fl(
    cache_path: str,
    pdf_dir: str,
    output_dir: str,
    compounds: List[str] = None,
    reverse: bool = False,
    save: bool = True,
) -> pd.DataFrame:
    """
    Analyze Florida lab results.

    Args:
        cache_path (str): The path to the cache file.
        pdf_dir (str): The directory where the PDFs are stored.
        output_dir (str): The directory where the datasets are saved.
        compounds (List[str]): The list of compounds to analyze.
        reverse (bool): Whether to reverse the order of the results.
        save (bool): Whether to save the results to a file.

    Returns:
        pd.DataFrame: The analyzed results.
    """
    # Initialize cache.
    cache = Bogart(cache_path)

    # Get all of the PDFs.
    pdfs = get_pdf_files(pdf_dir)

    # Sort the PDFs by modified date
    pdfs.sort(key=os.path.getmtime)

    # Parse the PDFs.
    all_results = parse_coa_pdfs(pdfs, cache=cache, reverse=reverse)

    # Fill missing state.
    STATE = 'FL'
    all_results = pd.DataFrame(all_results)
    all_results['lab_state'] = all_results['lab_state'].fillna(STATE)
    all_results['producer_state'] = all_results['producer_state'].fillna(STATE)

    # Save all of the data.
    date = datetime.now().strftime('%Y-%m-%d')
    outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
    all_results.replace(r'\\u0000', '', regex=True, inplace=True)
    save_with_copyright(
        all_results,
        outfile,
        dataset_name='Florida Cannabis Lab Results',
        author='Keegan Skeate',
        publisher='Cannlytics',
        sources=['Kaycha Labs', 'TerpLife Labs'],
        source_urls=['https://yourcoa.com', 'https://www.terplifelabs.com'],
    )
    print('Saved %i COA data:' % len(all_results), outfile)

# === Test ===
if __name__ == '__main__':
    
    analyze_results_fl(
        cache_path = 'D://data/.cache/results-fl.jsonl',
        pdf_dir = 'D://data/florida/results/pdfs',
        output_dir = 'D://data/florida/results/datasets',
        reverse=True,
    )


#-----------------------------------------------------------------------
# Aggregate all lab results.
#-----------------------------------------------------------------------

# # Merge secondary cache.
# cache_to_merge = 'D://data/.cache/results-fl-kaycha.jsonl'
# cache.merge_caches(cache_to_merge)
# print('Merged cache:', cache_to_merge)

# # Define compounds.
# # TODO: Add pesticides, heavy metals, residual solvents, etc.
# compounds = list(terpenes.keys()) + list(cannabinoids.keys())

# # Read CA lab results.
# ca_cache_path = r"D:\data\.cache\results-ca.jsonl"
# ca_results = Bogart(ca_cache_path).to_df()
# ca_results = standardize_results(ca_results, compounds)
# ca_results['lab_state'] = ca_results['lab_state'].fillna('CA')
# ca_results['producer_state'] = ca_results['producer_state'].fillna('CA')
# print('Number of CA results:', len(ca_results))

# # Find al unique terpenes and cannabinoids and see if there are any new compounds.
# unidentified_compounds = set()
# for index, row in all_results.iterrows():
#     results = json.loads(row['results'])
#     for result in results:
#         if result.get('analysis') == 'cannabinoids' or result.get('analysis') == 'terpenes':
#             unidentified_compounds.add(result['key'])
# unidentified_compounds = unidentified_compounds - set(cannabinoids + terpenes)
# print('Unidentified compounds:', len(unidentified_compounds))

# # Fill missing state.
# STATE = 'FL'
# all_results = pd.DataFrame(all_results)
# all_results['lab_state'] = all_results['lab_state'].fillna(STATE)
# all_results['producer_state'] = all_results['producer_state'].fillna(STATE)

# # Save all of the data.
# date = datetime.now().strftime('%Y-%m-%d')
# outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
# all_results.replace(r'\\u0000', '', regex=True, inplace=True)
# save_with_copyright(
#     all_results,
#     outfile,
#     dataset_name='Florida Cannabis Lab Results',
#     author='Keegan Skeate',
#     publisher='Cannlytics',
#     sources=['Kaycha Labs', 'TerpLife Labs'],
#     source_urls=['https://yourcoa.com', 'https://www.terplifelabs.com'],
# )
# print('Saved %i COA data:' % len(all_results), outfile)


#-----------------------------------------------------------------------
# Calculate statistics.
#-----------------------------------------------------------------------

# TODO: Ensure totals are calculated:
# - total_cannabinoids
# - total_thc
# - total_cbd
# - total_terpenes

# TODO: Augment interesting statistics:
# - thc_to_cbd_ratio
# - beta_pinene_to_d_limonene_ratio
# - monoterpene_to_sesquiterpene_ratio

# TODO: Calculate averages, medians, standard deviations, and percentiles
# for cannabinoids and terpenes.
# Time series:
# - daily
# - weekly
# - monthly
# - quarterly
# - yearly


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
