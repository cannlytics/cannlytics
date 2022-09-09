"""
Get Raw Garden Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/23/2022
Updated: 9/9/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Curate Raw Garden's publicly published lab results by:

        1. Finding products and their COA URLS on Raw Garden's website.
        2. Downloading COA PDFs from their URLs.
        3. Using CoADoc to parse the COA PDFs (with OCR).
        4. Archiving the COA data in Firestore.

Data Source:

    - Raw Garden Lab Results
    URL: <https://rawgarden.farm/lab-results/>

"""
# Standard imports.
from datetime import datetime, timedelta
import os
from time import sleep
from typing import Any, List, Optional, Tuple

# External imports.
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Internal imports.
from cannlytics.data.coas import CoADoc
from cannlytics.firebase import (
    get_document,
    initialize_firebase,
    update_documents,
    upload_file,
)
from cannlytics.utils import kebab_case, rmerge
from cannlytics.utils.constants import DEFAULT_HEADERS

# Specify where your data lives.
BUCKET_NAME = 'cannlytics-company.appspot.com'
COLLECTION = 'public/data/lab_results'
STORAGE_REF = 'data/lab_results/raw_garden'

# Create directories if they don't already exist.
# TODO: Edit `ENV_FILE` and `DATA_DIR` as needed for your desired setup.
ENV_FILE = '.env'
DATA_DIR = '.datasets'
COA_DATA_DIR = f'{DATA_DIR}/lab_results/raw_garden'
COA_PDF_DIR = f'{COA_DATA_DIR}/pdfs'
TEMP_PATH = f'{COA_DATA_DIR}/tmp'
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(COA_DATA_DIR): os.makedirs(COA_DATA_DIR)
if not os.path.exists(COA_PDF_DIR): os.makedirs(COA_PDF_DIR)
if not os.path.exists(TEMP_PATH): os.makedirs(TEMP_PATH)

# Define constants.
BASE = 'https://rawgarden.farm/lab-results/'


def get_rawgarden_products(
        start: Optional[Any] = None,
        end: Optional[Any] = None,
    ) -> pd.DataFrame:
    """Get Raw Garden's lab results page. Then get all of the product
    categories. Finally, get all product data, including: `coa_pdf`, 
    `lab_results_url`, `product_name`, `product_subtype`, `date_retail`.
    Args:
        start (str or datetime): A point in time to begin restricting
            the product list by `date_retail` (optional).
        end (str or datetime): A point in time to end restricting
            the product list by `date_retail` (optional).
    Returns:
        (DataFrame): Returns a DataFrame of product data.
    """

    # Get the website.
    response = requests.get(BASE, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get all product data listed on the website.
    observations = []
    categories = soup.find_all('div', attrs={'class': 'category-content'})
    for category in categories:
        subtype = category.find('h3').text
        dates = category.findAll('h5', attrs={'class': 'result-date'})
        names = category.findAll('h5')
        names = [div for div in names if div.get('class') is None]
        links = category.findAll('a')
        for i, link in enumerate(links):
            try:
                href = link.get('href')
                date = pd.to_datetime(dates[i].text)
                name = names[i].text
                if href.endswith('.pdf'):
                    observations.append({
                        'coa_pdf': href.split('/')[-1],
                        'lab_results_url': href,
                        'product_name': name,
                        'product_subtype': subtype,
                        'date_retail': date,
                    })
            except AttributeError:
                continue
    
    # Restrict the observations to the desired time frame.
    results = pd.DataFrame(observations)
    dates = results['date_retail']
    if start:
        if isinstance(start, str):
            latest = pd.to_datetime(start)
        else:
            latest = start
        results = results.loc[dates >= latest]
    if end:
        if isinstance(end, str):
            earliest = pd.to_datetime(end)
        else:
            earliest = end
        results = results.loc[dates <= earliest]
    results['date_retail'] = dates.apply(lambda x: x.isoformat()[:19])
    return results


def download_rawgarden_coas(
        items: pd.DataFrame,
        pause: Optional[float] = 0.24,
        verbose: Optional[bool] = True,
    ) -> None:
    """Download Raw Garden product COAs to `product_subtype` folders.
    Args:
        items: (DataFrame): A DataFrame of products with `product_subtype`
            and `lab_results_url` to download.
        pause (float): A pause to respect the server serving the PDFs,
            `0.24` seconds by default (optional).
        verbose (bool): Whether or not to print status, `True` by
            default (optional).
    """
    if verbose:
        total = len(items)
        print('Downloading %i PDFs, ETA > %.2fs' % (total, total * pause))

    # Create a folder of each of the subtypes.
    subtypes = list(items['product_subtype'].unique())
    for subtype in subtypes:
        folder = kebab_case(subtype)
        subtype_folder = f'{COA_PDF_DIR}/{folder}'
        if not os.path.exists(subtype_folder):
            os.makedirs(subtype_folder)

    # Download each COA PDF from its URL to a `product_subtype` folder.
    for i, row in enumerate(items.iterrows()):
        item = row[1]
        url = item['lab_results_url']
        subtype = item['product_subtype']
        filename = url.split('/')[-1]
        folder = kebab_case(subtype)
        outfile = os.path.join(COA_PDF_DIR, folder, filename)
        response = requests.get(url, headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        if verbose:
            message = 'Downloaded {}/{} | {}/{}'
            message = message.format(str(i +  1), str(total), folder, filename)
            print(message)
        sleep(pause)


def parse_rawgarden_coas(
        directory: str,
        filenames: Optional[list] = None,
        temp_path: Optional[str] = '/tmp',
        verbose: Optional[bool] = True,
        **kwargs,
    ) -> Tuple[list]:
    """Parse Raw Garden lab results with CoADoc.
    Args:
        directory (str): The directory of files to parse.
        filenames (list): A list of files to parse (optional).
        temp_path (str): A temporary directory to use for any OCR (optional).
        verbose (bool): Whether or not to print status, `True` by
            default (optional).
    Returns:
        (tuple): Returns both a list of parsed and unidentified COA data.
    """
    parser = CoADoc()
    parsed, unidentified = [], []
    started = False
    for path, _, files in os.walk(directory):
        if verbose and not started:
            started = True
            if filenames:
                total = len(filenames)
            else:
                total = len(files)
            print('Parsing %i COAs, ETA > %.2fm' % (total, total * 25 / 60))
        for filename in files:
            if not filename.endswith('.pdf'):
                continue
            if filenames is not None:
                if filename not in filenames:
                    continue
            doc = os.path.join(path, filename)
            try:
                coa  = parser.parse(doc, temp_path=temp_path, **kwargs)
                subtype = path.split('\\')[-1]
                coa[0]['product_subtype'] = subtype
                parsed.extend(coa)
                if verbose:
                    print('Parsed:', filename)
            except Exception as e:
                unidentified.append({'coa_pdf': filename})
                if verbose:
                    print('Error:', filename)
                    print(e)
                pass
    return parsed, unidentified


def upload_lab_results(
        observations: List[dict],
        collection: Optional[str] = None,
        database: Optional[Any] = None,
        update: Optional[bool] = True,
        verbose: Optional[bool] = True,
    ) -> None:
    """Upload lab results to Firestore.
    Args:
        observations (list): A list of lab results to upload.
        collection (str): The Firestore collection where lab results live,
            `'public/data/lab_results'` by default (optional).
        database (Client): A Firestore database instance (optional).
        update (bool): Whether or not to update existing entries, `True`
            by default (optional).
        verbose (bool): Whether or not to print status, `True` by
            default (optional).
    """
    if collection is None:
        collection = COLLECTION
    if database is None:
        database = initialize_firebase()
    refs, updates = [], []
    for obs in observations:
        sample_id = obs['sample_id']
        ref = f'{collection}/{sample_id}'
        if not update:
            doc = get_document(ref)
            if doc is not None:
                continue
        refs.append(ref)
        updates.append(obs)
    if updates:
        if verbose:
            print('Uploading %i lab results.' % len(refs))
        update_documents(refs, updates, database=database)
    if verbose:
        print('Uploaded %i lab results.' % len(refs))


#-----------------------------------------------------------------------
# EXAMPLE: Collect Raw Garden lab results data by:
#
#    1. Finding products and their COA URLS.
#    2. Downloading COA PDFs from their URLs.
#    3. Using CoADoc to parse the COA PDFs (with OCR).
#    4. Saving the data to datafiles, Firebase Storage, and Firestore.
#
#-----------------------------------------------------------------------
if __name__ == '__main__':

    # Get the most recent Raw Garden products.
    DAYS_AGO = 1
    start = datetime.now() - timedelta(days=DAYS_AGO)
    products = get_rawgarden_products(start=start)

    # Download Raw Garden product COAs to `product_subtype` folders.
    download_rawgarden_coas(products, pause=0.24, verbose=True)

    # Parse COA PDFs with CoADoc.
    coa_data, unidentified_coas = parse_rawgarden_coas(
        COA_PDF_DIR,
        filenames=products['coa_pdf'].to_list(),
        temp_path=TEMP_PATH,
        verbose=True,
    )

    # Merge the `products`'s `product_subtype` with the COA data.
    coa_dataframe = rmerge(
        pd.DataFrame(coa_data),
        products,
        on='coa_pdf',
        how='left',
        replace='right',
    )

    # Optional: Save the COA data to a workbook.
    parser = CoADoc()
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    datafile = f'{COA_DATA_DIR}/rawgarden-coa-data-{timestamp}.xlsx'
    parser.save(coa_dataframe, datafile)

    # Optional: Save the unidentified COA data.
    errors = [x['coa_pdf'] for x in unidentified_coas]
    error_file = f'{COA_DATA_DIR}/rawgarden-unidentified-coas-{timestamp}.xlsx'
    products.loc[products['coa_pdf'].isin(errors)].to_excel(error_file)

    # Optional: Initialize Firebase.
    initialize_firebase(ENV_FILE)

    # Optional: Upload the lab results to Firestore.
    upload_lab_results(
        coa_dataframe.to_dict(orient='records'),
        update=True,
        verbose=True
    )

    # Optional: Upload datafiles to Firebase Storage.
    storage_datafile = '/'.join([STORAGE_REF, datafile.split('/')[-1]])
    storage_error_file = '/'.join([STORAGE_REF, error_file.split('/')[-1]])
    upload_file(storage_datafile, datafile, bucket_name=BUCKET_NAME)
    upload_file(storage_error_file, error_file, bucket_name=BUCKET_NAME)
