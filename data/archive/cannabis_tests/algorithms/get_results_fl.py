"""
Florida cannabis lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 5/20/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)
    - [Kaycha Labs](https://yourcoa.com)

Resources:

    - https://www.reddit.com/r/FLMedicalTrees/search/?q=COA
    - https://www.reddit.com/r/FLMedicalTrees/comments/11hfwjl/question_on_dispensaries_and_coas/
    - https://www.reddit.com/r/FLMedicalTrees/comments/1272per/anyone_have_batch_s_they_can_share_for_our/
    - https://www.reddit.com/r/FLMedicalTrees/comments/vdnpqf/coa_accumulation/
    - https://www.reddit.com/r/FLMedicalTrees/comments/13jizze/vidacann_finally_put_all_coas_up/
    - https://www.reddit.com/r/FLMedicalTrees/comments/13j1tua/rick_james_coa/
    - https://www.reddit.com/r/FLMedicalTrees/comments/13d7bwb/can_someone_explain_some_terps_to_me/
    - https://www.reddit.com/r/FLMedicalTrees/comments/11v4pa5/holy_farnesene_batman/

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Specify where your data lives.
DATA_DIR = 'D://data/florida/lab_results'
ENV_FILE = '../../../../.env'


#-----------------------------------------------------------------------
# Parse Kaycha Labs COAs.
#-----------------------------------------------------------------------

# Get a list of Florida companies.
# Note: It may be best to retrieve this list dynamically.
# TODO: Try to find COAs for the remaining companies.
# - Plant 13 Florida, Inc.
# - House of Platinum Cannabis
# - Cookies Florida, Inc.
licenses = {
    'MMTC-2015-0002': {
        'business_dba_name': 'Ayr Cannabis Dispensary',
        'business_legal_name': 'Liberty Health Sciences, FL',
        'slug': 'Liberty+Health+Sciences%2C+FL',
        'total': 3924,
    },
    'MMTC-2017-0011': {
        'business_dba_name': 'Cannabist',
        'slug': 'Cannabist',
        'total': 3,
    },
    'MMTC-2019-0018': {
        'business_dba_name': 'Cookies Florida, Inc.',
        'slug': '',
        'total': 0,
    },
    'MMTC-2015-0001': {
        'business_dba_name': 'Curaleaf',
        'slug': 'CURALEAF+FLORIDA+LLC',
        'total': 8905,
    },
    'MMTC-2015-0003': {
        'business_dba_name': 'Fluent ',
        'slug': 'Fluent',
        'total': 70,
    },
    'MMTC-2019-0019': {
        'business_dba_name': 'Gold Leaf',
        'slug': 'Gold+Leaf',
        'total': 6,
    },
    'MMTC-2019-0021': {
        'business_dba_name': 'Green Dragon',
        'slug': 'Green+Dragon',
        'total': 0,
    },
    'MMTC-2016-0007': {
        'business_dba_name': 'GrowHealthy',
        'slug': 'GrowHealthy',
        'total': 28,
    },
    'MMTC-2017-0013': {
        'business_dba_name': 'GTI (Rise Dispensaries)',
        'slug': 'GTI',
        'total': 0,
    },
    'MMTC-2018-0014': {
        'business_dba_name': 'House of Platinum Cannabis',
        'slug': '',
        'total': 0,
    },
    'MMTC-2019-0016': {
        'business_dba_name': 'Insa - Cannabis for Real Life',
        'slug': 'Insa',
        'total': 0,
    },
    'MMTC-2019-0015': {
        'business_dba_name': 'Jungle Boys',
        'slug': 'Jungle+Boys',
        'total': 2,
    },
    'MMTC-2017-0010': {
        'business_dba_name': 'MüV',
        'slug': 'Muv',
        'total': 0,
    },
    'MMTC-2016-0006': {
        'business_dba_name': 'Planet 13 Florida, Inc.',
        'slug': '',
        'total': 0,
    },
    'MMTC-2019-0022': {
        'business_dba_name': 'Revolution Florida',
        'slug': 'Revolution',
        'total': 0,
    },
    'MMTC-2019-0017': {
        'business_dba_name': 'Sanctuary Cannabis',
        'slug': 'Sanctuary',
        'total': 581,
    },
    'MMTC-2017-0012': {
        'business_dba_name': 'Sunburn',
        'slug': '',
        'total': 0,
    },
    'MMTC-2017-0008': {
        'business_dba_name': 'Sunnyside*',
        'slug': 'Sunnyside',
        'total': 886,
    },
    'MMTC-2015-0004': {
        'business_dba_name': 'Surterra Wellness',
        'slug': 'Surterra+Wellness',
        'total': 1,
    },
    'MMTC-2019-0020': {
        'business_dba_name': 'The Flowery',
        'slug': 'The+Flowery',
        'total': 0,
    },
    'MMTC-2015-0005': {
        'business_dba_name': 'Trulieve',
        'slug': 'Trulieve',
        'total': 0,
    },
    'MMTC-2017-0009': {
        'business_dba_name': 'VidaCann',
        'slug': 'VidaCann',
        'total': 4,
    },
}


def download_license_coas_kaycha(
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
    datasets_dir = os.path.join(data_dir, '.datasets')
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
            print(f"Request failed with status {response.status_code}")

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
            observation['download_url'] = links[n]
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

    # Download the PDF.
    for _, row in df.iterrows():
        sleep(0.3)
        sample_id = row['lab_id']
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            continue
        response = requests.get(row['download_url'], headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)
    
    # Return the COA URLs.
    return df


def get_results_kaycha(data_dir: str, **kwargs):
    """Get lab results published by Kaycha Labs on the public web."""

    # Sort licenses by the number of COAs.
    licenses = dict(sorted(licenses.items(), key=lambda x: x[1]['total']))

    # Iterate over each producer.
    coa_urls = []
    for license_number, licensee in licenses.items():
        expected_total = licensee['total']
        if expected_total == 0:
            continue
        print('Preparing to download %i+ COAs for %s' % (expected_total, licensee['business_dba_name']))
        urls = download_license_coas_kaycha(
            data_dir,
            slug=licensee['slug'],
            dba=licensee['business_dba_name'],
            producer_license_number=license_number,
        )
        coa_urls.append(urls)

    # Save and return all of the COA URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    data = pd.concat(coa_urls)
    datasets_dir = os.path.join(data_dir, '.datasets')
    data.to_excel(f'{datasets_dir}/fl-lab-result-urls-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for Kaycha Labs.' % len(data))
    return data


# TODO: Begin to parse lab results from the PDFs!


# TODO: Parse a COA from a URL.
url = 'https://yourcoa.com/coa/coa-download?sample=DA20708002-010'
url = 'https://yourcoa.com/coa/coa-download?sample=DA30314006-007-mrk'
url = 'https://www.trulieve.com/files/lab-results/35603_0001748379.pdf'
# Broken: https://yourcoa.com/company/company?t=Green+Ops+FL+OpCo+LLC

#-----------------------------------------------------------------------
# The Flowery (892+ results).
#-----------------------------------------------------------------------

def get_results_the_flowery(
        slug = 'the-flowery',
        producer_license_number = 'MMTC-2019-0020',
        lists_url = 'https://support.theflowery.co/hc/en-us/sections/7240468576283-Drop-Information',
        overwrite = False,
    ):
    """Get lab results published by The Flowery on the public web."""

    # Initialize Selenium.
    try:
        service = Service()
        options = Options()
        options.add_argument('--window-size=1920,1200')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options, service=service)
    except:
        driver = webdriver.Edge()

    # Load the lists page to get each list of COAs.
    coa_lists = []
    driver.get(lists_url)
    links = driver.find_elements(by=By.TAG_NAME, value='a')
    for link in links:
        if 'COAs' in link.text:
            coa_lists.append(link.get_attribute('href'))

    # Get COA URLs.
    coa_urls = []
    for coa_list in coa_lists:
        driver = webdriver.Edge()
        driver.get(coa_list)
        links = driver.find_elements(by=By.TAG_NAME, value='a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.endswith('.pdf'):
                coa_urls.append(href)
        driver.quit()

    # Close the browser.
    driver.quit()

    # Create an output directory.
    datasets_dir = os.path.join(DATA_DIR, '.datasets')
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    # Save the COA URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    df = pd.DataFrame(coa_urls)
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

    # Download the COA PDFs.
    for coa_url in coa_urls:
        sample_id = coa_url.split('/')[-1].split('.')[0]
        batch_id = coa_url.split('/')[-2]
        outfile = os.path.join(license_pdf_dir, f'{batch_id}-{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            continue
        sleep(0.3)
        response = requests.get(coa_url, headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)


#-----------------------------------------------------------------------
# TerpLife Labs (in development).
#-----------------------------------------------------------------------

def get_search_box(driver):
    """Find the search box and enter text."""
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    for input in inputs:
        if input.get_attribute('placeholder') == 'Enter a keyword to search':
            return input
    return None

def query_search_box(driver, character):
    """Query the search box."""
    search_box = get_search_box()
    driver.execute_script("arguments[0].scrollIntoView();", search_box)
    sleep(0.3)
    search_box.clear()
    search_box.send_keys(character)


def download_search_results(driver, license_pdf_dir, wait=10):
    """Download the results of a search."""

    # Get all of the rows.
    # table = driver.find_element(By.CLASS_NAME, 'file-list')
    table = WebDriverWait(driver, wait).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'file-item'))
    )
    rows = table.find_elements(By.CLASS_NAME, 'file-item')

    # Download COA PDFs for each row.
    for row in rows:

        # Skip if the file has already be downloaded.
        file_name = row.find_element(By.CLASS_NAME, 'file-item-name').text
        outfile = os.path.join(license_pdf_dir, file_name)
        if os.path.exists(outfile):
            continue

        # Click on the icons for each row.
        driver.execute_script("arguments[0].scrollIntoView();", row)
        sleep(3.33)
        row.click()

        # Click the download button.
        sleep(3.33)
        download_button = driver.find_element(By.CLASS_NAME, 'lg-download')
        download_button.click()

        # Click the close button.
        try:
            sleep(3.33)
            close_button = driver.find_element(By.CLASS_NAME, 'lg-close')
            close_button.click()
        except:
            # Return unsuccessful completion.
            print('LARGE FILE: %s' % file_name)
            return False
    
    # Return successful completion.
    return True


def get_results_terplife(
        url = 'https://www.terplifelabs.com/coa/',
    ):
    """Get lab results published by TerpLife Labs on the public web."""

    # Create an output directory.
    datasets_dir = os.path.join(DATA_DIR, '.datasets')
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    # Create a directory for COA PDFs.
    pdf_dir = os.path.join(datasets_dir, 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Create a directory for TerpLife Labs.
    license_pdf_dir = os.path.join(pdf_dir, 'terplife')
    if not os.path.exists(license_pdf_dir):
        os.makedirs(license_pdf_dir)

    # Initialize Selenium.
    try:
        service = Service()
        options = Options()
        options.add_argument('--window-size=1920,1200')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options, service=service)
    except:
        options = EdgeOptions()
        # options.use_chromium = True
        options.add_experimental_option('prefs', {
            'download.default_directory': 'D:\\data\\florida\\lab_results\\.datasets\\pdfs\\terplife',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        })
        driver = webdriver.Edge(options=options)

    # Open the website.
    driver.get(url)
    sleep(1)

    # FIXME: Iterate through the alphabet.
    # alphabet = ['z']
    # for character in alphabet:
    character = 'z'

    # Query the results.
    query_search_box(driver, character)

    # Download files until all have been downloaded.
    iterate = True
    while iterate:

        # Stop iteration once all rows are downloaded.
        success = download_search_results(driver, license_pdf_dir)
        if success:
            iterate = False

        # Otherwise, download large files.
        drive_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uc-download-link'))
        )
        drive_button.click()

        # Go back.
        driver.back()

        # FIXME: Re-search.
        query_search_box(driver, character)

    # Close the browser
    driver.quit()

    # TODO: Return the COA PDF paths.
    return []



# TODO: Search TerpLife for known strains, e.g. ChryTop.


# TODO: Parse TerpLife Labs COA PDF.

#-----------------------------------------------------------------------
# ACS Labs
#-----------------------------------------------------------------------

# TODO: Parse Trulieve COA from a URL.
url = 'https://www.trulieve.com/files/lab-results/18362_0003059411.pdf'


# TODO: Parse a ACS Labs PDF from a URL.
url = 'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEQzA2Mi0wNjAzMjItOTlQUi1SMzUtMDcxNDIwMjI='


# TODO: Parse a ACS Labs PDF.



#-----------------------------------------------------------------------
# US Cannalytics Labs
#-----------------------------------------------------------------------

# TODO: Parse COA from URL.
us_cannalytics_coa = 'https://www.vidacann.com/wp-content/uploads/2023/04/Batch-0653-0603-5236-3992-Lot-8391-232004.pdf'


#-----------------------------------------------------------------------
# Method Testing Labs
#-----------------------------------------------------------------------

# TODO: Parse a MTL COA PDF.


#-----------------------------------------------------------------------
# Modern Canna
#-----------------------------------------------------------------------

# TODO: Parse COAs from URL.
url = 'https://moderncanna.com/coa/GD22003-07.pdf'
url = 'https://moderncanna.com/coa/GF23007-01.pdf'


#-----------------------------------------------------------------------
# Lab result analysis.
#-----------------------------------------------------------------------

# TODO: Heatmap of number of lab results throughout Florida by zipcode.


# TODO: Heatmap of terpene concentrations throughout Florida by zipcode.
