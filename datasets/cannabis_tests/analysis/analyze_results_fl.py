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
from cannlytics.data.coas import CoADoc
import pandas as pd
import os
from pathlib import Path


#-----------------------------------------------------------------------
# Parse all FL COAs.
#-----------------------------------------------------------------------

data_dirs = [
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0022",
    r"D:\data\florida\lab_results\.datasets\pdfs\moderncanna",
    r"D:\data\florida\lab_results\.datasets\pdfs\mtl",
    r"D:\data\florida\lab_results\.datasets\pdfs\terplife",
    r"D:\data\florida\lab_results\.datasets\pdfs\acs",
    r"D:\data\florida\lab_results\.datasets\pdfs\green-scientific-labs",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2015-0001",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2015-0002",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2015-0003",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2015-0004",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2015-0005",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2016-0006",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2016-0007",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0008",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0009",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0010",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0011",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0012",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2017-0013",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2018-0014",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0015",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0016",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0017",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0018",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0019",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0020",
    r"D:\data\florida\lab_results\.datasets\pdfs\MMTC-2019-0021",
    r"D:\data\florida\lab_results\fl-medical-trees",
    r"D:\data\florida\lab_results\jungleboys\pdfs",
]


# Find all of the parsed and failed PDFs.
parsed_files, failed_files = [], []
logs_files = [
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-1.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-2.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-3.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-5.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-6.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-7.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-8.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-9.txt",
    r"C:\Users\keega\OneDrive\Cannlytics\archive\2024-03\parsing-fl-coas-logs-interactive-10.txt",
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
            # Skip already parsed or failed files.
            if filename.endswith('.pdf'):
                file_path = os.path.join(root, filename)
                # if file_path in parsed_files:
                #     continue
                if file_path in failed_files:
                    continue
                file_size = os.path.getsize(file_path)
                if file_size >= min_file_size:
                    pdfs.append(file_path)

# Define where data should live,
output_dir = 'D://data/florida/lab_results/datasets'

# Parse each COA.
parser = CoADoc()
all_data = []
print(f'Parsing {len(pdfs)} COAs...')
for i, doc in enumerate(reversed(pdfs[4000:])):
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
    if i % 250 == 0 and i > 0:
        all_results = pd.DataFrame(all_data)
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
        outfile = os.path.join(output_dir, f'fl-results-{timestamp}.xlsx')
        all_results.to_excel(outfile, index=False)
        print(f'Saved {len(all_results)} parsed COAs: {outfile}')

# Save all of the data.
date = datetime.now().strftime('%Y-%m-%d')
outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
df = pd.DataFrame(all_data)
df.replace(r'\\u0000', '', regex=True, inplace=True)
parser.save(df, outfile)
print('Saved COA data:', outfile)


#-----------------------------------------------------------------------
# Read all lab results.
#-----------------------------------------------------------------------

import os
import pandas as pd


# Aggregate lab results.
data_dir = "D://data/florida/lab_results/datasets"
datafiles = os.listdir(data_dir)
datafiles = [os.path.join(data_dir, x) for x in datafiles if x.endswith('.xlsx')]
datafiles = [x for x in datafiles if 'all' not in x and '2024-01-26' not in x]
print('Number of datafiles:', len(datafiles))
all_results = []
for datafile in datafiles:
    print('Reading:', datafile)
    data = pd.read_excel(datafile)
    all_results.append(data)
all_results = pd.concat(all_results)
all_results.drop_duplicates(subset=['sample_id', 'results_hash'], inplace=True)
all_results = all_results.loc[all_results['results'] != '[]']
print('Number of results:', len(all_results))

# Save the results.
date = pd.Timestamp.now().strftime('%Y-%m-%d')
outfile = os.path.join(data_dir, f'all-fl-results-{date}.xlsx')
all_results.to_excel(outfile, index=False)
print('Saved aggregate Florida lab results:', outfile)



#-----------------------------------------------------------------------
# Parse ACS labs COAs.
#-----------------------------------------------------------------------

# # Initialize CoADoc.
# parser = CoADoc()

# # Specify where your ACS Labs COAs live.
# all_data = []
# data_dir = 'D://data/florida/lab_results/.datasets/pdfs/acs'
# coa_pdfs = os.listdir(data_dir)
# for coa_pdf in coa_pdfs:
#     filename = os.path.join(data_dir, coa_pdf)
#     try:
#         data = parser.parse(filename)
#         all_data.extend(data)
#         print('Parsed:', filename)
#     except Exception as e:
#         print('Failed to parse:', filename)

# # Save the data.
# date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
# outfile = f'D://data/florida/lab_results/.datasets/acs-lab-results-{date}.xlsx'
# df = pd.DataFrame(all_data)
# # FIXME: Make this replacement as the data is being parsed.
# df.replace(r'\\u0000', '', regex=True, inplace=True)
# parser.save(df, outfile)
# print('Saved COA data:', outfile)


#-----------------------------------------------------------------------
# Parse COAs from QR codes, images, and product labels.
#-----------------------------------------------------------------------

# TODO:
# coa_images_dir = ''
# labels_dir = ''
# qr_codes_dir = ''

# import os
# import requests

# # List of URLs
# urls = [
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRTI3OV8yNDEyNzAwMDM4MjU0NzZfMDMwOTIwMjNfNjQwYTcyMTFmMTAyMA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRDk5MV81NzEwNjAwMDM3MTk4MzRfMDMwNjIwMjNfNjQwNjgyN2Y2ZjU4Mg==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDc5N18zMjE1NjAwMDM5ODYxMzZfMDQxMDIwMjNfNjQzNDlhNTJlMmRlYg==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTk5MF8yOTM1MzAwMDM5NDA2MjBfMDQyMTIwMjNfNjQ0MmFhNTJlYjcxMw==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjM5MV8yOTUyNzAwMDQxMzQ3ODZfMDQyNTIwMjNfNjQ0ODFlOTQ1NDBlNQ==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRjg3MV80OTQ0NzAwMDQwNDgxODVfMDMyMzIwMjNfNjQxY2FmNTllYjcxMA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQTU4NF81NTMxMjAwMDM3ODAxNTBfMDEzMDIwMjNfNjNkODZjNGI2MzQxZQ==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDSDEyMl8yNjU4LTE1OTQtNjk5NC0yNjg5XzEyMjgyMDIxXzYxY2I1MDA1M2YxZjk=",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjQ4OF81NTMwMDAwMDI4OTQ2MzNfMDIxMDIwMjNfNjNlNmM3N2Y1OWJjYw==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjE5OV8xODM2MTAwMDM3MDUzNzVfMDIwODIwMjNfNjNlM2M5ZmMyMzY4ZQ==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzAwOS1ETFItNDEtU1RQQS1MUkM1LTA1MDEyMDIz",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEWjQ5Ny0xMjE0MjItOTlQUi1SMzUtMDEyMTIwMjM=",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzI3Ny1JRDI0Mi1MUi1RU0ZHLUxSNS0wNTAzMjAyMw==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjU1Ml81NTc3MzAwMDQwOTUwNzJfMDQyODIwMjNfNjQ0YzFmNjc4YjM3Mg==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDkxMS0wMzA2MjMtREJTRC1TSC1TRzM1LTA0MTAyMDIz",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEUTY3MV80OTQ0NzAwMDM0NDUwMTlfMTEwMTIwMjJfNjM2MWM3Y2Q5MGM3MA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzc4M180OTQ0NzAwMDM4NzY5MzZfMDUwOTIwMjNfNjQ1YTUwNWE2OTFmNA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDWjkxNl8xODM2MzAwMDI0NDc4NzlSMl8wNjI3MjAyMl82MmI5Y2E4YTI5YmI3",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzcwM180OTQ0ODAwMDQxMzYyNjhfMDUwODIwMjNfNjQ1OTVkNjgxMzExZA==",
#     "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQzc0OS0wMTA1MjMtU0dMQzEyLVIzNS0wMjIxMjAyMw==",
#     "https://salve-platform-production-pub-1.s3.amazonaws.com/10877/DA30425010-002-%28Original%29-%281%29.pdf",
#     "https://salve-platform-production-pub-1.s3.amazonaws.com/11319/DA30512010-006-%28Original%29.pdf",
#     "https://salve-platform-production-pub-1.s3.amazonaws.com/11432/DA30518009-001-%28Original%29.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30412005-002-Revision-2-1.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30330009-005-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/05/DA30429001-005-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30411005-004-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30309007-004-Original-1.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30225012-006-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/T304067-FTH-Dragon-Fruit-WF-3.5g-1-8oz.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30304005-002-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30309007-003-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30325005-007-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30223006-006-Revision-1.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30316004-009-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30316005-002-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30311007-004-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2022/01/DA11229005-002.pdf",
#     "https://getfluent.com/wp-content/uploads/2022/01/DA20104001-010.pdf",
#     "https://getfluent.com/wp-content/uploads/2022/01/Super-Jack-WF-3.5-g.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30407004-006-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/03/DA30314003-001-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30402002-002-Original.pdf",
#     "https://getfluent.com/wp-content/uploads/2023/04/DA30406008-001-Original.pdf",
#     "https://jungleboysflorida.com/wp-content/uploads/2023/04/Puro-Loco-Prem-Fl-02156-DA30415006-009-marketing.pdf",
#     "https://jungleboysflorida.com/wp-content/uploads/2023/04/Frozen-Grapes-Prem-Flower-02058-DA30414007-001-marketing.pdf",
#     "https://yourcoa.com/coa/coa-download?sample=DA20708002-010",
#     "https://yourcoa.com/coa/coa-download?sample=DA30314006-007-mrk",
#     "https://www.trulieve.com/files/lab-results/35603_0001748379.pdf",
# ]

# # Folder where you want to save the files
# download_folder = r"../../../.datasets/coas/fl-coas"

# # Ensure the folder exists, if not create it
# if not os.path.exists(download_folder):
#     os.makedirs(download_folder)

# # Download files
# for url in urls:
#     filename = os.path.join(download_folder, url.split("/")[-1].split('?salt=')[-1])
#     if not filename.endswith('.pdf'):
#         filename = filename + '.pdf'
#     if os.path.exists(filename):
#         continue
#     else:
#         print("Downloading:", url)
#     response = requests.get(url, stream=True)
#     with open(filename, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=8192):
#             file.write(chunk)

# print('Downloaded %i COA URLs.' % len(urls))



# TODO: Aggregate (parse if needed) TerpLife Labs COA PDFs.


#-----------------------------------------------------------------------
# Aggregate all parsed COAs.
#-----------------------------------------------------------------------

def parse_results_kaycha(
        parser,
        data_dir: str,
        outfile: Optional[str] = None,
        temp_path: Optional[str] = None,
        reverse: Optional[bool] = True,
        completed: Optional[list] = [],
        license_number: Optional[str] = None,
    ):
    """Parse lab results from Kaycha Labs COAs."""
    # Create the output data directory if it does not exist.
    if outfile:
        output_dir = os.path.dirname(outfile)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # Get a temporary path for storing images.
    if temp_path is None:
        temp_path = tempfile.gettempdir()

    # Iterate over PDF directory.
    all_data = []
    for path, _, files in os.walk(data_dir):
        if reverse:
            files = reversed(files)

        # Iterate over all files.
        for filename in list(iter(files)):

            # Skip all files except PDFs.
            if not filename.endswith('.pdf'):
                continue

            # Skip parsed files.
            if filename in completed:
                continue

            # Parse COA PDFs one by one.
            try:
                doc = os.path.join(path, filename)
                data = parser.parse(doc, temp_path=temp_path)
                if license_number is not None:
                    data['license_number'] = license_number
                all_data.extend(data)
                print('Parsed:', doc)
            except:
                print('Error:', doc)

    # Save the data.
    if outfile:
        try:
            parser.save(all_data, outfile)
            print('Saved COA data:', outfile)
        except:
            print('Failed to save COA data.')

    # Return the data.
    return all_data

# [✓] TEST: Parse Kaycha COAs.
# Note: This is a super, super long process
pdf_dir = 'D://data/florida/lab_results/.datasets/pdfs'
data_dir = 'D://data/florida/lab_results/kaycha'
date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
folders = os.listdir(pdf_dir)
folders.reverse()
parser = CoADoc()
for folder in folders:
    # if folder.startswith('MMTC'):
    data_dir = os.path.join(pdf_dir, folder)
    outfile = os.path.join(data_dir, '.datasets', f'{folder}-lab-results-{date}.xlsx')
    print('Parsing:', folder)
    coa_data = parse_results_kaycha(
        parser,
        data_dir,
        outfile,
        reverse=True,
        completed=[],
        license_number=folder,
    )
    
    # Lab result constants.
    CONSTANTS = {
        'lims': 'Kaycha Labs',
        'lab': 'Kaycha Labs',
        'lab_image_url': 'https://www.kaychalabs.com/wp-content/uploads/2020/06/newlogo-2.png',
        'lab_address': '4101 SW 47th Ave, Suite 105, Davie, FL 33314',
        'lab_street': '4101 SW 47th Ave, Suite 105',
        'lab_city': 'Davie',
        'lab_county': 'Broward',
        'lab_state': 'FL',
        'lab_zipcode': '33314',
        'lab_phone': '833-465-8378',
        'lab_email': 'info@kaychalabs.com',
        'lab_website': 'https://www.kaychalabs.com/',
        'lab_latitude': 26.071350,
        'lab_longitude': -80.210750,
        'licensing_authority_id': 'OMMU',
        'licensing_authority': 'Florida Office of Medical Marijuana Use',
    }

    # Specify where your ACS Labs COAs live.
    folder_path = 'D://data/florida/lab_results/.datasets/'

    # Aggregate all of the parsed COAs.
    data_frames = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_excel(file_path, sheet_name='Details')
                data_frames.append(df)
                print('Compiled %i results:' % len(df), filename)
            except:
                continue

    # Sort by when the COA was parsed and keep only the most recent by sample ID.
    aggregate = pd.concat(data_frames, ignore_index=True)
    aggregate.sort_values('coa_parsed_at', ascending=False, inplace=True)
    aggregate.drop_duplicates(subset='sample_id', keep='first', inplace=True)
    print('Aggregated %i COAs.' % len(aggregate))

    # # FIXME: Standardize the data.
    # for constant, value in CONSTANTS.items():
    #     aggregate[constant] = value

    # FIXME: Augment license data.
    import sys
    sys.path.append('./datasets')
    sys.path.append('../../../datasets')
    from cannabis_licenses.algorithms.get_licenses_fl import get_licenses_fl
    licenses = get_licenses_fl()
    licenses['license_type'] = 'Medical - Retailer'
    data = pd.merge(
        aggregate,
        licenses,
        suffixes=['', '_copy'],
        left_on='producer_license_number',
        right_on='license_number',
    )
    data = data.filter(regex='^(?!.*_copy$)')

    # Save the results.
    parser = CoADoc()
    date = datetime.now().strftime('%Y-%m-%d')
    outfile = f'D://data/florida/lab_results/.datasets/fl-lab-results-{date}.xlsx'
    parser.save(data, outfile)
    print('Saved aggregated COAs data:', outfile)

    # TODO: Merge with unparsed COA URLs.
    


#-----------------------------------------------------------------------
# Aggregate all lab results.
#-----------------------------------------------------------------------

import pandas as pd


FL_LAB_RESULTS = {
    'acs': {
        'datafiles': [
            r"D:\data\florida\lab_results\.datasets\acs-lab-results-2023-12-27-08-30-49.xlsx",
        ]
    },
    'kaycha': {
        'datafiles': [
            r"D:\data\florida\lab_results\.datasets\fl-lab-results-2023-06-07T06-20-43.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0020-lab-results-2023-09-21-20-26-18.xlsx",
            r"D:\data\florida\lab_results\.datasets\green-scientific-labs-lab-results-2023-06-06T11-38-34.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0001-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0001-lab-results-2023-06-04T06-49-10.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0001-lab-results-2023-06-04T23-17-02.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0001-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0001-lab-results-2023-09-11-19-09-20.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-04T23-17-49.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-07-19-14-34.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-07-19-14-50.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-07-19-14-58.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-07-19-15-08.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-07-19-15-13.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-06-08-06-21-23.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0002-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0003-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0003-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0004-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2015-0004-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2016-0007-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2016-0007-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2016-0007-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0008-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0008-lab-results-2023-06-04T06-48-27.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0008-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0009-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0009-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0009-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0010-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0010-lab-results-2023-06-04T23-16-29.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0010-lab-results-2023-09-11-19-09-20.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0010-lab-results-2023-09-21-20-26-18.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0011-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2017-0011-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0015-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0015-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0017-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0017-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0019-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0019-lab-results-2023-08-29-21-04-30.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0019-lab-results-2023-09-11-16-14-09.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0020-lab-results-2023-06-03.xlsx",
            r"D:\data\florida\lab_results\.datasets\MMTC-2019-0020-lab-results-2023-09-11-19-09-20.xlsx",
        ]
    },
    'terplife': {
        'datafiles': [
            r"D:\data\florida\lab_results\.datasets\fl-lab-results-2024-01-24.xlsx",
        ]
    },
}


# Read all datafiles.
all_results = []
for source in FL_LAB_RESULTS:
    for datafile in FL_LAB_RESULTS[source]['datafiles']:
        try:
            data = pd.read_excel(datafile)
        except:
            print('Error reading:', datafile)
            continue
        all_results.append(data)

# Aggregate results, removing lab results that are being processed (no results).
results = pd.concat(all_results)
print('Number of results before dropping in-progress:', len(results))
results = results.loc[results['results'] != "[]"]
print('Number of results before dropping duplicates:', len(results))
results.drop_duplicates(subset=['sample_id'], inplace=True)
print('Number of results:', len(results))

# Save the data.
date = pd.to_datetime('today').strftime('%Y-%m-%d')
outfile = f"D://data/florida/lab_results/datasets/fl-results-{date}.csv"
results.to_csv(outfile, index=False)
print('Saved:', outfile)
