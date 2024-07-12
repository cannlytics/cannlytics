"""
Get Results | Utah
Copyright (c) 2023-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/4/2024
Updated: 7/10/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
import os
from typing import List, Optional
from zipfile import ZipFile

# External imports:
from cannlytics import __version__
from cannlytics.data.cache import Bogart
from cannlytics.data.coas.parsing import get_coa_files
from cannlytics.data.coas import CoADoc
from cannlytics.data.coas.algorithms.utah import parse_utah_coa
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import find_unique_analytes
import pandas as pd

def unzip_folder(folder, destination, remove=True):
    """Unzip a folder.
    Args:
        pdf_dir (str): The directory where the folder is stored.
        folder (str): The name of the folder to unzip.
    """
    os.makedirs(destination, exist_ok=True)
    with ZipFile(folder) as zip_ref:
        zip_ref.extractall(destination)
    if remove:
        os.remove(folder)

def parse_coa_pdfs(
        pdfs,
        algorithm=None,
        parser=None,
        cache=None,
        data=None,
        verbose=True,
    ) -> List[dict]:
    """Parse a list of COA PDFs.
    Args:
        pdfs (List[str]): A list of PDFs to parse.
        algorithm (function): The parsing algorithm to use.
        parser (object): The parser object to use.
        cache (object): The cache object to use.
        data (List[dict]): The data to append to.
        verbose (bool): Whether to print verbose output.
    Returns:
        List[dict]: The parsed data.
    """
    if data is None:
        data = []
    if parser is None:
        parser = CoADoc()
    for pdf in pdfs:
        if not os.path.exists(pdf):
            if verbose: print(f'PDF not found: {pdf}')
            continue
        if cache is not None:
            pdf_hash = cache.hash_file(pdf)
            if cache is not None:
                if cache.get(pdf_hash):
                    if verbose: print('Cached:', pdf)
                    data.append(cache.get(pdf_hash))
                    continue
        try:
            if algorithm is not None:
                coa_data = algorithm(parser, pdf)
            else:
                coa_data = parser.parse(pdf)
            data.append(coa_data)
            if cache is not None:
                cache.set(pdf_hash, coa_data)
            print('Parsed:', pdf)
        except:
            print('Error:', pdf)
    return data

def get_results_ut(
        data_dir: str,
        pdf_dir: str,
        cache_path: Optional[str] = None,
        clear_cache: Optional[bool] = False,
    ) -> pd.DataFrame:
    """Get lab results for Utah."""

    # Unzip all of the folders.
    folders = [os.path.join(pdf_dir, x) for x in os.listdir(pdf_dir) if x.endswith('.zip')]
    for folder in folders:
        unzip_folder(folder, pdf_dir)
        print('Unzipped:', folder)

    # Get all of the PDFs.
    pdfs = get_coa_files(pdf_dir)
    pdfs.sort(key=os.path.getmtime)
    print('Found %i PDFs.' % len(pdfs))

    # Initialize COA parsing.
    cache = Bogart(cache_path)

    # DEV: Clear the cache.
    if clear_cache:
        cache.clear()

    # Parse COAs.
    parse_coa_pdfs(
        pdfs,
        algorithm=parse_utah_coa,
        cache=cache,
    )

    # Read results.
    results = cache.to_df()
    print('Number of results:', len(results))

    # Standardize time.
    results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
    results['week'] = results['date'].dt.to_period('W').astype(str)
    results['month'] = results['date'].dt.to_period('M').astype(str)
    results = results.sort_values('date')

    # Standardize compounds.
    # Note: Removes nuisance analytes.
    analytes = find_unique_analytes(results)
    nuisance_analytes = [
        'det_detected',
        'global_shortages_of_laboratory_suppliesto',
        'here_recorded_may_not_be_used_as_an_endorsement_for_a_product',
        'information_see',
        'information_see_https_totoag_utah_govto_2021_to_04_to_29_toudaf_temporarily_adjusts_medical_cannabis_testing_protocols_due_to',
        'nd_not_detected',
        'notes',
        'notes_sample_was_tested_as_received_the_cannabinoid_results_were_not_adjusted_for_moisture_content',
        'phtatpthso_togtoaegn_utetashti_nggo_vwto_2_a_0_s',
        'recorded_the_results_here_recorded_may_not_be_used_as_an_endorsement_for_a_product',
        'results_pertain_only_to_the_test_sample_listed_in_this_report',
        'see_https_totoag_utah_govto_2021_to_04_to_29_toudaf_temporarily_adjusts_medical_cannabis_testing_protocols_due_to_global',
        'shortages_of_laboratory_suppliesto',
        'tac_2500000',
        'tac_t',
        'this_report_may_not_be_reproduced_except_in_its_entirety',
        'total_cbd',
        'total_thc',
    ]
    analytes = analytes - set(nuisance_analytes)
    analytes = sorted(list(analytes))
    results = standardize_results(results, analytes)

    # Save the results.
    outfile = os.path.join(data_dir, 'ut-results-latest.xlsx')
    outfile_csv = os.path.join(data_dir, 'ut-results-latest.csv')
    outfile_json = os.path.join(data_dir, 'ut-results-latest.jsonl')
    results.to_excel(outfile, index=False)
    results.to_csv(outfile_csv, index=False)
    results.to_json(outfile_json, orient='records', lines=True)
    print('Saved Excel:', outfile)
    print('Saved CSV:', outfile_csv)
    print('Saved JSON:', outfile_json)

    # Print out features.
    features = {x: 'string' for x in results.columns}
    print('Number of features:', len(features))
    print('Features:', features)

    # Return the results.
    return results

# === Tests ===
# [✓] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    # Define where the data lives.
    data_dir = 'D://data/utah'
    pdf_dir = 'D://data/public-records/Utah'
    cache_path = 'D://data/.cache/results-ut.jsonl'

    # Curate results.
    results = get_results_ut(
        data_dir=data_dir,
        pdf_dir=pdf_dir,
        cache_path=cache_path,
        clear_cache=True
    )
