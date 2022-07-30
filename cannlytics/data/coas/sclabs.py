"""
Get SC Labs Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/8/2022
Updated: 7/26/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Get lab results from SC Labs publicly published lab results.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ {analysis}_status
    ✓ coa_urls
    ✓ date_collected
    ✓ date_tested
    ✓ date_received
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    - distributor_city
    - distributor_state
    ✓ distributor_zipcode
    ✓ distributor_license_number
    ✓ images
    ✓ lab_results_url
    ✓ producer
    ✓ producer_address
    - producer_street
    ✓ producer_city
    - producer_state
    - producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ lab_id
    ✓ product_type
    ✓ batch_number
    ✓ metrc_ids
    - metrc_lab_id
    ✓ metrc_source_id
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight
    ✓ results
    ✓ status
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_cbg
    ✓ total_thcv
    ✓ total_cbc
    ✓ total_cbdv
    ✓ total_terpenes
    ✓ sample_id (generated)
    - strain_name (augmented)

Static Data Points:

    ✓ lab
    ✓ lab_image_url
    - lab_license_number
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_county (augmented)
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    - lab_email
    ✓ lab_website
    ✓ lab_latitude (augmented)
    ✓ lab_longitude (augmented)

Data Sources:
    
    - SC Labs Test Results
    URL: <https://client.sclabs.com/>

Future work:

    - Optional: Normalize the `results`, `images`.
    - Optional: Standardize the `product_type` and `status`.
    - Optional: Find the `county` given the `producer_zipcode`.
    - Future work: Identify a `strain_name` from the `product_name`.
    - Future work: Standardize `analyses`. 
    - Future work: Standardize analytes (`results` `key`).

"""
# Internal imports.
from urllib.parse import urljoin
from time import sleep

# External imports.
from bs4 import BeautifulSoup
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import snake_case, strip_whitespace
import requests


# It is assumed that the lab has the following details.
SC_LABS = {
    'coa_algorithm': 'sclabs.py',
    'coa_algorithm_entry_point': 'get_sc_labs_sample_details',
    'lims': 'SC Labs',
    'url': 'https://client.sclabs.com',
    'lab': 'SC Labs',
    'lab_image_url': 'https://www.sclabs.com/wp-content/uploads/2020/11/sc-labs-logo-white.png',
    # 'lab_license_number': '', # Get this data point dynamically.
    'lab_address': '100 Pioneer St., Ste. E, Santa Cruz, CA 95060',
    'lab_street': '100 Pioneer St., Ste. E',
    'lab_city': 'Santa Cruz',
    'lab_county': 'Santa Cruz',
    'lab_state': 'CA',
    'lab_zipcode': '95060',
    'lab_phone': '(866) 435-0709',
    'lab_email': 'info@sclabs.com',
    'lab_website': 'https://sclabs.com',
    'lab_latitude': '36.987869',
    'lab_longitude': '-122.033162',
}

# It is assumed that the CoA has the following parameters.
SC_LABS_COA = {
    'analyses': {

    },
    'coa_fields': {
        'batch_number': 'batch_number',
        'batch_size': 'batch_size',
        'business_name': 'distributor',
        'coa_id': 'lab_id',
        'license_number': 'distributor_license_number',
        'sum_of_cannabinoids': 'sum_of_cannabinoids',
        'total_cannabinoids': 'total_cannabinoids',
        'total_thc': 'total_thc',
        'total_cbd': 'total_cbd',
        'total_cbg': 'total_cbg',
        'total_thcv': 'total_thcv',
        'total_cbc': 'total_cbc',
        'total_cbdv': 'total_cbdv',
        'total_terpenoids': 'total_terpenes',
        '9_thc_per_unit': 'cannabinoids_status',
        'pesticides': 'pesticides_status',
        'mycotoxins': 'mycotoxins_status',
        'residual_solvents': 'residual_solvents_status',
        'heavy_metals': 'heavy_metals_status',
        'microbiology': 'microbiology_status',
        'foreign_material': 'foreign_matter_status',
        'foreign_material_method': 'foreign_matter_method',
        'total_terpenoids_percent': 'total_terpenes',
        'total_terpenoids_mgtog': '',
        'source_metrc_uid': 'metrc_source_id',
    },
    'coa_results_fields': {
        'compound': 'name',
        'mu': 'margin_of_error',
        'result-mass': 'mg_g',
        'result-percent': 'value',
        'action-limit': 'limit',
        'result-pf': 'status',
    },
}


def parse_data_block(div, tag='span') -> dict:
    """Parse an HTML data block into a dictionary.
    Args:
        div (bs4.element): An HTML element.
        tag (string): The type of tag that is repeated in the block.
    Returns:
        (dict): A dictionary of key and value pairs.
    """
    data = {}
    for el in div:
        try:
            label = el.find(tag).text
            value = el.text
            value = value.replace(label, '')
            value = value.replace('\n', '').strip()
            label = label.replace(':', '')
            data[snake_case(label)] = value
        except AttributeError:
            pass
    return data


def get_sc_labs_test_results(
        producer_id,
        reverse=True,
        limit=100,
        page_limit=100,
        pause=0.2,
        headers=None
    ) -> list:
    """Get all test results for a specific SC Labs client.
    Args:
        producer_id (str): A producer ID.
        reverse (bool): Whether to collect in reverse order, True by default (optional).
        limit (int): The number of samples per page to collect, 100 by default.
        page_limit (int): The maximum number of pages to collect, 100 by default.
        pause (float): A respectful pause to wait between requests.
    Returns:
        (list): A list of dictionaries of sample data.
    """

    #  Iterate over pages, getting all the samples on each page,
    # until the active page is repeated and the first sample is the same.
    active_page = None
    first_sample = None
    samples = []
    sample_pages = range(1, page_limit)
    if headers is None:
            headers = DEFAULT_HEADERS
    for sample_page in sample_pages:

        # Pause between requests to be respectful of the API server.
        if sample_page > 1 and pause:
            sleep(pause)

        # Get a client page with X amount of samples.
        url = '/'.join([SC_LABS['url'], 'client', str(producer_id)])
        params = {'limit': limit, 'page': sample_page}
        response = requests.get(url, headers=headers, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check if the page is a 404.
        top_spans = soup.find_all('span')
        for span in top_spans:
            if '404' in span.text:
                print('Client not found: %s' % (producer_id))
                break

        # FIXME: This may not be working as intended.
        # Break the iteration if the page max is reached.
        try:
            current_sample = soup.find('h3').text
        except AttributeError:
            current_sample = first_sample
        attributes = {'class': 'pagination-active'}
        current_page = soup.find('li', attrs=attributes)
        if (current_page == active_page) and (current_sample == first_sample):
            break
        active_page = current_page
        first_sample = current_sample

        # Get producer.
        details = soup.find('div', attrs={'id': 'detailQuickView'})
        try:
            producer = details.find('h2').text
        except AttributeError:
            try:
                producer = soup.find('h2').text
            except AttributeError:
                producer = 'Anonymous'

        # Get producer image.
        try:
            producer_image_url = details.find('img')['src'] \
                .replace('\n', '').strip()
        except AttributeError:
            producer_image_url = ''

        # Get producer website.
        try:
            attributes = {'class': 'pp-social-web'}
            element = details.find('span', attrs=attributes)
            producer_url = element.find('a')['href']
        except:
            producer_url = ''

        # Get all of the sample cards.
        cards = soup.find_all('div', attrs={'class': 'grid-item'})
        if reverse:
                cards.reverse()
        for card in cards:

            # Get the lab's internal ID.
            lab_id = card['id'].replace('div_', '')

            # Get the product name.
            product_name = card.find('h3').text

            # Get lab results URL.
            base_url = SC_LABS['url']
            href = card.find('a')['href']
            lab_results_url = urljoin(base_url, href)

            # Get the date tested.
            mm, dd, yyyy = card.find('h6').text.split('-')
            date = '-'.join([yyyy, mm, dd])

            # Get totals.
            totals = card.find('div', attrs={'class': 'sample-details'})
            values = totals.find_all('div')
            total_thc = values[0].text.split(':')[-1].replace('%', '')
            total_cbd = values[1].text.split(':')[-1].replace('%', '')
            total_terpenes = values[2].text.split(':')[-1].replace('%', '')

            # FIXME: Do any lab results have blank dates? Anticipate that?.
            # Create a sample ID.
            sample_id = create_sample_id(producer, product_name, date)

            # Aggregate sample data.
            sample = {
                'date_received': date,
                'lab_id': lab_id,
                'lab_results_url': lab_results_url,
                'producer_id': producer_id,
                'producer': producer,
                'producer_image_url': producer_image_url,
                'product_name': product_name,
                'producer_url': producer_url,
                'sample_id': sample_id,
                'total_cbd': total_cbd,
                'total_thc': total_thc,
                'total_terpenes': total_terpenes,
            }
            samples.append(sample)

    # Return all of the samples for the client.
    return samples


def get_sc_labs_client_details():
    """Find client details. This is useful when getting a sample's
    data directly.
    Returns:
        (dict): The client's details data.
    """
    # TODO: Implement.
    raise NotImplementedError


def get_sc_labs_sample_details(sample, headers=None) -> dict:
    """Get the details for a specific SC Labs test sample.
    Args:
        sample (str): A sample number or sample URL.
    Returns:
        (dict): A dictionary of sample details.
    """

    # Get the sample page.
    base_url = SC_LABS['url']
    if sample.startswith(base_url):
        url = sample
    else:
        if headers is None:
            headers = DEFAULT_HEADERS
        url = urljoin(base_url, f'sample/{sample}/')
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the bulk of the details.
    elements = soup.find_all('p', attrs={'class': 'sdp-summary-data'})
    obs = parse_data_block(elements)

    # Get the product name.
    obs['product_name'] = soup.find('h2').text

    # Format the distributor address.
    try:
        address = obs.get('address', '').split('*')[-1].strip()
        obs['distributor_address'] = address
        obs['distributor_city'] = address.split(',')[0]
        obs['distributor_zipcode'] = address.split(' ')[-1]
    except TypeError:
        obs['distributor_address'] = ''
        obs['distributor_city'] = ''
        obs['distributor_zipcode'] = ''
    
    # Get the producer details.
    element = soup.find('div', attrs={'id': 'cultivator-details'})
    producer_details = parse_data_block(element)
    obs['producer'] = producer_details['business_name']
    obs['producer_license_number'] = producer_details['license_number']

    # Format the producer address.
    try:
        address = producer_details['address'].split('*')[-1].strip()
        obs['producer_address'] = address
        obs['producer_city'] = address.split(',')[0]
        obs['producer_zipcode'] = address.split(' ')[-1]
    except TypeError:
        obs['producer_address'] = ''
        obs['producer_city'] = ''
        obs['producer_zipcode'] = ''

    # Get the producer image.
    el = soup.find('div', attrs={'id': 'clientprofileimage'})
    obs['producer_image_url'] = strip_whitespace(el.find('img')['src'])

    # Get the producer URL.
    links = soup.find_all('a', attrs={'class': 'greybutton'})
    for link in links:
        href = link['href']
        if 'sample' in href:
            sample_number = href.split('sample/')[-1].split('/')[0]
            obs['sample_number'] = sample_number
            obs['coa_urls'] = [{
                'url': urljoin(url, href),
                'filename': f'{sample_number}.pdf',
            }]
        elif 'client' in href:
            obs['producer_url'] = urljoin(url, href)

    # Get the Metrc IDs.
    try:
        metrc_ids = obs['source_metrc_uid'].split(',')
        obs['metrc_ids'] = [x.strip() for x in metrc_ids]
    except KeyError:
        obs['metrc_ids'] = []

    # Get the product type.
    try:
        attributes = {'class': 'sdp-producttype'}
        obs['product_type'] = soup.find('p', attrs=attributes).text
    except AttributeError:
        obs['product_type'] = 'Unknown'

    # Get the image.
    try:
        attributes = {'data-popup': 'fancybox'}
        image_url = soup.find('a', attrs=attributes)['href']
        obs['images'] = [{
            'url': image_url,
            'filename': image_url.split('/')[-1],
        }]
    except TypeError:
        obs['images'] = []

    # Get the date tested.
    try:
        element = soup.find('div', attrs={'class': 'sdp-masthead-data'})
        mm, dd, yyyy = element.find('p').text.split('/')
        obs['date_tested'] = '-'.join([yyyy, mm, dd])
    except AttributeError:
        obs['date_tested'] = ''

    # Get the overall status: Pass / Fail.
    try:
        status = soup.find('p', attrs={'class': 'sdp-result-pass'}).text
        obs['status'] = status.replace('\n', '').strip()
    except AttributeError:
        obs['status'] = ''

    # Format the dates.
    try:
        mm, dd, yyyy = obs['date_collected'].split('/')
        obs['date_collected'] = '-'.join([yyyy, mm, dd]) 
    except KeyError:
        obs['date_collected'] = ''
    try:
        mm, dd, yyyy = obs['date_received'].split('/')
        obs['date_received'] = '-'.join([yyyy, mm, dd])
    except KeyError:
        obs['date_received'] = ''
    
    # FIXME: Rename desired fields.
    for key, field in SC_LABS_COA['coa_fields'].items():
        try:
            value = obs.pop(key)
            if field:
                obs[field] = value
        except KeyError:
            pass

    # Get the CoA ID.
    try:
        attributes = {'class': 'coa-id'}
        obs['coa_id'] = soup.find('p', attrs=attributes).text \
            .split(':')[-1]
    except AttributeError:
        obs['coa_id'] = ''

    # Remove any keys that begin with a digit.
    for key in list(obs.keys()):
        if key[0].isdigit():
            del obs[key]

    # Optional: Try to get sample_weight.

    # Get all of the analyses and results.
    analyses = []
    results = []
    notes = None
    coa_results_fields = SC_LABS_COA['coa_results_fields']
    cards = soup.find_all('div', attrs={'class': 'analysis-container'})    
    for element in cards:

        # Get the analysis.
        analysis = element.find('h4').text
        if 'Notes' in analysis:
            div = element.find('div', attrs={'class': 'section-inner'})
            notes = div.find('p').text
        if 'Analysis' not in analysis:
            continue
        analysis = snake_case(analysis.split(' Analysis')[0])
        analyses.append(analysis)

        # Get the method for the analysis.
        bold = element.find('b')
        method = bold.parent.text.replace('Method: ', '')
        key = '_'.join([analysis, 'method'])
        obs[key] = method

        # Get all of the results for the analysis.
        # - value, units, margin_of_error, lod, loq
        table = element.find('table')
        rows = table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            result = {}
            for cell in cells:
                key = cell['class'][0].replace('table-', '')
                key = coa_results_fields.get(key, key)
                value = cell.text.replace('\n', '').strip()
                result[key] = value
                result['analysis'] = analysis
            results.append(result)
    
    # Parse legacy results if no results collected at this stage.
    if not results:

        # Get details.
        element = soup.find('div', attrs={'id': 'detailQuickView'})
        items = element.find_all('li')
        mm, dd, yyyy = items[0].text.split(': ')[-1].split('-')
        obs['date_tested'] = f'{yyyy}-{mm}-{dd}'
        obs['product_type'] = items[-1].text.split(': ')[-1]

        # Get analysis cards.
        cards = soup.find_all('div', attrs={'class': 'detail-row'})
        for card in cards:
            
            # Get the analysis.
            title = card.find('h3').text.lower()
            if 'not tested' in title:
                continue
            text = title.split('test')[0]
            analysis = snake_case(strip_whitespace(text))
            if analysis == 'label_claims':
                continue

            # Get the method for the analysis.
            method = card.find('p').text
            key = '_'.join([analysis, 'method'])
            obs[key] = method
            
            # FIXME:
            # Get all of the results for the analysis.
            # - value, units, margin_of_error, lod, loq
            table = card.find('table')
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                result = {}
                for cell in cells:
                    key = cell['class'][0].replace('table-', '')
                    key = coa_results_fields.get(key, key)
                    value = cell.text.replace('\n', '').strip()
                    result[key] = value
                    result['analysis'] = analysis
                results.append(result)

    # Separate `lod` and `loq`.
    lod_loq_values = [x['lodloq'].split(' / ') if x.get('lodloq') else None for x in results]
    for i, values in enumerate(lod_loq_values):
        if values is not None:
            result = results[i]
            result['lod'] = values[0]
            result['loq'] = values[1]
            del result['lodloq']
            results[i] = result
    
    # Clean results.
    c
    for result in results:
        try:
            margin = result['margin_of_error'].replace('±', '')
            result['margin_of_error'] = margin
        except KeyError:
            pass

        # FIXME: Parse `units` from `value`. E.g. '71.742%'

        # TODO: Ensure that the results are numbers.

        # TODO: Standardize the analyses!
        result['analysis'] = result['analysis']

        # Assign a `key` for the analyte.
        result['key'] = snake_case(result['name'])
    
    # FIXME: Clean `total_{analyte}`s and `sum_of_cannabinoids`.

    # FIXME: Lowercase `{analysis}_status`
    
    # FIXME: Re-key `address` to `producer_address`

    # Separate `batch_units` from `batch_size`.
    obs['batch_size'], obs['batch_units'] = tuple(obs['batch_size'].split(' '))
    
    # Create a `sample_id`.
    obs['sample_id'] = create_sample_id(
        private_key=obs['producer'],
        public_key=obs['product_name'],
        salt=obs['date_tested'],
    )

    # Aggregate the sample data.
    if not results:
        results = None
    obs['analyses'] = analyses
    obs['lab_results_url'] = url
    obs['notes'] = notes
    obs['results'] = results
    return { **SC_LABS, **obs}


if __name__ == '__main__':

    # === Test ===

    # [✓] TEST: Get all test results for a specific client.
    # test_results = get_sc_labs_test_results('2821')
    # assert test_results is not None

    # [✓] TEST: Get details for a specific sample ID.
    # sample_details = get_sc_labs_sample_details('858084')
    # assert sample_details is not None

    # [✓] TEST: Get details for a specific sample URL.
    sc_labs_coa_url = 'https://client.sclabs.com/sample/858084'
    data = get_sc_labs_sample_details(sc_labs_coa_url)
    assert data is not None
