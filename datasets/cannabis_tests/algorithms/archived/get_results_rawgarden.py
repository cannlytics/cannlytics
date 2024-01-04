"""
Cannabis Tests | Get Raw Garden Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/23/2022
Updated: 10/7/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Raw Garden's publicly published lab results by:

        1. Finding products and their COA URLS on Raw Garden's website.
        2. Downloading COA PDFs from their URLs.
        3. Using CoADoc to parse the COA PDFs (with OCR).
        4. Archiving the COA data in Firestore.

Data Source:

    - Raw Garden Lab Results
    URL: <https://rawgarden.farm/lab-results/>

Command line usage:

    python get_rawgarden_data.py --days_ago=1 --get_all=False

"""
# Standard imports.
from datetime import datetime, timedelta
import gc
import os
from time import sleep
from typing import Any, List, Optional, Tuple

# External imports.
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Internal imports.
from cannlytics.data.coas import CoADoc
from cannlytics.data.data import create_hash
from cannlytics.firebase import (
    get_document,
    initialize_firebase,
    update_documents,
    upload_file,
)
from cannlytics.utils import kebab_case, rmerge
from cannlytics.utils.constants import DEFAULT_HEADERS


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
        replace: Optional[bool] = False,
        verbose: Optional[bool] = True,
    ) -> None:
    """Download Raw Garden product COAs to `product_subtype` folders.
    Args:
        items: (DataFrame): A DataFrame of products with `product_subtype`
            and `lab_results_url` to download.
        pause (float): A pause to respect the server serving the PDFs,
            `0.24` seconds by default (optional).
        replace (bool): Whether or not to replace any existing PDFs,
            `False` by default (optional).
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
        if os.path.isfile(outfile):
            continue
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
    parsed, unidentified = [], []
    started = False
    filename = None
    try:
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
                file_path = os.path.join(path, filename)

                # Parse the COA, by any means necessary!
                parser = CoADoc()
                try:
                    new_data = parser.parse_pdf(
                        file_path,
                        temp_path=temp_path,
                        **kwargs
                    )
                except:
                    try:
                        # FIXME: This should work without directly calling OCR.
                        temp_file = f'{temp_path}/ocr_coa.pdf'
                        parser.pdf_ocr(
                            file_path,
                            temp_file,
                            temp_path,
                            resolution=180,
                        )
                        new_data = parser.parse_pdf(
                            temp_file,
                            temp_path=temp_path,
                            **kwargs
                        )
                    except Exception as e:
                        # Hot-fix: Remove temporary `magick-*` files.
                        try:
                            for i in os.listdir(temp_path):
                                magick_path = os.path.join(temp_path, i)
                                if os.path.isfile(magick_path) and i.startswith('magick-'):
                                    os.remove(magick_path)
                        except FileNotFoundError:
                            pass
                        unidentified.append({'coa_pdf': filename})
                        if verbose:
                            print('Error:', filename)
                            print(e)
                        continue

                # Add the subtype key and record the data.
                subtype = path.split('\\')[-1]
                if isinstance(new_data, dict):
                    new_data = [new_data]
                new_data[0]['product_subtype'] = subtype
                parsed.extend(new_data)
                parser.quit()
                gc.collect()
                if verbose:
                    print('Parsed:', filename)

                # FIXME: Save intermittently?
    except:
        print('Error parsing:', filename)

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
#    3. Using CoADoc to parse the COA PDFs (with OCR as needed).
#    4. Saving the data to datafiles, Firebase Storage, and Firestore.
#
#-----------------------------------------------------------------------
if __name__ == '__main__':

    # === Setup ===

    # Specify where your data lives.
    BUCKET_NAME = 'cannlytics-company.appspot.com'
    COLLECTION = 'public/data/lab_results'
    STORAGE_REF = 'data/lab_results/rawgarden'

    # Create directories if they don't already exist.
    # TODO: Edit `ENV_FILE` and `DATA_DIR` as needed for your desired setup.
    ENV_FILE = '../../../../.env'
    DATA_DIR = 'D:/data/california/lab_results'
    COA_DATA_DIR = f'{DATA_DIR}/rawgarden'
    COA_PDF_DIR = f'{COA_DATA_DIR}/pdfs'
    TEMP_PATH = f'{COA_DATA_DIR}/tmp'
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    if not os.path.exists(COA_DATA_DIR): os.makedirs(COA_DATA_DIR)
    if not os.path.exists(COA_PDF_DIR): os.makedirs(COA_PDF_DIR)
    if not os.path.exists(TEMP_PATH): os.makedirs(TEMP_PATH)

    # Define constants.
    BASE = 'https://rawgarden.farm/lab-results/'

    # Support command line usage.
    # Future work: Allow data dirs to be specified from the command line.
    import argparse
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--days_ago', dest='days_ago', type=int)
        parser.add_argument('--get_all', dest='get_all', type=bool)
        args = parser.parse_args()
    except SystemExit:
        args = {}

    # Specify collection period.
    DAYS_AGO = args.get('days_ago', 365 * 5)
    GET_ALL =  args.get('get_all', True)

    # === Data Collection ===

    # Get the most recent Raw Garden products.
    start = datetime.now() - timedelta(days=DAYS_AGO)
    if GET_ALL:
        start = datetime(year=2018, month=1, day=1)
    products = get_rawgarden_products(start=start)
    filenames = products['coa_pdf'].to_list()

    # Download Raw Garden product COAs to `product_subtype` folders.
    download_rawgarden_coas(products, pause=0.24, verbose=True)

    # === Data Curation ===

    # Parse COA PDFs with CoADoc.
    # filenames.reverse()
    # coa_data, unidentified_coas = parse_rawgarden_coas(
    #     COA_PDF_DIR,
    #     filenames=filenames,
    #     temp_path=TEMP_PATH,
    #     verbose=True,
    # )
    directory = COA_PDF_DIR
    temp_path = TEMP_PATH
    verbose = True
    parsed, unidentified = [], []
    started = False
    filename = None
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
            file_path = os.path.join(path, filename)

            # Parse the COA, by any means necessary!
            parser = CoADoc()
            try:
                new_data = parser.parse_pdf(
                    file_path,
                    temp_path=temp_path,
                )
            except:
                try:
                    # FIXME: This should work without directly calling OCR.
                    temp_file = f'{temp_path}/ocr_coa.pdf'
                    parser.pdf_ocr(
                        file_path,
                        temp_file,
                        temp_path,
                        resolution=180,
                    )
                    new_data = parser.parse_pdf(
                        temp_file,
                        temp_path=temp_path,
                    )
                except Exception as e:
                    # Hot-fix: Remove temporary `magick-*` files.
                    try:
                        for i in os.listdir(temp_path):
                            magick_path = os.path.join(temp_path, i)
                            if os.path.isfile(magick_path) and i.startswith('magick-'):
                                os.remove(magick_path)
                    except FileNotFoundError:
                        pass
                    unidentified.append({'coa_pdf': filename})
                    if verbose:
                        print('Error:', filename)
                        print(e)
                    continue

            # Add the subtype key and record the data.
            subtype = path.split('\\')[-1]
            if isinstance(new_data, dict):
                new_data = [new_data]
            new_data[0]['product_subtype'] = subtype
            parsed.extend(new_data)
            if verbose:
                print('Parsed:', filename)

            # Deprecated: Reset the parer.
            # parser.quit()
            # gc.collect()

            # TODO: See if the following fields need to be augmented:
            # - date_retail
            # - lab_results_url

            # Save intermittently.
            if len(parsed) % 100 == 0:

                # Merge the `products`'s `product_subtype` with the COA data.
                # FIXME: Keep the URL (`lab_results_url`)!
                coa_df = pd.DataFrame(parsed)
                # coa_df = rmerge(
                #     pd.DataFrame(parsed),
                #     products,
                #     on='coa_pdf',
                #     how='left',
                #     replace='right',
                # )

                # Create custom column order.
                column_order = ['sample_hash', 'results_hash']
                # column_order += list(parser.column_order)
                column_index = coa_df.columns.get_loc('product_type') + 1
                column_order.insert(column_index, 'product_subtype')

                # Save the COA data.
                parser = CoADoc()
                timestamp = datetime.now().isoformat()[:19].replace(':', '-')
                datafile = f'{COA_DATA_DIR}/rawgarden-coa-data-{timestamp}.xlsx'
                parser.save(coa_df, datafile, column_order=column_order)
                print('Saved:', datafile)

                # Save the unidentified COA data.
                errors = [x['coa_pdf'] for x in unidentified]
                timestamp = datetime.now().isoformat()[:19].replace(':', '-')
                error_file = f'{COA_DATA_DIR}/rawgarden-unidentified-coas-{timestamp}.xlsx'
                products.loc[products['coa_pdf'].isin(errors)].to_excel(error_file)
    
    # === Data saving ===
    
    # # Create hashes.
    # coa_df = coa_df.where(pd.notnull(coa_df), None)
    # coa_df['results_hash'] = coa_df['results'].apply(
    #     lambda x: create_hash(x),
    # )
    # coa_df['sample_hash'] = coa_df.loc[:, coa_df.columns != 'sample_hash'].apply(
    #     lambda x: create_hash(x.to_dict()),
    #     axis=1,
    # )
    # datafile_hash = create_hash(coa_df)

    # Save Raw Garden COA data as JSON.
    coa_data = pd.DataFrame(parsed)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    data_dir = 'D://data/california/lab_results'
    outfile = os.path.join(data_dir, f'rawgarden-coa-data-{timestamp}.json')
    coa_data.to_json(outfile, orient='records')
    print('Saved Raw Garden lab results:', outfile)

    # Save Raw Garden COA datafile.
    coa_data = pd.DataFrame(parsed)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outfile = os.path.join(data_dir, f'rawgarden-coa-data-{timestamp}.xlsx')
    parser.save(coa_data[:1000], outfile)
    print('Saved Raw Garden lab results:', outfile)


    # === Data Aggregation ===

    # Aggregate historic lab results.
    aggregate = []
    files = os.listdir(COA_DATA_DIR)
    for file in files:
        if 'unidentified' in file or not file.endswith('.xlsx'):
            continue
        file_name = os.path.join(COA_DATA_DIR, file)
        df = pd.read_excel(file_name, sheet_name='Details')
        aggregate.append(df)

    # Aggregate and remove duplicates.
    aggregate = pd.concat(aggregate)
    aggregate = aggregate.drop_duplicates(subset=['sample_id'])
    print('Aggregated %i results.' % len(aggregate))

    # Save Raw Garden lab results.
    date = datetime.now().strftime('%Y-%m-%d')
    data_dir = 'D://data/california/lab_results'
    outfile = os.path.join(data_dir, f'rawgarden-lab-results-{date}.csv')
    aggregate.to_csv(outfile, index=False)
    print('Saved Raw Garden lab results:', outfile)
