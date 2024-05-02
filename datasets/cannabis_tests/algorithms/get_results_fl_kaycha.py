"""
Get Florida cannabis lab results | Kaycha Labs
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 5/1/2024
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
import os
import tempfile
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.coas.algorithms.kaycha import parse_kaycha_coa
from cannlytics.utils.utils import (
    download_file_with_selenium,
    remove_duplicate_files,
)
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd
import requests

# Get a list of Florida companies.
# Note: It may be best to retrieve this list dynamically.
# TODO: Try to find COAs for the remaining companies. E.g.
# - Plant 13 Florida, Inc.
# - House of Platinum Cannabis
# - Cookies Florida, Inc.
FLORIDA_LICENSES = {
    # 'MMTC-2015-0002': {
    #     'business_dba_name': 'Ayr Cannabis Dispensary',
    #     'business_legal_name': 'Liberty Health Sciences, FL',
    #     'slug': 'Liberty+Health+Sciences%2C+FL',
    # },
    # 'MMTC-2017-0011': {
    #     'business_dba_name': 'Cannabist',
    #     'slug': 'Cannabist',
    # },
    # 'MMTC-2019-0018': {
    #     'business_dba_name': 'Cookies Florida, Inc.',
    #     'slug': '',
    # },
    'MMTC-2015-0001': {
        'business_dba_name': 'Curaleaf',
        'slug': 'CURALEAF+FLORIDA+LLC',
    },
    # 'MMTC-2015-0003': {
    #     'business_dba_name': 'Fluent ',
    #     'slug': 'Fluent',
    # },
    # 'MMTC-2019-0019': {
    #     'business_dba_name': 'Gold Leaf',
    #     'slug': 'Gold+Leaf',
    # },
    # 'MMTC-2019-0021': {
    #     'business_dba_name': 'Green Dragon',
    #     'slug': 'Green+Dragon',
    # },
    # 'MMTC-2016-0007': {
    #     'business_dba_name': 'GrowHealthy',
    #     'slug': 'GrowHealthy',
    # },
    # 'MMTC-2017-0013': {
    #     'business_dba_name': 'GTI (Rise Dispensaries)',
    #     'slug': 'GTI',
    # },
    # 'MMTC-2018-0014': {
    #     'business_dba_name': 'House of Platinum Cannabis',
    #     'slug': '',
    # },
    # 'MMTC-2019-0016': {
    #     'business_dba_name': 'Insa - Cannabis for Real Life',
    #     'slug': 'Insa',
    # },
    # 'MMTC-2019-0015': {
    #     'business_dba_name': 'Jungle Boys',
    #     'slug': 'Jungle+Boys',
    # },
    # 'MMTC-2017-0010': {
    #     'business_dba_name': 'MüV',
    #     'slug': 'Altmed+Florida',
    # },
    # 'MMTC-2016-0006': {
    #     'business_dba_name': 'Planet 13 Florida, Inc.',
    #     'slug': '',
    # },
    # 'MMTC-2019-0022': {
    #     'business_dba_name': 'Revolution Florida',
    #     'slug': 'Revolution',
    # },
    # 'MMTC-2019-0017': {
    #     'business_dba_name': 'Sanctuary Cannabis',
    #     'slug': 'Sanctuary',
    # },
    # 'MMTC-2017-0012': {
    #     'business_dba_name': 'Sunburn',
    #     'slug': '',
    # },
    # 'MMTC-2017-0008': {
    #     'business_dba_name': 'Sunnyside*',
    #     'slug': 'Sunnyside',
    # },
    # 'MMTC-2015-0004': {
    #     'business_dba_name': 'Surterra Wellness',
    #     'slug': 'Surterra+Wellness',
    # },
    # 'MMTC-2019-0020': {
    #     'business_dba_name': 'The Flowery',
    #     'slug': 'The+Flowery',
    # },
    # 'MMTC-2015-0005': {
    #     'business_dba_name': 'Trulieve',
    #     'slug': 'Trulieve',
    # },
    # 'MMTC-2017-0009': {
    #     'business_dba_name': 'VidaCann',
    #     'slug': 'VidaCann',
    # },
}

# Define the minimum file size for a PDF.
MIN_FILE_SIZE = 21 * 1024


def download_coas_kaycha(
        data_dir: str,
        slug: str,
        pdf_dir: Optional[str] = None,
        dba: Optional[str] = None,
        producer_license_number: Optional[str] = None,
        overwrite: Optional[bool] = False,
        base: Optional[str] = 'https://yourcoa.com',
        columns: Optional[list] = None,
        pause: Optional[float] = 0.33,
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
        sleep(pause)

    # Save the observed lab result URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    df = pd.DataFrame(observations)
    df.to_excel(f'{datasets_dir}/fl-lab-result-urls-{slug}-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for %s' % (len(df), slug))

    # Create a directory for COA PDFs.
    if pdf_dir is None:
        pdf_dir = os.path.join(data_dir, 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Create a directory for each licensees COAs.
    license_pdf_dir = os.path.join(pdf_dir, producer_license_number)
    if not os.path.exists(license_pdf_dir):
        os.makedirs(license_pdf_dir)

    # Download the PDFs.
    # Checks if the file size is small and retires with Selenium if needed.
    print('License directory:', license_pdf_dir)
    for _, row in df.iterrows():
        sleep(pause)
        download_url = row['download_url']
        if not download_url.startswith('http'):
            download_url = base + download_url
        sample_id = download_url.split('/')[-1].split('?')[0].split('&')[0]
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            print('Cached:', download_url)
            continue
        try:
            coa_url = f'{base}/coa/download?sample={sample_id}'
            response = requests.get(coa_url, headers=DEFAULT_HEADERS)
            if response.status_code == 200:
                if len(response.content) < MIN_FILE_SIZE:
                    print('File size is small, retrying with Selenium:', coa_url)
                    # coa_url = f'{base}/coa/coa-view?sample={sample_id}'
                    response = requests.get(download_url, allow_redirects=True)
                    if response.status_code == 200:
                        redirected_url = response.url
                        download_file_with_selenium(
                            redirected_url,
                            download_dir=license_pdf_dir,
                        )
                        print('Downloaded with Selenium:', redirected_url)
                else:
                    with open(outfile, 'wb') as pdf:
                        pdf.write(response.content)
                    print('Downloaded:', outfile)
            else:
                print('Failed to download, retrying with Selenium:', coa_url)
                response = requests.get(download_url, allow_redirects=True)
                if response.status_code == 200:
                    redirected_url = response.url
                    download_file_with_selenium(
                        redirected_url,
                        download_dir=license_pdf_dir,
                    )
                    print('Downloaded with Selenium:', redirected_url)
        except:
            coa_url = f'{base}/coa/coa-view?sample={sample_id}'
            response = requests.get(coa_url, allow_redirects=True)
            if response.status_code == 200:
                redirected_url = response.url
                download_file_with_selenium(
                    redirected_url,
                    download_dir=license_pdf_dir,
                )
                print('Downloaded with Selenium:', redirected_url)

    # Return the COA URLs.
    return df


def get_results_kaycha(
        data_dir: str,
        licenses=None,
        pause: Optional[float] = 0.33,
        verbose: Optional[bool] = False,
        **kwargs
    ):
    """Get lab results published by Kaycha Labs on the public web."""

    # Download COAs for each licensee.
    coa_urls = []
    if licenses is None:
        licenses = FLORIDA_LICENSES
    items = reversed(licenses.items())
    # items = licenses.items()
    for producer_license_number, licensee in items:
        print('Getting COAs for %s' % licensee['business_dba_name'])
        urls = download_coas_kaycha(
            data_dir,
            slug=licensee['slug'],
            dba=licensee['business_dba_name'],
            producer_license_number=producer_license_number,
            pause=pause,
        )
        coa_urls.append(urls)

        # Remove duplicate COAs.
        try:
            datasets_dir = os.path.join(data_dir, 'datasets')
            pdf_dir = os.path.join(datasets_dir, 'pdfs')
            license_pdf_dir = os.path.join(pdf_dir, producer_license_number)
            remove_duplicate_files(license_pdf_dir, verbose=verbose)
        except:
            print('Failed to remove duplicate files.')

    # Save and return all of the COA URLs.
    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    data = pd.concat(coa_urls)
    datasets_dir = os.path.join(data_dir, 'datasets')
    data.to_excel(f'{datasets_dir}/fl-lab-result-urls-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for Kaycha Labs.' % len(data))
    return data


def parse_results_kaycha(
        data_dir: str,
        pdf_dir: str,
        temp_path: Optional[str] = None,
        reverse: Optional[bool] = True,
        sort: Optional[bool] = False,
    ):
    """Parse lab results from Kaycha Labs COAs."""
    parser = CoADoc()
    if temp_path is None:
        temp_path = tempfile.mkdtemp()
    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    folders = os.listdir(pdf_dir)
    folders = [x for x in folders if x.startswith('MMTC')]
    if sort: folders = sorted(folders)
    if reverse: folders = reversed(folders)
    for folder in folders:

        # DEV:
        completed = [
            "MMTC-2015-0004",
            "MMTC-2015-0005",
            "MMTC-2016-0006",
            "MMTC-2015-0003",
            "MMTC-2015-0002",
            'MMTC-2017-0009',
            'MMTC-2016-0007',
            'MMTC-2017-0011',
            'MMTC-2017-0012',
            'MMTC-2017-0013',
            'MMTC-2018-0014',
            'MMTC-2019-0015',
            # In-progress
            'MMTC-2015-0001',
            'MMTC-2017-0008',
            'MMTC-2017-0010',
            'MMTC-2019-0016',
        ]
        if folder in completed:
            print('Completed:', folder)
            continue           

        # Identify all of the PDFs for a licensee.
        outfile = os.path.join(data_dir, 'datasets', f'fl-results-{folder}-{date}.xlsx')
        license_pdf_dir = os.path.join(pdf_dir, folder)
        pdf_files = os.listdir(license_pdf_dir)
        if reverse: pdf_files = reversed(pdf_files)

        # Parse the COAs for each licensee.
        print('Parsing %i COAs:' % len(pdf_files), folder)
        all_data = []
        for pdf_file in pdf_files:
            if not pdf_file.endswith('.pdf'):
                continue
            try:
                doc = os.path.join(license_pdf_dir, pdf_file)
                coa_data = parse_kaycha_coa(
                    parser,
                    doc,
                    verbose=True,
                    temp_path=temp_path,
                )
                if coa_data.get('producer_license_number') is None:
                    coa_data['producer_license_number'] = folder
                all_data.append(coa_data)
                print('Parsed:', doc)
            except:
                print('Error:', doc)
        
        # Save the data for each licensee.
        try:
            parser.save(all_data, outfile)
            print('Saved COA data:', outfile)
        except:
            print('Failed to save COA data.')
    return all_data


# === Test ===
# [✓] Tested: 2024-04-21 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # # [✓] TEST: Get Kaycha COAs.
    # data_dir = 'D://data/florida/results'
    # kaycha_coas = get_results_kaycha(
    #     data_dir=data_dir,
    #     pause=3.33,
    #     verbose=True,
    # )

    # [✓] TEST: Parse Kaycha COAs.
    # Note: This is a super, super long process
    parse_results_kaycha(
        data_dir='D://data/florida/results',
        pdf_dir='D://data/florida/results/pdfs',
        reverse=False,
        sort=True,
    )
