"""
Get California Lab Results | SC Labs
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/30/2023
Updated: 1/15/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime, timedelta
import os
from time import sleep
from typing import Optional
from urllib.parse import urljoin

# External imports:
from bs4 import BeautifulSoup
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.data.coas import CoADoc
from cannlytics.data.coas.algorithms import sclabs
import pandas as pd
import requests


# Define the base URL for SC Labs.
BASE_URL = 'https://client.sclabs.com/verify/'


def get_sc_labs_results_by_month(
        year: int,
        month: int,
        start_day: int = 1,
        days: int = 31,
        max_samples: int = 199,
        prefix: Optional[str] = 'P',
        pause: float = 3.33,
        verbose: bool = True,
        reverse: bool = False,
    ) -> list:
    """Get SC Labs results for a given month and year.
    Args:
        year (int): The year to search.
        month (int): The month to search.
        max_samples (int): The maximum number of samples to search for each day.
    Returns:
        docs (list): A list of URLs to the COAs.
    """
    docs = []
    start_date = datetime(year, month, start_day)
    if reverse:
        end_date = (start_date - timedelta(days=days))
    else:
        end_date = (start_date + timedelta(days=days))
    print('Start date:', start_date)
    print('End date:', end_date)
    while start_date < end_date:

        # Iterate through all possible sample IDs for the day.
        for i in range(1, max_samples):
            sample_id = start_date.strftime('%y%m%d') + f'{prefix}{i:03}'
            url = urljoin(BASE_URL, sample_id + '/')
            page = requests.get(url, headers=DEFAULT_HEADERS)
            sleep(pause)
            if page.status_code != 200:
                continue

            # Check for 'Product not found' to break the loop
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                note = soup.find('p', {'class': 'errornote'}).text.strip()
            except:
                note = ''
            if note == 'Product not found.':
                if verbose:
                    print('Product not found:', url)
                break

            # Check for 'results as private' to skip the sample
            if note.endswith('the results as private.'):
                if verbose:
                    print('Private results:', url)
                continue

            # Check for 'Certificate of Analysis'
            try:
                certificate_tag = soup.find('div', {'class': 'sdp-sample-coa'})
            except:
                if verbose:
                    print('Failed to find COA:', url)
                continue
            if certificate_tag and certificate_tag.text.strip() == 'Certificate of Analysis':
                docs.append(url)
                if verbose:
                    print('Found COA:', url)

        # Move to the next day.
        start_date += timedelta(days=1)

    # Return the list of URLs.
    return docs


# Define parameters for data collection.
prefixes = [
    # Used prefixes
    'J', 'K', 'L', 'M', 'N', 'P',
    'Q', 'R', 'S', 'T', 'U',
    'W', 'V', 'X', 'Y',
    'H', 'Z',
    # Unknown if used
    # 'A', 'B', 'C', 'D', 'E', 'F', 'G',  'I', 'O',
    ]
start_day = 1
days = 7
start_year = 2024
end_year = 2024
start_month = 2
end_month = 2
pause = 3.33

# Get all valid URLS, iterating over prefixes, years, and months.
docs = []
for y in reversed(range(start_year, end_year + 1)):
    for m in reversed(range(start_month, end_month + 1)):
        for prefix in prefixes:
            print(f'=== Querying {y}-{m:02d} ({prefix}) ===')
            results = get_sc_labs_results_by_month(
                prefix=prefix,
                year=y,
                month=m,
                days=days,
                start_day=start_day,
                pause=pause,
            )
            docs.extend(results)

# Save the list of URLS.
DATA_DIR = 'D:/data/california/lab_results/datasets/sclabs'
timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
outfile = os.path.join(DATA_DIR, f'ca-lab-results-sclabs-urls-{timestamp}.xlsx')
pd.DataFrame(docs, columns=['url']).to_excel(outfile, index=False)
print(f'Saved URLS: {outfile}')


# TODO: Implement functions for aggregation.

# # Optional: Read the list of URLs.
# urls = []
# url_files = [
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-23-11-42-37.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-24-00-52-02.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-24-15-39-06.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-29-07-53-39.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-30-21-15-44.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-02-20-22-30.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-03-03-40-42.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-04-17-48-13.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-04-18-09-29.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-05-00-57-43.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-05-07-23-55.xlsx",
#     "D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2024-01-05-15-43-00.xlsx",
# ]
# for url_file in url_files:
#     url_data = pd.read_excel(url_file)
#     urls.append(url_data)
# urls = pd.concat(urls)
# urls.drop_duplicates(subset=['url'], inplace=True)
# docs = urls['url'].tolist()
# docs.reverse()

# # Read all parsed COA datafiles.
# datafiles = [
#     'D:/data/california/lab_results/datasets/sclabs/ca-lab-results-sclabs-2024-01-02-00-39-36.xlsx',
#     'D:/data/california/lab_results/datasets/sclabs/ca-lab-results-sclabs-2024-01-03-06-24-11.xlsx',
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-2024-01-05-02-17-28.xlsx",
#     r"D:/data/california/lab_results/datasets/sclabs\ca-lab-results-sclabs-2024-01-05-23-23-15.xlsx",
#     r'D:/data/california/lab_results/datasets/sclabs\ca-lab-results-sclabs-2024-01-05-18-01-26.xlsx',
#     r'D:/data/california/lab_results/datasets/sclabs\ca-lab-results-sclabs-2024-01-08-18-12-08.xlsx',
# ]
# all_results = []
# for datafile in datafiles:
#     data = pd.read_excel(datafile)
#     all_results.append(data)
# results = pd.concat(all_results)
# results.drop_duplicates(subset=['coa_id'], inplace=True)
# results['lab_result_url'] = results['coa_id'].astype(str).apply(
#     lambda x: urljoin(BASE_URL, x.split('-')[0].strip() + '/')
# )
# print('Number of results:', len(results))

# # Determine un-parsed COAs (all docs not in results['lab_result_url'] column).
# docs = list(set(docs) - set(results['lab_result_url'].tolist()))
# print('Number of un-parsed COAs:', len(docs))

# Parse each COA.
all_data = []
errors = []
parser = CoADoc()
print(f'Parsing {len(docs)} URLs.')
for doc in docs:
    sleep(1)
    try:
        coa_data = sclabs.parse_sc_labs_coa(parser, doc, verbose=True)
        all_data.append(coa_data)
        print(f'Parsed COA: {doc}')
    except Exception as e:
        errors.append(doc)
        print(f'Failed to parse COA: {doc}')
        print(e)

# Save the results.
DATA_DIR = 'D:/data/california/lab_results/datasets/sclabs'
timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
outfile = os.path.join(DATA_DIR, f'ca-lab-results-sclabs-{timestamp}.xlsx')
pd.DataFrame(all_data).to_excel(outfile, index=False)
print(f'Saved {len(all_data)} results: {outfile}')
