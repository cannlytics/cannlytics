"""
Get MCR Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 8/1/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Tools to collect MCR Labs' publicly published lab results.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ date_tested
    ✓ images
    ✓ lab
    ✓ lab_website
    ✓ lab_results_url
    ✓ product_name
    ✓ product_type
    ✓ producer
    ✓ results
        ✓ analysis
        ✓ key
        ✓ name
        ✓ units
        ✓ value
        ✓ lod
        ✓ loq
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
import re
from time import sleep
from typing import Any, Optional

# External imports.
from bs4 import BeautifulSoup
import requests

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import (
    convert_to_numeric,
    format_iso_date,
    snake_case,
    strip_whitespace,
)


# Lab details.
MCR_LABS = {
    'coa_algorithm': 'mcrlabs.py',
    'coa_algorithm_entry_point': 'get_mcr_labs_sample_details',
    'lims': 'MCR Labs',
    'url': 'https://reports.mcrlabs.com',
    'lab': 'MCR Labs',
    'lab_website': 'https://mcrlabs.com',   
}


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
            details = get_mcr_labs_sample_details(sample_id=sample_id)
            rows.append({**sample, **details})
            if i > 1:
                sleep(pause)
            if verbose:
                print('Collected sample:', sample_id)
        except:
            print('Failed to collect sample:', sample_id)
            continue

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

        # Optional: Standardize product types.

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
        parser,
        sample_id: str,
        headers: Optional[Any] = None,
        **kwargs,
    ) -> dict:
    """Get the details for a specific MCR Labs test sample.
    Args:
        parser (CoADoc): A CoADoc client for standardization.
        sample_id (str): A sample ID number or the `lab_results_url`.
        headers (dict): Headers for the HTTP request (optional).
    Returns:
        (dict): A dictionary of sample details.
    """
    # Get the sample page.
    obs = {}
    if sample_id.startswith('https'):
        url = sample_id
    else:
        base = MCR_LABS['url']
        url = f'{base}/reports/{sample_id}'
    if headers is None:
        headers = DEFAULT_HEADERS
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the lab.
    try:
        element = soup.find('div', attrs={'class': 'rd_date'})
        obs['lab'] = strip_whitespace(element.text).split('by ')[-1]
    except:
        print('Failed to find lab:', sample_id)
        obs['lab'] = ''
    
    # Get the sample image, if not already collected.
    if not obs.get('images'):
        attrs = {'class': 'report_image'}
        image_url = soup.find('img', attrs=attrs)['src']
        filename = image_url.split('/')[-1]
        obs['images'] = [{'url': image_url, 'filename': filename}]

    # Get the date tested, if not already collected.
    if not obs.get('date_tested'):
        text = soup.find('div', attrs={'class': 'rd_date'}).text
        date = text.split('Tested ')[-1].split(' for')[0]
        obs['date_tested'] = format_iso_date(date)

    # Get the product name and producer, if not already collected.
    if not obs.get('product_name'):
        details = soup.find('div', attrs={'id': 'client'})
        product_name = details.find('b').text
        obs['product_name'] = product_name
        obs['producer'] = details.find('h4').text.replace(product_name, '')

    # Get the product type, if not already collected.
    if not obs.get('product_type'):
        el = soup.find('div', attrs={'class': 'abb'})
        obs['product_type'] = el.attrs['class'][-1].replace('repor_', '')
    
    # Optional: Standardize the product types?

    # Get the total cannabinoids and total terpenes, if not already collected.
    if not obs.get('total_cannabinoids'):
        details = soup.find('div', attrs={'class': 'client_detail'})
        values = details.find_all('h3')
        keys = details.find_all('b')
        for i, el in enumerate(values):
            key = snake_case(strip_whitespace(keys[i].text))
            value = convert_to_numeric(strip_whitespace(el.text), strip=True)
            obs[key] = value

    # Optional: Get any product serving size (for edibles?).

    # Get the analysis methods.
    details = soup.find_all('div', attrs={'class': 'calc-expl'})
    for detail in details:
        pars = detail.find_all('p')
        for par in pars:
            if 'quantified' in par.text:
                text = strip_whitespace(par.text)
                analysis = snake_case(text.split(' are quantified')[0])
                method = text.split('quantified using ')[-1]\
                        .replace('.', '').title()
                obs[f'{analysis}_method'] = method
    
    # Get the sample test results.
    analyses = []
    results = []

    # Get the cannabinoids.
    try:
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
    except UnboundLocalError:
        pass

    # Get the results for all other analyses.
    values = ['name', 'value', 'lod' ,'loq']
    tables = soup.find_all('table', attrs={'class': 'safetytable'})
    for table in tables:
        rows = table.find_all('tr')

        # Get the analysis of the table.
        el = tables[1].find_previous('h4')
        text = strip_whitespace(el.text)
        text = text \
            .replace('Screen', '') \
            .replace('Contaminant', '') \
            .replace('Profile', '')
        analysis = snake_case(text.strip())
        analyses.append(analysis)

        # Get each result field.
        current_units = None
        for row in rows:
            result = {'analysis': analysis}
            cells = row.find_all('td')

            # Get all of the detects, identifying the current units.
            # FIXME: heavy metals, microbes, pesticides, residual solvents
            # - [ ] wrong `analysis`
            # - [ ] Missing `value` and `units`
            # FIXME: 'aflatoxin_b_1_b_2_g_1_g_2_and_ochratoxin_a
            if len(cells) > 1:
                for i, cell in enumerate(cells):
                    try:
                        key = values[i]
                    except IndexError:
                        key = f'limit_{i}'
                    if key == 'name':
                        result['key'] = snake_case(cell.text)
                    elif key == 'value':
                        value = cell.text
                        units = re.sub('[\d\.]', '', value) \
                            .replace('%', 'percent') \
                            .replace('<', '') \
                            .strip()
                        if not units or units == 'ND' or units == 'Not Detected':
                            limit = result.get('lod', result.get('loq', result.get('limit', '')))
                            units = re.sub('[\d\.]', '', limit).replace('%', 'percent').strip()
                        if units != 'Negative' and units != 'Positive':
                            result['value'] = convert_to_numeric(re.sub('[^\d\.]', '', value))
                            result['units'] = units
                            current_units = units
                        else:
                            result['value'] = units
                            result['units'] = current_units
                    else:
                        result[key] = convert_to_numeric(cell.text, strip=True)

                # Record the result
                results.append(result)

            # Get all of the non-detects, using the current units.
            elif row.has_attr('class') and row.attrs['class'][0] == 'not-detected--substances':
                par = row.find('td').text.replace('Not detected:', '')
                block = [strip_whitespace(x) for x in par.split(',')]
                for analyte in block:
                    results.append({
                        'analysis': analysis,
                        'key': snake_case(analyte),
                        'name': analyte,
                        'value': 'ND',
                        'units': current_units,
                    })

    # Create or re-mint the `sample_id`.
    obs['sample_id'] = create_sample_id(
        private_key=obs['producer'],
        public_key=obs['product_name'],
        salt=obs['date_tested'],
    )

    # Return the sample details.
    obs['analyses'] = list(set(analyses))
    obs['lab_results_url'] = url
    obs['results'] = results
    return {**MCR_LABS, **obs}


if __name__ == '__main__':

    # === Tests ===
    from cannlytics.utils.utils import to_excel_with_style
    from datetime import datetime
    import pandas as pd

    # Specify where your test data lives.
    DATA_DIR = '../../../.datasets/lab_results'

    # [✓] TEST: Get the total number of samples.
    # page_count = get_mcr_labs_sample_count(per_page=30)
    # assert page_count is not None

    # [✓] TEST: Get the samples on a given page.
    # samples = get_mcr_labs_samples('6')
    # assert samples is not None

    # [✓] TEST: Get a sample's details.
    details = get_mcr_labs_sample_details(None, 'rooted-labs-distillate_2')
    assert details is not None

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
