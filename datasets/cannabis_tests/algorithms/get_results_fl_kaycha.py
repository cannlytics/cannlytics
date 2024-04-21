"""
Get Florida cannabis lab results | Kaycha Labs
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 4/20/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data for Kaycha Labs.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)
    - [Kaycha Labs](https://yourcoa.com)

"""
# Standard imports:
from datetime import datetime
import hashlib
import json
import os
import random
import string
import tempfile
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.web import initialize_selenium
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd
import requests

# Selenium imports.
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Get a list of Florida companies.
# Note: It may be best to retrieve this list dynamically.
# TODO: Keep track of the last page of results for each company.
# TODO: Try to find COAs for the remaining companies.
# - Plant 13 Florida, Inc.
# - House of Platinum Cannabis
# - Cookies Florida, Inc.
FLORIDA_LICENSES = {
    'MMTC-2015-0002': {
        'business_dba_name': 'Ayr Cannabis Dispensary',
        'business_legal_name': 'Liberty Health Sciences, FL',
        'slug': 'Liberty+Health+Sciences%2C+FL',
    },
    'MMTC-2017-0011': {
        'business_dba_name': 'Cannabist',
        'slug': 'Cannabist',
    },
    'MMTC-2019-0018': {
        'business_dba_name': 'Cookies Florida, Inc.',
        'slug': '',
    },
    'MMTC-2015-0001': {
        'business_dba_name': 'Curaleaf',
        'slug': 'CURALEAF+FLORIDA+LLC',
    },
    'MMTC-2015-0003': {
        'business_dba_name': 'Fluent ',
        'slug': 'Fluent',
    },
    'MMTC-2019-0019': {
        'business_dba_name': 'Gold Leaf',
        'slug': 'Gold+Leaf',
    },
    'MMTC-2019-0021': {
        'business_dba_name': 'Green Dragon',
        'slug': 'Green+Dragon',
    },
    'MMTC-2016-0007': {
        'business_dba_name': 'GrowHealthy',
        'slug': 'GrowHealthy',
    },
    'MMTC-2017-0013': {
        'business_dba_name': 'GTI (Rise Dispensaries)',
        'slug': 'GTI',
    },
    'MMTC-2018-0014': {
        'business_dba_name': 'House of Platinum Cannabis',
        'slug': '',
    },
    'MMTC-2019-0016': {
        'business_dba_name': 'Insa - Cannabis for Real Life',
        'slug': 'Insa',
    },
    'MMTC-2019-0015': {
        'business_dba_name': 'Jungle Boys',
        'slug': 'Jungle+Boys',
    },
    'MMTC-2017-0010': {
        'business_dba_name': 'MüV',
        'slug': 'Altmed+Florida',
    },
    'MMTC-2016-0006': {
        'business_dba_name': 'Planet 13 Florida, Inc.',
        'slug': '',
    },
    'MMTC-2019-0022': {
        'business_dba_name': 'Revolution Florida',
        'slug': 'Revolution',
    },
    'MMTC-2019-0017': {
        'business_dba_name': 'Sanctuary Cannabis',
        'slug': 'Sanctuary',
    },
    'MMTC-2017-0012': {
        'business_dba_name': 'Sunburn',
        'slug': '',
    },
    'MMTC-2017-0008': {
        'business_dba_name': 'Sunnyside*',
        'slug': 'Sunnyside',
    },
    'MMTC-2015-0004': {
        'business_dba_name': 'Surterra Wellness',
        'slug': 'Surterra+Wellness',
    },
    'MMTC-2019-0020': {
        'business_dba_name': 'The Flowery',
        'slug': 'The+Flowery',
    },
    'MMTC-2015-0005': {
        'business_dba_name': 'Trulieve',
        'slug': 'Trulieve',
    },
    'MMTC-2017-0009': {
        'business_dba_name': 'VidaCann',
        'slug': 'VidaCann',
    },
}


def download_pdf_with_selenium(
        url,
        driver=None,
        persist=False,
        pause=3.33,
        wait=10,
        el_id='download',
        method='iframe',
        tag_name='iframe',
        filename=None,
        download_dir=None,
        headless=True,
    ):
    if driver is None:
        driver = initialize_selenium(
            headless=headless,
            download_dir=download_dir,
        )
    driver.get(url)
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name))
    )
    if method == 'iframe':
        driver.switch_to.frame(el)
        download_button = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.ID, el_id))
        )
        download_button.click()
    else:
        pdf_url = el.get_attribute('href')
        response = requests.get(pdf_url)
        if response.status_code == 200:
            if filename is None:
                filename = os.path.basename(pdf_url)
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as file:
                file.write(response.content)
    sleep(pause)
    if not persist:
        driver.quit()


def hash_file(filepath, size=65536):
    """Generate a SHA-1 hash for a file."""
    hasher = hashlib.sha1()
    with open(filepath, 'rb') as f:
        buf = f.read(size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()


def remove_duplicate_files(directory):
    """Remove duplicate PDFs from a directory."""
    hashes = {}
    files_removed = 0
    total_files = 0
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            total_files += 1
            filepath = os.path.join(directory, filename)
            file_hash = hash_file(filepath)
            
            # Check if hash already exists in the dictionary
            if file_hash in hashes:
                os.remove(filepath)
                files_removed += 1
                print(f"Removed duplicate file: {filepath}")
            else:
                hashes[file_hash] = filepath
    print(f"Total files scanned: {total_files}, duplicates removed: {files_removed}")


def download_coas_kaycha(
        data_dir: str,
        slug: str,
        dba: Optional[str] = None,
        producer_license_number: Optional[str] = None,
        overwrite: Optional[bool] = False,
        base: Optional[str] = 'https://yourcoa.com',
        columns: Optional[list] = None,
    ):
    """Download Kaycha Labs COAs uploaded to the public web."""

    # Initialize COA URL collection.
    if columns is None:
        columns = ['lab_id', 'batch_number', 'product_name']

    # Create an output directory.
    datasets_dir = os.path.join(data_dir, 'datasets')
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    # Request each page until the maximum is reached.
    page = 0
    observations = []
    iterate = True
    while iterate:

        # Get the first/next page of COAs.
        page += 1
        url = f'{base}/company/company?t={slug}&page={page}'
        response = requests.get(url, headers=DEFAULT_HEADERS)
        if response.status_code != 200:
            print(f'Request failed with status {response.status_code}')

        # Get the download URLs.
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        links = [x['href'] for x in links if 'coa-download' in x['href']]
        links = list(set(links))
        links = [base + x for x in links]

        # Get the details from the page.
        divs = soup.find_all(class_='pdf_box')
        print('Found %i samples on page %i.' % (len(divs), page))
        for n, div in enumerate(divs):
            observation = {}
            spans = div.find_all('span')[:len(columns)]
            values = [x.text for x in spans]
            for k, value in enumerate(values):
                observation[columns[k]] = value
            try:
                observation['download_url'] = links[n]
            except:
                continue
            if dba is not None:
                observation['business_dba_name'] = dba
            if producer_license_number is not None:
                observation['producer_license_number'] = producer_license_number
            observations.append(observation)

        # See if the next button is disabled to know when to stop iterating.
        next_element = soup.find(class_='next')
        if not next_element:
            iterate = False
        elif next_element and 'disabled' in next_element.get('class', []):
            iterate = False

        # Otherwise pause to respect the server.
        sleep(0.3)

    # Save the observed lab result URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    df = pd.DataFrame(observations)
    df.to_excel(f'{datasets_dir}/fl-lab-result-urls-{slug}-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for %s' % (len(df), slug))

    # Create a directory for COA PDFs.
    pdf_dir = os.path.join(datasets_dir, 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Create a directory for each licensees COAs.
    license_pdf_dir = os.path.join(pdf_dir, producer_license_number)
    if not os.path.exists(license_pdf_dir):
        os.makedirs(license_pdf_dir)

    # Download the PDFs.
    print('License directory:', license_pdf_dir)
    for _, row in df.iterrows():
        sleep(0.3)
        download_url = row['download_url']
        if not download_url.startswith('http'):
            download_url = base + download_url
        sample_id = download_url.split('/')[-1]
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            print('Cached:', download_url)
            continue
        try:
            coa_url = f'{base}/coa/download?sample={sample_id}'
            response = requests.get(coa_url, headers=DEFAULT_HEADERS)
            if response.status_code == 200:
                with open(outfile, 'wb') as pdf:
                    pdf.write(response.content)
                print('Downloaded:', coa_url)
                # FIXME: Check if the file size is small,
                # then retry with Selenium if so.
        except:
            coa_url = f'{base}/coa/coa-view?sample={sample_id}'
            response = requests.get(coa_url, allow_redirects=True)
            if response.status_code == 200:
                redirected_url = response.url
                download_pdf_with_selenium(
                    redirected_url,
                    download_dir=license_pdf_dir,
                )
                print('Downloaded:', coa_url)

    # Return the COA URLs.
    return df


def get_results_kaycha(data_dir: str, licenses=None, **kwargs):
    """Get lab results published by Kaycha Labs on the public web."""

    # Sort licenses by the number of COAs.
    if licenses is None:
        licenses = FLORIDA_LICENSES
    licenses = dict(sorted(licenses.items(), key=lambda x: x[1]['total']))

    # Iterate over each producer.
    coa_urls = []
    for producer_license_number, licensee in licenses.items():
        # expected_total = licensee['total']
        # if expected_total == 0:
        #     continue
        print('Preparing to download COAs for %s' % licensee['business_dba_name'])
        urls = download_coas_kaycha(
            data_dir,
            slug=licensee['slug'],
            dba=licensee['business_dba_name'],
            producer_license_number=producer_license_number,
        )
        coa_urls.append(urls)

        # Remove duplicate COAs.
        datasets_dir = os.path.join(data_dir, 'datasets')
        pdf_dir = os.path.join(datasets_dir, 'pdfs')
        license_pdf_dir = os.path.join(pdf_dir, producer_license_number)
        remove_duplicate_files(license_pdf_dir)

    # Save and return all of the COA URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    data = pd.concat(coa_urls)
    datasets_dir = os.path.join(data_dir, '.datasets')
    data.to_excel(f'{datasets_dir}/fl-lab-result-urls-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for Kaycha Labs.' % len(data))
    return data


def parse_results_kaycha(
        data_dir: str,
        outfile: Optional[str] = None,
        temp_path: Optional[str] = None,
        reverse: Optional[bool] = True,
        completed: Optional[list] = [],
        license_number: Optional[str] = None,
    ):
    """Parse lab results from Kaycha Labs COAs."""
    # Initialize a parser.
    parser = CoADoc()

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
        for filename in list(iter(files))[550:1_000]:

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


# === Test ===
# [✓] Tested: 2024-04-20 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # [✓] TEST: Get Kaycha COAs.
    data_dir = 'D://data/florida/results'
    kaycha_coas = get_results_kaycha(data_dir=data_dir)

    # [✓] TEST: Parse Kaycha COAs.
    # Note: This is a super, super long process
    data_dir = 'D://data/florida/results'
    pdf_dir = 'D://data/florida/results/pdfs'
    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    for folder in os.listdir(pdf_dir):
        if folder.startswith('MMTC-2015-0002'):
            data_dir = os.path.join(pdf_dir, folder)
            outfile = os.path.join(data_dir, '.datasets', f'{folder}-lab-results-{date}.xlsx')
            print('Parsing:', folder)
            coa_data = parse_results_kaycha(
                data_dir,
                outfile,
                reverse=True,
                completed=[]
            )
