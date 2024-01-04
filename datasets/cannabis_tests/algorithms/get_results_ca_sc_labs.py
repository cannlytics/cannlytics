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
        days: int = 31,
        max_samples: int = 199,
        prefix: Optional[str] = 'P',
        pause: float = 3.33,
        verbose: bool = True,
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
    # TODO: Allow for starting at the end of the month and going backwards.
    start_date = datetime(year, month, 1)
    end_date = (start_date + timedelta(days=days)).replace(day=1)
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


# Get all valid URLS, iterating over prefixes, years, and months.
prefixes = [
    # 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'O',
    # 'J', 'K', 'L', 'M', 'N', 'P',
    # 'Q', 'R', 'S', 'T',
    'U',
    # 'V', 'W', 'X', 'Y', 'Z',
    ]
docs = []
for y in reversed(range(2019, 2025)):
    for m in reversed(range(1, 13)):

        # DEV: Restrict to desired timeframe.
        # if y == 2023 and m < 12:
        #     continue
        if y == 2024 and m > 1:
            continue
        if y == 2024:
            days = 3
        else:
            days = 31

        for prefix in prefixes:
            print(f'=== {y}-{m:02d} ({prefix}) ===')
            results = get_sc_labs_results_by_month(
                prefix=prefix,
                year=y,
                month=m,
                days=days,
                pause=1.0,
            )
            docs.extend(results)

# Save the list of URLS.
DATA_DIR = 'D:/data/california/lab_results/datasets/sclabs'
timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
outfile = os.path.join(DATA_DIR, f'ca-lab-results-sclabs-urls-{timestamp}.xlsx')
pd.DataFrame(docs, columns=['url']).to_excel(outfile, index=False)
print(f'Saved URLS: {outfile}')

# # # Optional: Read the list of URLs.
# urls = []
# url_files = [
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-29-07-53-39.xlsx",
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-24-15-39-06.xlsx",
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-24-00-52-02.xlsx",
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-23-11-42-37.xlsx",
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-all.xlsx",
#     r"D:\data\california\lab_results\datasets\sclabs\ca-lab-results-sclabs-urls-2023-12-30-21-15-44.xlsx",
# ]
# for url_file in url_files:
#     url_data = pd.read_excel(url_file)
#     urls.append(url_data)
# urls = pd.concat(urls)
# urls.drop_duplicates(subset=['url'], inplace=True)
# docs = urls['url'].tolist()
# docs.reverse()

# Parse each COA.
all_data = []
errors = []
parser = CoADoc()
print(f'Parsing {len(docs)} URLs.')
for doc in docs:
    sleep(3.3)
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
# parser.save(pd.DataFrame(all_data), outfile)
pd.DataFrame(all_data).to_excel(outfile, index=False)
print(f'Saved {len(all_data)} results: {outfile}')
