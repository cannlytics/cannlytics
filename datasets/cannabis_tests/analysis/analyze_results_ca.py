"""
Analyze Results | California
Copyright (c) 2023-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2023
Updated: 6/15/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
import os
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import CoADoc, get_result_value, standardize_results
from cannlytics.data.coas.parsing import get_coa_files, parse_coa_pdfs
from cannlytics.firebase import initialize_firebase
from cannlytics.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import pandas as pd

# Internal imports:
from analyze_results import calc_results_stats, calc_aggregate_results_stats


def analyze_results_ca(
    cache_path: str,
    pdf_dir: str,
    reverse: bool = False,
) -> pd.DataFrame:
    """
    Analyze California lab results.

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

    # TODO: Remove duplicates in the PDF dir.

    # Get all of the PDFs.
    pdfs = get_coa_files(pdf_dir)

    # Sort the PDFs by modified date
    pdfs.sort(key=os.path.getmtime)

    # Parse the PDFs.
    all_results = parse_coa_pdfs(pdfs, cache=cache, reverse=reverse)

    # # Fill missing state.
    # STATE = 'CA'
    # all_results = pd.DataFrame(all_results)
    # all_results['lab_state'] = all_results['lab_state'].fillna(STATE)
    # all_results['producer_state'] = all_results['producer_state'].fillna(STATE)

    # # Standardize the results.
    # all_results = standardize_results(all_results, compounds)

    # # Save all of the parsed data.
    # if save:
    #     date = pd.Timestamp.now().strftime('%Y-%m-%d')
    #     outfile = os.path.join(output_dir, f'ca-results-{date}.xlsx')
    #     parser = CoADoc()
    #     try:
    #         parser.save(all_results, outfile)
    #     except:
    #         all_results.to_excel(outfile, index=False)
    #     print(f'Saved {len(all_results)} {STATE} results: {outfile}')

    return all_results

# === Test ===
if __name__ == '__main__':

    analyze_results_ca(
        cache_path='D://data/.cache/results-ca.jsonl',
        pdf_dir='D://data/california/results/pdfs',
        reverse=True,
    )

    # Read the cache.
    results = Bogart('D://data/.cache/results-ca.jsonl').to_df()
    print('Read %i results from cache.' % len(results))

    # TODO: Figure out why there are duplicates.

    # Drop duplicates.
    results = results.drop_duplicates(subset=['sample_hash'])
    print('Number of unique results:', len(results))

    # TODO: Identify the same COA parsed multiple ways.
    multiple_coas = results['coa_pdf'].value_counts()
    print('Multiple COAs:', multiple_coas[multiple_coas > 1])

    # FIXME: Handle:
    # - `download.pdf`
    # - `DA20618004-002.pdf`

    # TODO: Drop all non-standard columns.

    # Standardize the data.
    # TODO: Add pesticides, heavy metals, residual solvents, etc.
    state = 'CA'
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



#-----------------------------------------------------------------------
# Upload COA PDFs to Google Cloud Storage and data to Firestore.
#-----------------------------------------------------------------------

# FIXME: Refactor into re-usable functions.

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
# # FIXME:
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
#         # FIXME:
#         # cache.setdefault('datafiles', []).append(filename)

# # Upload PDFs to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# print('Number of unique COA PDFs:', len(coa_pdfs))
# for sample_hash, pdf_path in coa_pdfs.items():
#     print('Uploading:', pdf_path)
#     pdf_hash = cache.hash_file(pdf_path)

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
#         # FIXME:
#         # cache.setdefault('pdfs', []).append(pdf_hash)

# # Upload the raw data to Firestore.
# # Checks if the data has been uploaded according to the local cache.
# refs, updates = [], []
# collection = 'results'
# for _, obs in all_results.iterrows():
#     doc_id = obs['sample_hash']
#     if doc_id not in cache.get('results', []):
#         refs.append(f'{collection}/{doc_id}')
#         updates.append(obs.to_dict())
#         # FIXME:
#         # cache.setdefault('results', []).append(doc_id)
# # if refs:
# #     update_documents(refs, updates, database=db)
# #     print('Uploaded %i results to Firestore.' % len(refs))

# # TODO: Save the statistics to Firestore.

# # Save the updated cache
# # with open(cache_file, 'w') as f:
# #     json.dump(cache, f)
# #     print('Saved cache:', cache_file)
