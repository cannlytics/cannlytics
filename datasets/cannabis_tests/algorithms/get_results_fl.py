"""
Florida cannabis lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 11/5/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)
    - [Kaycha Labs](https://yourcoa.com)
    - [The Flowery](https://support.theflowery.co)
    - [TerpLife Labs](https://www.terplifelabs.com)

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
import random
import string
import tempfile
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.gis import geocode_addresses
from cannlytics.utils.constants import DEFAULT_HEADERS
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


#-----------------------------------------------------------------------
# Parse Kaycha Labs COAs.
#-----------------------------------------------------------------------

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
        'slug': 'Altmed+Florida',
        'total': 1633,
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
    for _, row in df.iterrows():
        sleep(0.3)
        sample_id = row['lab_id']
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            continue
        # FIXME: Handle URLs without a base URL.
        download_url = row['download_url']
        if not download_url.startswith('http'):
            download_url = base + download_url
        response = requests.get(download_url, headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)

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
    for license_number, licensee in licenses.items():
        expected_total = licensee['total']
        if expected_total == 0:
            continue
        print('Preparing to download %i+ COAs for %s' % (expected_total, licensee['business_dba_name']))
        urls = download_coas_kaycha(
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
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = 'D://data/florida/lab_results'
    # DATA_DIR = r'C:\.datasets\data\florida\lab_results'

    # [✓] TEST: Get Kaycha COAs.
    kaycha_coas = get_results_kaycha(DATA_DIR)

    # [✓] TEST: Parse Kaycha COAs.
    # Note: This is a super, super long process
    # pdf_dir = 'D://data/florida/lab_results/.datasets/pdfs'
    # date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # for folder in os.listdir(pdf_dir):
    #     if folder.startswith('MMTC-2015-0002'):
    #         data_dir = os.path.join(pdf_dir, folder)
    #         outfile = os.path.join(DATA_DIR, '.datasets', f'{folder}-lab-results-{date}.xlsx')
    #         print('Parsing:', folder)
    #         coa_data = parse_results_kaycha(
    #             data_dir,
    #             outfile,
    #             reverse=True,
    #             completed=[]
    #         )


#-----------------------------------------------------------------------
# The Flowery (892+ results).
# TODO: Automate to be a daily script.
#-----------------------------------------------------------------------

def get_results_the_flowery(
        data_dir: str,
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
        options = EdgeOptions()
        options.add_argument('--headless')
        driver = webdriver.Edge(options=options)

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
    datasets_dir = os.path.join(data_dir, '.datasets')
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

    # TODO: Save details about each COA, including The Flowery company data.

    # Return the COA URLs.
    return df


def get_product_results_the_flowery(data_dir: str, overwrite = False, **kwargs):
    """Get product results from The Flowery website."""
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

    # Iterate over all of the product types.
    observations = []
    categories = ['Flower', 'Concentrates', 'Pre-Rolls', 'Vaporizers', 'Tinctures']
    for category in categories:

        # Load the category page.
        url = f'https://theflowery.co/shop?categories[]={category}'
        driver.get(url)
        sleep(3.33)

        # Get all of the product cards.
        divs = driver.find_elements(by=By.CSS_SELECTOR, value='a.s-shop-product-card')
        for div in divs:
            
            # Extract product name.
            product_name = div.find_element(by=By.CLASS_NAME, value='title').text

            # Extract product image URL.
            product_image = div.find_element(by=By.TAG_NAME, value='img').get_attribute('src')

            # Extract product price.
            product_price = float(div.find_element(by=By.CLASS_NAME, value='full-price').text.strip('$'))

            # Extract strain type.
            strain_type = div.find_element(by=By.CLASS_NAME, value='sort').text

            # Extract product URL (assuming the URL is stored in the href attribute of a link)
            product_url = div.get_attribute('href')

            # Store the extracted data in a dictionary
            obs = {
                'product_name': product_name,
                'image_url': product_image,
                'product_price': product_price,
                'strain_type': strain_type,
                'product_url': product_url
            }
            observations.append(obs)

    # Get the COA URL for each product.
    # TODO: Also get the image_url.
    for i, obs in enumerate(observations):
        coa_url = ''
        driver.get(obs['product_url'])
        sleep(3.33)
        links = driver.find_elements(by=By.TAG_NAME, value='a')
        for link in links:
            if link.get_attribute('href') and '.pdf' in link.get_attribute('href'):
                coa_url = link.get_attribute('href')
                break
        observations[i]['coa_url'] = coa_url
        print('Found COA URL: %s' % coa_url)

    # Close the driver.
    driver.close()

    # Download the COA PDFs.
    license_pdf_dir = os.path.join(data_dir, '.datasets', 'pdfs', 'MMTC-2019-0020')
    for obs in observations:
        coa_url = obs['coa_url']

        # Get the sample ID
        sample_id = coa_url.split('/')[-1].split('.')[0]

        # Format the file.
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            print('Cached: %s' % outfile)
            continue
        sleep(0.3)

        # Download the PDF.
        try:
            response = requests.get(coa_url, headers=DEFAULT_HEADERS)
            with open(outfile, 'wb') as pdf:
                pdf.write(response.content)
            print('Downloaded: %s' % outfile)
            sleep(3.33)
        except:
            print('Failed to download: %s' % coa_url)

    # Merge The Flowery data with the COA data.
    the_flowery = FLORIDA_LICENSES['MMTC-2019-0020']
    observations = [{**the_flowery, **x} for x in observations]

    # Save the data.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    data = pd.DataFrame(observations)
    datasets_dir = os.path.join(DATA_DIR, '.datasets')
    data.to_excel(f'{datasets_dir}/the-flowery-lab-result-urls-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for The Flowery.' % len(data))
    return data


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = 'D://data/florida/lab_results'
    
    # [✓] TEST: Get The Flowery COAs.
    the_flowery_products = get_product_results_the_flowery(DATA_DIR)
    the_flowery_coas = get_results_the_flowery(DATA_DIR)


#-----------------------------------------------------------------------
# Download TerpLife Labs COAs.
#-----------------------------------------------------------------------

class TerpLifeLabs:
    """Download lab results from TerpLife Labs."""

    def __init__(self, data_dir):
        """Initialize the driver and directories."""
        self.data_dir = data_dir
        self.datasets_dir = os.path.join(data_dir, '.datasets')
        self.pdf_dir = os.path.join(self.datasets_dir, 'pdfs')
        self.license_pdf_dir = os.path.join(self.pdf_dir, 'terplife')
        if not os.path.exists(self.datasets_dir): os.makedirs(self.datasets_dir)
        if not os.path.exists(self.pdf_dir): os.makedirs(self.pdf_dir)
        if not os.path.exists(self.license_pdf_dir): os.makedirs(self.license_pdf_dir)
        self.driver = self.initialize_selenium()

    def get_results_terplife(
            self,
            queries: list,
            url='https://www.terplifelabs.com/coa/',
            wait=60,
        ):
        """Get lab results published by TerpLife Labs on the public web."""
        start = datetime.now()
        self.driver.get(url)
        sleep(1)
        for query in queries:
            print('Querying: %s' % query)
            self.query_search_box(query)
            self.download_search_results(wait=wait)
        end = datetime.now()
        print('Finished downloading TerpLife Labs COAs.')
        print('Time elapsed: %s' % str(end - start))

    def download_search_results(self, wait=60):
        """Download the results of a search."""
        # FIXME: Wait for the table to load instead of simply waiting.
        sleep(wait)
        load = EC.presence_of_element_located((By.CLASS_NAME, 'file-list'))
        table = WebDriverWait(self.driver, wait).until(load)
        rows = table.find_elements(By.CLASS_NAME, 'file-item')
        print('Found %i rows.' % len(rows))
        for row in rows:

            # Skip if the file has already be downloaded.
            try:
                file_name = row.find_element(By.CLASS_NAME, 'file-item-name').text
                if file_name == 'COAS':
                    continue
                outfile = os.path.join(self.license_pdf_dir, file_name)
                if os.path.exists(outfile):
                    print('Cached: %s' % outfile)
                    continue
            except:
                print('ERROR FINDING: %s' % file_name)
                sleep(60)
                break

            # Click on the icons for each row.
            try:
                self.driver.execute_script('arguments[0].scrollIntoView();', row)
                sleep(3.33)
                row.click()
            except:
                print('ERROR CLICKING: %s' % file_name)
                continue

            # Click the download button.
            try:
                sleep(random.uniform(30, 31))
                download_button = self.driver.find_element(By.CLASS_NAME, 'lg-download')
                download_button.click()
                print('Downloading: %s' % file_name)
                # FIXME: Properly wait for the download to finish.
                sleep(random.uniform(30, 31))
            except:
                print('ERROR DOWNLOADING: %s' % file_name)
                continue

            # Click the close button.
            try:
                close_button = self.driver.find_element(By.CLASS_NAME, 'lg-close')
                close_button.click()
            except:
                print('ERROR CLOSING: %s' % file_name)

    def query_search_box(self, character):
        """Find the search box and enter text."""
        search_box = self.get_search_box()
        self.driver.execute_script('arguments[0].scrollIntoView();', search_box)
        sleep(0.3)
        search_box.clear()
        search_box.send_keys(character)
        sleep(0.3)
        search_button = search_box.find_element(By.XPATH, 'following-sibling::*[1]')
        search_button.click()

    def get_search_box(self):
        """Find the search box and enter text."""
        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
        for input in inputs:
            if input.get_attribute('placeholder') == 'Enter a keyword to search':
                return input
        return None

    def initialize_selenium(self):
        """Initialize Selenium."""
        service = Service()
        prefs = {
            # FIXME: Does this need an absolute reference?
            # 'download.default_directory': self.license_pdf_dir,
            'download.default_directory': r'D:\data\florida\lab_results\.datasets\pdfs\terplife',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True
        }
        # try:
        #     options = Options()
        #     options.add_argument('--window-size=1920,1200')
        #     options.add_argument('--headless')
        #     options.add_argument('--disable-gpu')
        #     options.add_argument('--no-sandbox')
        #     options.add_experimental_option('prefs', prefs)
        #     service = Service()
        #     driver = webdriver.Chrome(options=options, service=service)
        # except:
        options = EdgeOptions()
        options.add_experimental_option('prefs', prefs)
        # options.add_argument('--headless')
        driver = webdriver.Edge(options=options, service=service)
        return driver

    def quit(self):
        """Close the driver."""
        self.driver.quit()


# === Test ===
if __name__ == '__main__':

    # Download TerpLife Labs COAs.
    # queries = ['h' + x for x in string.ascii_lowercase]
    # queries.extend(['d' + x for x in string.ascii_lowercase])
    # queries.extend(['e' + x for x in string.ascii_lowercase])
    # queries.extend(['f' + x for x in string.ascii_lowercase])
    # queries.extend(['g' + x for x in string.ascii_lowercase])
    specific_letters = [x for x in string.ascii_lowercase]
    queries = [a + b for a in specific_letters for b in string.ascii_lowercase]
    queries = queries[78:]
    # queries.reverse()
    DATA_DIR = 'D://data/florida/lab_results'
    downloader = TerpLifeLabs(DATA_DIR)
    downloader.get_results_terplife(queries)
    downloader.quit()


# TODO: Search TerpLife for known strains.

# TODO: Parse TerpLife Labs COA PDF.


#-----------------------------------------------------------------------
# Parse ACS labs COAs.
#-----------------------------------------------------------------------

# # EXAMPLE: Parse a folder of ACS labs COAs.

# from datetime import datetime
# import os
# import pandas as pd
# from cannlytics.data.coas import CoADoc

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
#         print(str(e))

# # Save the data.
# date = datetime.now().isoformat()[:19].replace(':', '-')
# outfile = f'D://data/florida/lab_results/.datasets/acs-lab-results-{date}.xlsx'
# df = pd.DataFrame(all_data)
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

import os
import requests

# List of URLs
urls = [
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRTI3OV8yNDEyNzAwMDM4MjU0NzZfMDMwOTIwMjNfNjQwYTcyMTFmMTAyMA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRDk5MV81NzEwNjAwMDM3MTk4MzRfMDMwNjIwMjNfNjQwNjgyN2Y2ZjU4Mg==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDc5N18zMjE1NjAwMDM5ODYxMzZfMDQxMDIwMjNfNjQzNDlhNTJlMmRlYg==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTk5MF8yOTM1MzAwMDM5NDA2MjBfMDQyMTIwMjNfNjQ0MmFhNTJlYjcxMw==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjM5MV8yOTUyNzAwMDQxMzQ3ODZfMDQyNTIwMjNfNjQ0ODFlOTQ1NDBlNQ==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRjg3MV80OTQ0NzAwMDQwNDgxODVfMDMyMzIwMjNfNjQxY2FmNTllYjcxMA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQTU4NF81NTMxMjAwMDM3ODAxNTBfMDEzMDIwMjNfNjNkODZjNGI2MzQxZQ==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDSDEyMl8yNjU4LTE1OTQtNjk5NC0yNjg5XzEyMjgyMDIxXzYxY2I1MDA1M2YxZjk=",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjQ4OF81NTMwMDAwMDI4OTQ2MzNfMDIxMDIwMjNfNjNlNmM3N2Y1OWJjYw==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjE5OV8xODM2MTAwMDM3MDUzNzVfMDIwODIwMjNfNjNlM2M5ZmMyMzY4ZQ==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzAwOS1ETFItNDEtU1RQQS1MUkM1LTA1MDEyMDIz",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEWjQ5Ny0xMjE0MjItOTlQUi1SMzUtMDEyMTIwMjM=",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzI3Ny1JRDI0Mi1MUi1RU0ZHLUxSNS0wNTAzMjAyMw==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjU1Ml81NTc3MzAwMDQwOTUwNzJfMDQyODIwMjNfNjQ0YzFmNjc4YjM3Mg==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDkxMS0wMzA2MjMtREJTRC1TSC1TRzM1LTA0MTAyMDIz",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEUTY3MV80OTQ0NzAwMDM0NDUwMTlfMTEwMTIwMjJfNjM2MWM3Y2Q5MGM3MA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzc4M180OTQ0NzAwMDM4NzY5MzZfMDUwOTIwMjNfNjQ1YTUwNWE2OTFmNA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDWjkxNl8xODM2MzAwMDI0NDc4NzlSMl8wNjI3MjAyMl82MmI5Y2E4YTI5YmI3",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzcwM180OTQ0ODAwMDQxMzYyNjhfMDUwODIwMjNfNjQ1OTVkNjgxMzExZA==",
    "https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQzc0OS0wMTA1MjMtU0dMQzEyLVIzNS0wMjIxMjAyMw==",
    "https://salve-platform-production-pub-1.s3.amazonaws.com/10877/DA30425010-002-%28Original%29-%281%29.pdf",
    "https://salve-platform-production-pub-1.s3.amazonaws.com/11319/DA30512010-006-%28Original%29.pdf",
    "https://salve-platform-production-pub-1.s3.amazonaws.com/11432/DA30518009-001-%28Original%29.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30412005-002-Revision-2-1.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30330009-005-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/05/DA30429001-005-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30411005-004-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30309007-004-Original-1.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30225012-006-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/T304067-FTH-Dragon-Fruit-WF-3.5g-1-8oz.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30304005-002-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30309007-003-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30325005-007-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30223006-006-Revision-1.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30316004-009-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30316005-002-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30311007-004-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2022/01/DA11229005-002.pdf",
    "https://getfluent.com/wp-content/uploads/2022/01/DA20104001-010.pdf",
    "https://getfluent.com/wp-content/uploads/2022/01/Super-Jack-WF-3.5-g.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30407004-006-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/03/DA30314003-001-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30402002-002-Original.pdf",
    "https://getfluent.com/wp-content/uploads/2023/04/DA30406008-001-Original.pdf",
    "https://jungleboysflorida.com/wp-content/uploads/2023/04/Puro-Loco-Prem-Fl-02156-DA30415006-009-marketing.pdf",
    "https://jungleboysflorida.com/wp-content/uploads/2023/04/Frozen-Grapes-Prem-Flower-02058-DA30414007-001-marketing.pdf",
    "https://yourcoa.com/coa/coa-download?sample=DA20708002-010",
    "https://yourcoa.com/coa/coa-download?sample=DA30314006-007-mrk",
    "https://www.trulieve.com/files/lab-results/35603_0001748379.pdf",
]

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



#-----------------------------------------------------------------------
# Aggregate all parsed COAs.
#-----------------------------------------------------------------------

# # === Tests ===
# # [✓] Tested: 2023-08-14 by Keegan Skeate <keegan@cannlytics>
# if __name__ == '__main__':

#     from datetime import datetime
#     import os
#     from cannlytics.data.coas import CoADoc
#     import pandas as pd

#     # [✓] TEST: Parse Kaycha COAs.
#     # Note: This is a super, super long process
#     pdf_dir = 'D://data/florida/lab_results/.datasets/pdfs'
#     date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
#     folders = os.listdir(pdf_dir)
#     folders.reverse()
#     for folder in folders:
#         if folder.startswith('MMTC'):
#             data_dir = os.path.join(pdf_dir, folder)
#             outfile = os.path.join(DATA_DIR, '.datasets', f'{folder}-lab-results-{date}.xlsx')
#             print('Parsing:', folder)
#             coa_data = parse_results_kaycha(
#                 data_dir,
#                 outfile,
#                 reverse=True,
#                 completed=[],
#                 license_number=folder,
#             )
    
#     # Lab result constants.
#     CONSTANTS = {
#         'lims': 'Kaycha Labs',
#         'lab': 'Kaycha Labs',
#         'lab_image_url': 'https://www.kaychalabs.com/wp-content/uploads/2020/06/newlogo-2.png',
#         'lab_address': '4101 SW 47th Ave, Suite 105, Davie, FL 33314',
#         'lab_street': '4101 SW 47th Ave, Suite 105',
#         'lab_city': 'Davie',
#         'lab_county': 'Broward',
#         'lab_state': 'FL',
#         'lab_zipcode': '33314',
#         'lab_phone': '833-465-8378',
#         'lab_email': 'info@kaychalabs.com',
#         'lab_website': 'https://www.kaychalabs.com/',
#         'lab_latitude': 26.071350,
#         'lab_longitude': -80.210750,
#         'licensing_authority_id': 'OMMU',
#         'licensing_authority': 'Florida Office of Medical Marijuana Use',
#     }

#     # Specify where your ACS Labs COAs live.
#     folder_path = 'D://data/florida/lab_results/.datasets/'

#     # Aggregate all of the parsed COAs.
#     data_frames = []
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.xlsx'):
#             file_path = os.path.join(folder_path, filename)
#             try:
#                 df = pd.read_excel(file_path, sheet_name='Details')
#                 data_frames.append(df)
#                 print('Compiled %i results:' % len(df), filename)
#             except:
#                 continue

#     # Sort by when the COA was parsed and keep only the most recent by sample ID.
#     aggregate = pd.concat(data_frames, ignore_index=True)
#     aggregate.sort_values('coa_parsed_at', ascending=False, inplace=True)
#     aggregate.drop_duplicates(subset='sample_id', keep='first', inplace=True)
#     print('Aggregated %i COAs.' % len(aggregate))

#     # FIXME: Standardize the data.
#     for constant, value in CONSTANTS.items():
#         aggregate[constant] = value

#     # FIXME: Augment license data.
#     import sys
#     sys.path.append('./datasets')
#     sys.path.append('../../../datasets')
#     from cannabis_licenses.algorithms.get_licenses_fl import get_licenses_fl
#     licenses = get_licenses_fl()
#     licenses['license_type'] = 'Medical - Retailer'
#     data = pd.merge(
#         aggregate,
#         licenses,
#         suffixes=['', '_copy'],
#         on='license_number',
#     )
#     data = data.filter(regex='^(?!.*_copy$)')

#     # Save the results.
#     parser = CoADoc()
#     date = datetime.now().isoformat()[:19].replace(':', '-')
#     outfile = f'D://data/florida/lab_results/.datasets/fl-lab-results-{date}.xlsx'
#     parser.save(aggregate, outfile)
#     print('Saved aggregated COAs data:', outfile)

#     # TODO: Merge with unparsed COA URLs.
