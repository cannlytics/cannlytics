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
import gc
import os
import tempfile
from typing import Optional

# External imports:
from cannlytics.utils.utils import hash_file
from cannlytics.data.coas import CoADoc
import pandas as pd
import os
from pathlib import Path


#-----------------------------------------------------------------------
# Parse all FL COAs.
#-----------------------------------------------------------------------

data_dirs = [
    # Labs without parsing algorithms:
    # r"D:\data\florida\lab_results\pdfs\moderncanna",
    # r"D:\data\florida\lab_results\pdfs\mtl",
    # r"D:\data\florida\lab_results\pdfs\green-scientific-labs",
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
logs_files = [
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-1.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-2.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-3.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-5.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-6.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-7.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-8.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-9.txt",
    # r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-10.txt",
]
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
min_file_size = 12_000
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
print('Number of unique COAs:', len(all_results))

# Save the results locally.
date = pd.Timestamp.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'all-fl-results-{date}.xlsx')
all_results.to_excel(outfile, index=False)
print('Saved aggregate Florida lab results:', outfile)

# TODO: Use a local cache to keep track of lab results in Firestore,
# PDFs in Google Cloud Storage, and which datafiles are in Cloud Storage.
cache_dir = 'D://data/florida/cache'

# FIXME: Upload data to Firestore.


# === Upload PDFs to Google Cloud Storage. ===

# Match COA PDFs with the results.
pdf_dir = 'D://data/florida/results/pdfs'
coa_pdfs = {}
for index, result in all_results.iterrows():

    # Walk directory to try to find the PDF.
    coa_pdf = result['coa_pdf']
    if coa_pdf == 'download.pdf':
        lab_results_url = result['lab_results_url']
        sample_id = lab_results_url.split('=')[-1].split('?')[0]
        for root, _, files in os.walk(pdf_dir):
            for filename in files:
                if sample_id in filename:
                    pdf_path = os.path.join(root, filename)
                    print('Matched %s to %s' % (result['sample_hash'], pdf_path))
                    coa_pdfs[result['sample_hash']] = pdf_path
                    break
        continue
    for root, _, files in os.walk(pdf_dir):
        for filename in files:
            if filename == coa_pdf:
                pdf_path = os.path.join(root, filename)
                print('Matched %s to %s' % (result['sample_hash'], pdf_path))
                coa_pdfs[result['sample_hash']] = pdf_path
                break

# FIXME: Upload PDFs to Google Cloud Storage.
for sample_hash, pdf_path in coa_pdfs.items():
    print('Uploading:', pdf_path)
    pdf_hash = hash_file(pdf_path)



# FIXME: Upload datafiles to Google Cloud Storage.


