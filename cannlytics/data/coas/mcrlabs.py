"""
Get MCR Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 7/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Tools to collect MCR Labs' publicly published lab results.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ date_tested
    ✓ image
    ✓ lab
    ✓ lab_website
    ✓ lab_results_url
    ✓ product_name
    ✓ product_type
    ✓ producer
    ✓ results
        - analysis
        ✓ key
        ✓ name
        ✓ units
        ✓ value
    ✓ sample_id (generated)
    ✓ total_cannabinoids
    ✓ total_terpenes

Data Sources:
    
    - MCR Labs Test Results
    URL: <https://reports.mcrlabs.com>

Future development:

    - Implement the function to get all of a given client's lab results.
    - Optional: Create necessary data dirs automatically.
    - Optional: Function to download any pre-existing results.

"""
# Internal imports.
import json
import math
from time import sleep
from typing import Any, Optional

# External imports.
from bs4 import BeautifulSoup
import requests

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import snake_case, strip_whitespace


# Lab details.
MCR_LABS = {
    'coa_algorithm': 'mcrlabs.py',
    'coa_algorithm_entry_point': 'get_mcr_labs_sample_details',
    'lims': 'MCR Labs',
    'url': 'https://reports.mcrlabs.com',
    'lab': 'MCR Labs',
    'lab_website': 'https://mcrlabs.com',   
}


def format_iso_date(date, sep='/'):
    """Format a human-written date into an ISO formatted date."""
    mm, dd, yyyy = tuple(date.split(sep))
    if len(mm) == 1:
        mm = f'0{mm}'
    if len(dd) == 1:
        dd = f'0{dd}'
    if len(yyyy) == 2:
        yyyy = f'20{yyyy}'
    return '-'.join([yyyy, mm, dd])


def get_mcr_labs_sample_count(
        per_page: Optional[int] = 30,
        headers: Optional[Any] = None,
    ) -> dict:
    """Get the number of samples and pages of MCR Labs samples.
    Args:
        per_page (int): The number of results displayed per page.
        headers (dict): Headers for the HTTP request (optional).
    Returns:
        (dict): A dictionary with `count` and `pages` keys.
    """
    base = MCR_LABS['url']
    url = f'{base}/products-weve-tested'
    if headers is None:
        headers = DEFAULT_HEADERS
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.find('span', attrs={'id': 'found_posts'})
    count = int(element.text.replace(',', ''))
    pages = math.ceil(count / per_page)
    return {'count': count, 'pages': pages}


def get_mcr_labs_test_results(
        starting_page: Optional[int] = 1,
        ending_page: Optional[int] = None,
        pause: Optional[float] = 3,
        verbose: Optional[bool] = True
    ) -> list:
    """Get all MCR Labs test results.
    Args:
        starting_page (int): The page to start collecting results,
            `1` by default (optional).
        ending_page (int): The page to end collecting results,
            `None` by default, which will collect to the end (optional).
        pause (float): The amount of time to wait between requests.
        verbose (bool): Whether to print out status, `True` by default
            (optional).
    Returns:
        (list): The complete sample data.
    """
    # Iterate over all of the pages.
    page_count = get_mcr_labs_sample_count()
    total_pages = page_count['pages']
    if not ending_page:
        ending_page = total_pages
    if verbose:
        print('Getting samples for pages %i to %i.' % (starting_page, ending_page))
    samples = []
    for page_id in range(starting_page, ending_page + 1):
        sample_data = get_mcr_labs_samples(page_id)
        samples += sample_data
        if page_id > 1 and page_id <= ending_page:
            sleep(pause)
    if verbose:
        print('Found %i samples.' % len(samples))

    # Get all of the sample details.
    rows = []
    for i, sample in enumerate(samples):
        try:
            sample_id = sample['lab_results_url'].split('/')[-1]
            details = get_mcr_labs_sample_details(sample_id)
            rows.append({**sample, **details})
            if i > 1:
                sleep(pause)
            if verbose:
                print('Collected sample:', sample_id)
        except:
            print('Failed to collect sample:', sample_id)
            continue
    
    # Optional: Clean the data after collection?
    # - Map product types.
    # - Parse units from results
    # data = pd.DataFrame(rows)
    
    # Return all of the sample data.
    return rows


def get_mcr_labs_samples(
        page_id: Any,
        cat: Optional[str] = 'all',
        order: Optional[str] = 'date-desc',
        search: Optional[str] = '',
        headers: Optional[Any] = None,
    ) -> list:
    """Get all test results from MCR Labs on a specific page.
    Args:
        page_id (str|int): The page number to get samples.
        cat (str): The category, `all` by default (optional). Options:
            `flower`, `concentrate`, `extract`, `mip`.
        order (str): The order to list results, `date-desc` by default
            (optional). Options: `date-desc`, `samplename`, `client`,
            `totalcann-desc`, `totalterp-desc`, `maxthc-desc`, `maxcbd-desc`.
        search (str): A particular search query.
        headers (dict): Headers for the HTTP request (optional).
    Returns:
        (list): A list of dictionaries of sample data.
    """
    # Get a page.
    base = MCR_LABS['url']
    url = f'{base}/ProductWeVeTested/AjaxSearch'
    params = {
        'category': cat,
        'order': order,
        'page': str(page_id),
        'searchString': search,
    }
    if headers is None:
        headers = DEFAULT_HEADERS
    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get all of the products on the page.
    samples = []
    products = soup.find_all('li', attrs={'class': 'grid-item'})
    for product in products:

        # Get sample details.
        sample = {}
        details = product.find('div', attrs={'class': 'reportTable'})
        sample['product_name'] = details.find('div', \
            attrs={'class': 'fth_name'}).text
        sample['producer'] = details.find('div', \
            attrs={'class': 'fth_client'}).text
        sample['product_type'] = details.find('div', \
            attrs={'class': 'fth_category'}).text
        sample['total_cannabinoids'] = strip_whitespace(details.find('div', \
            attrs={'class': 'fth_cannabinoids'}).text)
        sample['total_terpenes'] = strip_whitespace(details.find('div', \
            attrs={'class': 'fth_terpenes'}).text)
        try:
            sample['date_tested'] = format_iso_date(details.find('div', \
                attrs={'class': 'fth_date'}).text)
        except ValueError:
            print('Error:', sample)
            sample['date_tested'] = ''

        # Try to get the producer's URL.
        try:
            element = product.find('span', attrs={'class': 'url-linked'})
            href = element.attrs['data-url']
            sample['producer_url'] = '/'.join([base, href])
        except AttributeError:
            sample['producer_url'] = ''

        # Get the lab results URL.
        href = product.find('a')['href']
        sample['lab_results_url'] = '/'.join([base, href])

        # Get the image.
        image_url = product.find('img')['src']
        filename = image_url.split('/')[-1]
        sample['images'] = [{'url': image_url, 'filename': filename}]

        # Create a sample ID.
        sample['sample_id'] = create_sample_id(
            private_key=sample['producer'],
            public_key=sample['product_name'],
            salt=sample['date_tested'],
        )

        # Aggregate sample data.
        samples.append({**MCR_LABS, **sample})

    # Return the samples.
    return samples


def get_mcr_labs_producer_test_results():
    """Get all test results from MCR Labs for a specific producer.
    Returns:
        (list): A list of dictionaries of sample data.
    """
    # TODO: Implement.
    raise NotImplementedError


def get_mcr_labs_client_details():
    """Find details for any known producer of a given lab sample..
    Returns:
        (dict): The client's details data.
    """
    # TODO: Implement.
    raise NotImplementedError


def get_mcr_labs_sample_details(
        sample_id: str,
        headers: Optional[Any] = None,
    ) -> dict:
    """Get the details for a specific MCR Labs test sample.
    Args:
        sample_id (str): A sample ID number.
        headers (dict): Headers for the HTTP request (optional).
    Returns:
        (dict): A dictionary of sample details.
    """
    # Get the sample page.
    sample = {}
    base = MCR_LABS['url']
    url = f'{base}/reports/{sample_id}'
    if headers is None:
        headers = DEFAULT_HEADERS
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Optional: Get product serving size.

    # Get the lab.
    try:
        element = soup.find('div', attrs={'class': 'rd_date'})
        sample['lab'] = strip_whitespace(element.text).split('by ')[-1]
    except:
        print('Failed to find lab:', sample_id)
        sample['lab'] = ''

    # Get sample test results.
    analyses = []
    results = []

    # Get the methods.
    details = soup.find_all('div', attrs={'class': 'calc-expl'})
    for detail in details:
        pars = detail.find_all('p')
        for par in pars:
            if 'quantified' in par.text:
                text = strip_whitespace(par.text)
                analysis = snake_case(text.split(' are quantified')[0])
                method = text.split('quantified using ')[-1]\
                        .replace('.', '').title()
                sample[f'{analysis}_method'] = method
                analyses.append(analysis)

    # Get the cannabinoids.
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            if 'dataProvided' in script.string:
                break
    block = script.string.split('const dataProvided = ')[-1].split(';')[0]
    block = strip_whitespace(block).replace(' ', '').replace(',]', ']')
    cannabinoids = json.loads(block)
    analyses.append('cannabinoids')
    for analyte in cannabinoids:
        results.append({
            'analysis': 'cannabinoids',
            'key': analyte['key'],
            'name': analyte['label'],
            'value': analyte['perc'],
            'units': 'percent',
        })

    # Get the results for all other analyses.
    # FIXME: Add `analysis` field to results.
    values = ['name', 'result', 'lod' ,'loq']
    tables = soup.find_all('table', attrs={'class': 'safetytable'})
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            result = {}
            cells = row.find_all('td')
            if len(cells) > 1:
                for i, cell in enumerate(cells):
                    try:
                        key = values[i]
                    except IndexError:
                        key = f'limit_{i}'
                    result[key] = cell.text
                if result:
                    results.append(result)

    # Return the sample details.
    sample['results'] = results
    return {**MCR_LABS, **sample}


if __name__ == '__main__':

    # === Tests ===
    from cannlytics.utils.utils import to_excel_with_style
    from datetime import datetime
    import pandas as pd

    # Specify where your test data lives.
    DATA_DIR = '../../../.datasets/lab_results'
    RAW_DATA = '../../../.datasets/lab_results/raw_data/mcr_labs'
    TRAINING_DATA = '../../../.datasets/lab_results/training_data'

    # [✓] TEST: Get the total number of samples.
    # page_count = get_mcr_labs_sample_count(per_page=30)
    # assert page_count is not None

    # [✓] TEST: Get the samples on a given page.
    # samples = get_mcr_labs_samples('6')
    # assert samples is not None

    # [✓] TEST: Get a sample's details.
    # details = get_mcr_labs_sample_details('rooted-labs-distillate_2')
    # assert details is not None

    # [✓] TEST: Get a range of the samples.
    # print('Getting range of the samples.')
    # all_results = get_mcr_labs_test_results(
    #     starting_page=150,
    #     ending_page=250,
    #     pause=0.2,
    # )
    # timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    # datafile = f'{DATA_DIR}/mcr-lab-results-{timestamp}.xlsx'
    # to_excel_with_style(pd.DataFrame(all_results), datafile)
    # print('Finished getting range of samples.')

    # [✓] TEST: Get only the most recent samples.
    # print('Getting the most recent samples.')
    # recent_results = get_mcr_labs_test_results(ending_page=2)
    # timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    # datafile = f'{DATA_DIR}/mcr-lab-results-{timestamp}.xlsx'
    # to_excel_with_style(pd.DataFrame(recent_results), datafile)
    # print('Tested getting the most recent samples.')
