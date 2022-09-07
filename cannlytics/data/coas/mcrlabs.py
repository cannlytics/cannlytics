"""
Get MCR Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 8/30/2022
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

    - [ ] Create a parse CoA routine that could handle a MCR labs PDF.
    - [ ] Implement a function to get all of a given client's lab results.
    - Optional: Create necessary data dirs automatically.
    - Optional: Function to download any pre-existing results.

"""
# Standard imports.
from datetime import datetime
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
from cannlytics.utils.constants import ANALYSES, ANALYTES, DEFAULT_HEADERS
from cannlytics.utils.utils import (
    convert_to_numeric,
    format_iso_date,
    snake_case,
    strip_whitespace,
)


# It is assumed that the lab has the following details.
MCR_LABS = {
    'coa_algorithm': 'mcrlabs.py',
    'coa_algorithm_entry_point': 'get_mcr_labs_sample_details',
    'lims': 'MCR Labs',
    'url': 'https://reports.mcrlabs.com',
    'lab': 'MCR Labs',
    'lab_website': 'https://mcrlabs.com',
    'public': True,
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


def get_mcr_labs_sample_details(
        parser,
        lab_id: str,
        headers: Optional[Any] = None,
        standard_analyses: Optional[Any] = None,
        standard_analytes: Optional[Any] = None,
        **kwargs,
    ) -> dict:
    """Get the details for a specific MCR Labs test sample.
    Args:
        parser (CoADoc): A CoADoc client for standardization.
        lab_id (str): A sample ID number or the `lab_results_url`.
        headers (dict): Headers for the HTTP request (optional).
        standard_analyses (dict): An optional mapping of lab-specific
            analyses to standard analyses.
        standard_analytes (dict): An optional mapping of lab-specific
            analyses to standard analytes.
    Returns:
        (dict): A dictionary of sample details.
    """
    # Get the sample page.
    obs = {}
    if lab_id.startswith('https'):
        url = lab_id
    else:
        base = MCR_LABS['url']
        url = f'{base}/reports/{lab_id}'
    if headers is None:
        headers = DEFAULT_HEADERS
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the lab.
    try:
        element = soup.find('div', attrs={'class': 'rd_date'})
        obs['lab'] = strip_whitespace(element.text).split('by ')[-1]
    except:
        print('Failed to find lab:', lab_id)
        obs['lab'] = ''
    
    # Get a map of lab-specific analyses, analytes, and fields to the standard.
    if standard_analyses is None:
        standard_analyses = ANALYSES
    if standard_analytes is None:
        standard_analytes = ANALYTES
    
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
    # Optional: Standardize the product types?
    if not obs.get('product_type'):
        el = soup.find('div', attrs={'class': 'abb'})
        obs['product_type'] = el.attrs['class'][-1].replace('repor_', '')

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
                analysis = standard_analyses.get(analysis, analysis)
                method = text.split('quantified using ')[-1]\
                        .replace('.', '').title()
                obs[f'{analysis}_method'] = method
    
    # Get the sample test results.
    analyses = []
    results = []

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

    # Determine the cannabinoids units.
    units = None
    try:
        assert '%' in soup.find('div', attrs={'class': 'rd_can_table'}).text
        units = 'percent'
    except AttributeError:
        table = soup.find('table', attrs={'class': 'safetytable'})
        thead = table.find('thead')
        units = snake_case(thead.find_all('th', limit=2)[-1].text)

    # Record the cannabinoids.
    for analyte in cannabinoids:
        if analyte['label'] == 'TotalCannabinoids':
            continue
        key = snake_case(analyte['key'].replace('-', ''))
        key = standard_analytes.get(key, key)
        results.append({
            'analysis': 'cannabinoids',
            'key': key,
            'name': analyte['label'],
            'value': analyte['perc'],
            'units': units,
        })

    # Get the results for all other analyses.
    values = ['name', 'value', 'lod' ,'loq']
    tables = soup.find_all('table', attrs={'class': 'safetytable'})
    for table in tables:

        # Get the analysis of the table.
        el = table.find_previous('h4')
        try:
            assert el.parent['id'] == 'client'
            analysis = 'cannabinoids'
        except KeyError:
            text = strip_whitespace(el.text)
            text = text \
                .replace('Screen', '') \
                .replace('Contaminant', '') \
                .replace('Profile', '')
            analysis = snake_case(text.strip())
            analysis = standard_analyses.get(analysis, analysis)
        analyses.append(analysis)

        # Optional: Break up aflatoxins and ochratoxin A.
        # Aflatoxin (B1, B2, G1, G2) &amp; Ochratoxin A

        # Get each result field.
        current_units = None
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            result = {'analysis': analysis}

            # Precisely extract results if possible.
            try:
                name = row.find('td', attrs={'class': 'sr_label'}).text.strip()
            except AttributeError:
                name = None
            try:
                value = row.find('td', attrs={'class': 'sr_result'}).text.strip()
            except:
                value = None
            units = None
            try:
                lod = row.find('td', attrs={'class': 'sr_limit'}).text
                loq = row.find('td', attrs={'class': 'sr_limit'}).text
                result['lod'] = convert_to_numeric(lod, strip=True)
                result['loq'] = convert_to_numeric(loq, strip=True)
                result['units'] = re.sub('[\d\.]', '', lod).strip()
            except AttributeError:
                pass
            if name and value:
                analyte = snake_case(name)
                analyte = standard_analytes.get(analyte, analyte)
                result['key'] = analyte
                result['value'] = convert_to_numeric(value)
                results.append(result)

            # Otherwise, parse results to the best of our abilities.
            if name is None and value is None:
                cells = row.find_all('td')
                if len(cells) > 1:
                    for i, cell in enumerate(cells):
                        value, units = None, None
                        try:
                            key = values[i]
                        except IndexError:
                            key = f'limit_{i}'
                        if key == 'name':
                            analyte = snake_case(cell.text)
                            analyte = standard_analytes.get(analyte, analyte)
                            result['key'] = analyte
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
                                value = convert_to_numeric(re.sub('[^\d\.]', '', value))
                                result['value'] = value
                                result['units'] = units
                                current_units = units
                            else:
                                result['value'] = units
                                result['units'] = current_units
                        else:
                            result[key] = convert_to_numeric(cell.text, strip=True)

                    # Record the result, if present.
                    if not value and not units:
                        continue
                    results.append(result)

                # Get all of the non-detects, using the current units.
                # Note: This is crudely using units from the prior table.
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
    
    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Return the sample details with a new or re-minted `sample_id`.
    obs['analyses'] = list(set(analyses))
    obs['lab_results_url'] = url
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(obs['results']),
        public_key=obs['product_name'],
        salt=obs['producer'],
    )
    obs['coa_parsed_at'] = datetime.now().isoformat()
    return {**MCR_LABS, **obs}


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

        # Get the sample details.
        obs = {}
        details = product.find('div', attrs={'class': 'reportTable'})

        # Get the product name.
        attrs = {'class': 'fth_name'}
        obs['product_name'] = details.find('div', attrs=attrs).text

        # Get the producer.
        attrs = {'class': 'fth_client'}
        obs['producer'] = details.find('div', attrs=attrs).text

        # Get the product type.
        # Optional: Standardize product types.
        attrs = {'class': 'fth_category'}
        obs['product_type'] = details.find('div', attrs=attrs).text

        # Get the total cannabinoids.
        attrs = {'class': 'fth_cannabinoids'}
        value = details.find('div', attrs=attrs).text
        obs['total_cannabinoids'] = strip_whitespace(value)

        # Get the total terpenes.
        attrs = {'class': 'fth_terpenes'}
        value = details.find('div', attrs=attrs).text
        obs['total_terpenes'] = strip_whitespace(value)

        # Get the date tested.
        try:
            obs['date_tested'] = format_iso_date(details.find('div', \
                attrs={'class': 'fth_date'}).text)
        except ValueError:
            print('Error parsing date:', obs)
            obs['date_tested'] = ''

        # Try to get the producer's URL.
        try:
            element = product.find('span', attrs={'class': 'url-linked'})
            href = element.attrs['data-url']
            obs['producer_url'] = '/'.join([base, href])
        except AttributeError:
            obs['producer_url'] = ''

        # Get the lab results URL.
        href = product.find('a')['href']
        obs['lab_results_url'] = '/'.join([base, href])

        # Get the image.
        image_url = product.find('img')['src']
        filename = image_url.split('/')[-1]
        obs['images'] = [{'url': image_url, 'filename': filename}]

        # Turn dates to ISO format.
        date_columns = [x for x in obs.keys() if x.startswith('date')]
        for date_column in date_columns:
            try:
                obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
            except:
                pass

        # Aggregate sample data.
        samples.append({**MCR_LABS, **obs})

    # Return the samples.
    return samples


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
    # Determine the pages to collect.
    page_count = get_mcr_labs_sample_count()
    total_pages = page_count['pages']
    if not ending_page:
        ending_page = total_pages
    if verbose:
        print('Getting samples for pages %i to %i.' % (starting_page, ending_page))
    samples = []

    # Iterate over all of the pages, index starting at 1.
    for page_id in range(starting_page, ending_page + 1):
        sample_data = get_mcr_labs_samples(page_id)
        samples += sample_data
        if page_id > 1 and page_id <= ending_page:
            sleep(pause)
    if verbose:
        print('Found %i samples.' % len(samples))

    # Get all of the sample details.
    # Optional: Log errors?
    rows = []
    for i, sample in enumerate(samples):
        try:
            lab_id = sample['lab_results_url'].split('/')[-1]
            details = get_mcr_labs_sample_details(None, lab_id)
            rows.append({**sample, **details})
            if i > 1:
                sleep(pause)
            if verbose:
                print('Collected sample:', lab_id)
        except:
            print('Failed to collect sample:', lab_id)
            continue

    # Return all of the sample data.
    return rows


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
    # sample = get_mcr_labs_sample_details(None, 'rooted-labs-distillate_2')
    # assert sample is not None

    # [✓] TEST: Get an infused products's results (`product_type == 'mip'`).
    # details = get_mcr_labs_sample_details(None, '67545')
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
