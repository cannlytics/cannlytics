"""
Get SC Labs Test Result Data
Copyright (c) 2022 Cannlytics

Author: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/8/2022
Updated: 7/12/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Periodically collect recent lab results from
    SC Labs publicly published lab results.

Data Sources:
    
    - SC Labs Test Results
    URL: <https://client.sclabs.com/>

"""
# Internal imports.
from datetime import datetime
from hashlib import sha256
import hmac
from time import sleep

# External imports.
from bs4 import BeautifulSoup
from cannlytics.utils.utils import snake_case
# from cannlytics.firebase import update_documents
import pandas as pd
import requests


# Constants.
BASE = 'https://client.sclabs.com'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
STATE = 'CA'
DATA_DIR = '.datasets/lab_results'
RAW_DATA = '.datasets/lab_results/raw_data/sc_labs'
TRAINING_DATA = '.datasets/lab_results/training_data'

# Pertinent sample details (original key to final key).
DETAILS = {
    'batch_number': 'batch_number',
    'batch_size': 'batch_size',
    'business_name': 'distributor',
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
    'foreign_material': 'foreign_material_status',
}


def create_sample_id(private_key, public_key, salt='') -> str:
    """Create a hash to be used as a sample ID.
    The standard is to use:
        1. `private_key = producer`
        2. `public_key = product_name`
        3. `salt = date_tested`
    Args:
        private_key (str): A string to be used as the private key.
        public_key (str): A string to be used as the public key.
        salt (str): A string to be used as the salt, '' by default (optional).
    Returns:
        (str): A sample ID hash.
    """
    secret = bytes(private_key, 'UTF-8')
    message = snake_case(public_key) + snake_case(salt)
    sample_id = hmac.new(secret, message.encode(), sha256).hexdigest()
    return sample_id


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


def strip_whitespace(string):
    """Strip whitespace from a string."""
    return string.replace('\n', '').strip()


#-----------------------------------------------------------------------
# Automate collection
#-----------------------------------------------------------------------

def get_sc_labs_test_results(
        producer_id,
        reverse=True,
        limit=100,
        page_limit=100,
        pause=0.2,
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
    for sample_page in sample_pages:

        # Pause between requests to be respectful of the API server.
        if sample_page > 1 and pause:
            sleep(pause)

        # Get a client page with X amount of samples.
        url = '/'.join([BASE, 'client', str(producer_id)])
        params = {'limit': limit, 'page': sample_page}
        response = requests.get(url, headers=HEADERS, params=params)
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
        current_page = soup.find('li', attrs={'class': 'pagination-active'})
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
            producer_image_url = details.find('img')['src'].replace('\n', '').strip()
        except AttributeError:
            producer_image_url = ''

        # Get producer website.
        try:
            element = details.find('span', attrs={'class': 'pp-social-web'})
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
            lab_results_url = BASE + card.find('a')['href']

            # Get the date tested.
            mm, dd, yyyy = card.find('h6').text.split('-')
            date = '-'.join([yyyy, mm, dd])

            # Get totals.
            totals = card.find('div', attrs={'class': 'sample-details'})
            values = totals.find_all('div')
            total_thc = values[0].text.split(':')[-1].replace('%', '')
            total_cbd = values[1].text.split(':')[-1].replace('%', '')
            total_terpenes = values[2].text.split(':')[-1].replace('%', '')

            # FIXME: Do some lab results have blank dates?
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


def get_sc_labs_sample_details(sample) -> dict:
    """Get the details for a specific SC Labs test sample.
    Args:
        sample (str): A sample number.
    Returns:
        (dict): A dictionary of sample details.
    """

    # Get the sample page.
    url = '/'.join([BASE, 'sample', sample])
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the bulk of the details.
    elements = soup.find_all('p', attrs={'class': 'sdp-summary-data'})
    details = parse_data_block(elements)

    # Format the distributor address.
    try:
        address = details.get('address', '').split('*')[-1].strip()
        details['distributor_address'] = address
        details['distributor_city'] = address.split(',')[0]
        details['distributor_zip_code'] = address.split(' ')[-1]
    except TypeError:
        details['distributor_address'] = ''
        details['distributor_city'] = ''
        details['distributor_zip_code'] = ''
    
    # Get the producer details.
    try:
        element = soup.find('div', attrs={'id': 'cultivator-details'})
        producer_details = parse_data_block(element)
    
        # Format the producer address.
        address = producer_details['address'].split('*')[-1].strip()
        details['address'] = address
        details['city'] = address.split(',')[0]
        details['zip_code'] = address.split(' ')[-1]
    except TypeError:
        details['address'] = ''
        details['city'] = ''
        details['zip_code'] = ''

    # Get the Metrc IDs.
    try:
        metrc_ids = details['source_metrc_uid'].split(',')
        details['metrc_ids'] = [x.strip() for x in metrc_ids]
    except KeyError:
        details['metrc_ids'] = []

    # Get the product type.
    try:
        details['product_type'] = soup.find('p', attrs={'class': 'sdp-producttype'}).text
    except AttributeError:
        details['product_type'] = 'Unknown'

    # Get the image.
    try:
        image_url = soup.find('a', attrs={'data-popup': 'fancybox'})['href']
        details['images'] = [{'url': image_url, 'filename': image_url.split('/')[-1]}]
    except TypeError:
        details['images'] = []

    # Get the date tested.
    try:
        element = soup.find('div', attrs={'class': 'sdp-masthead-data'})
        mm, dd, yyyy = element.find('p').text.split('/')
        details['date_tested'] = '-'.join([yyyy, mm, dd])
    except AttributeError:
        details['date_tested'] = ''

    # Get the overall status: Pass / Fail.
    try:
        status = soup.find('p', attrs={'class': 'sdp-result-pass'}).text
        details['status'] = status.replace('\n', '').strip()
    except AttributeError:
        details['status'] = ''

    # Format the dates.
    try:
        mm, dd, yyyy = details['date_collected'].split('/')
        details['date_collected'] = '-'.join([yyyy, mm, dd]) 
    except KeyError:
        details['date_collected'] = ''
    try:
        mm, dd, yyyy = details['date_received'].split('/')
        details['date_received'] = '-'.join([yyyy, mm, dd])
    except KeyError:
        details['date_received'] = ''
    
    # Rename desired fields.
    for key, value in DETAILS.items():
        try:
            details[value] = details.pop(key)
        except KeyError:
            pass

    # Get the CoA ID.
    try:
        details['coa_id'] = soup.find('p', attrs={'class': 'coa-id'}).text.split(':')[-1]
    except AttributeError:
        details['coa_id'] = ''

    # Remove any keys that begin with a digit.
    for key in list(details.keys()):
        if key[0].isdigit():
            del details[key]

    # Optional: Try to get sample_weight.

    # Get all of the analyses and results.
    analyses = []
    results = []
    notes = None
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
        details[key] = method

        # Get all of the results for the analysis.
        # - value, units, margin_of_error, lod, loq
        table = element.find('table')
        rows = table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            result = {}
            for cell in cells:
                key = cell['class'][0].replace('table-', '')
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
        details['date_tested'] = f'{yyyy}-{mm}-{dd}'
        details['product_type'] = items[-1].text.split(': ')[-1]

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
            details[key] = method
            
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
                    value = cell.text.replace('\n', '').strip()
                    result[key] = value
                    result['analysis'] = analysis
                results.append(result)

    # Remove any sample ID that may be in details as it is not needed.
    try:
        del details['sample_id']
    except KeyError:
        pass

    # Aggregate the sample details.
    if not results:
        results = None
    data = {'notes': notes, 'results': results}
    return {**data, **details}


#-----------------------------------------------------------------------
# ✓ Test the core functionality.
#-----------------------------------------------------------------------

# if __name__ == '__main__':

    # ✓ Get all test results for a specific client.
    # test_results = get_sc_labs_test_results('2821')

    # ✓ Get details for a specific sample.
    # sample_details = get_sc_labs_sample_details('858084')


#-----------------------------------------------------------------------
# ✓ Test full scrape.
#-----------------------------------------------------------------------
# 1. Discover all SC Labs public clients by scanning:
#
#       https://client.sclabs.com/client/{client}/
#
# 2. Iterate over pages for each client, collecting samples until
# the 1st sample and active page are the same:
# 
#       https://client.sclabs.com/client/{client}/?page={page}
#
# 3. (a) Get the sample details for each sample found.
#    (b) Save the sample details.
#-----------------------------------------------------------------------

if __name__ == '__main__':

    # Future work: Figure out a more efficient way to find all producer IDs.
    # PAGES = range(1, 12_000)
    # PRODUCER_IDS = list(PAGES)
    # PRODUCER_IDS.reverse()

    # Alternatively, read in the known producer IDs.
    # from .sc_labs_producer_ids import PRODUCER_IDS

    # # 1. and 2. Iterate over potential client pages and client sample pages.
    # start = datetime.now()
    # clients = []
    # errors = []
    # test_results = []
    # for _id in PRODUCER_IDS:
    #     results = get_sc_labs_test_results(_id)
    #     if results:
    #         test_results += results
    #         print('Found all samples for producer:', _id)
    #         clients.append(_id)
    #     sleep(3)

    # # 2b. Save the results, just in case.
    # data = pd.DataFrame(test_results)
    # timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    # datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
    # data.to_excel(datafile, index=False)
    # end = datetime.now()
    # print('Sample collection took:', end - start)

    # # Read in the saved test results (useful for debugging).
    datafile = f'{DATA_DIR}/sc_labs_test_results_pending.xlsx'
    start = datetime.now()
    data = pd.read_excel(datafile)
    
    import math

    # 3a. Get the sample details for each sample found.
    errors = []
    rows = []
    subset = data.loc[data['results'].isnull()]
    total = len(subset)
    for index, values in subset[9_000:].iterrows():
        if not math.isnan(values['results']):
            continue
        if index < 5465:
            continue
        percent = round((index  + 1) * 100 / total, 2)
        sample = values['lab_results_url'].split('/')[-2]
        details = get_sc_labs_sample_details(sample)
        rows.append({**values.to_dict(), **details})
        if details['results']:
            print('Results found (%.2f%%) (%i/%i):' % (percent, index + 1, total), sample)
        else:
            print('No results found (%.2f%%) (%i/%i):' % (percent, index + 1, total), sample)
        sleep(3)
        
        # Save every 500 rows just in case.
        if index % 500 == 0 and index != 0:
            data = pd.DataFrame(rows)
            timestamp = datetime.now().isoformat()[:19].replace(':', '-')
            datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
            data.to_excel(datafile, index=False)
            print('Saved data:', datafile)

    # 3b. Save the final results.
    data = pd.DataFrame(rows)
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    datafile = f'{RAW_DATA}/sc-lab-results-{timestamp}.xlsx'
    data.to_excel(datafile, index=False)
    end = datetime.now()
    print('Detail collection took:', end - start)


#-----------------------------------------------------------------------
# TODO: Test scrape most recent.
#-----------------------------------------------------------------------
# 1. Discover all SC Labs public clients.
# 2. Get the most recent 100 samples for each client.
# 3. (a) Get the sample details for each sample found.
#    (b) Save the sample details.
#-----------------------------------------------------------------------

# # 1. Discover all SC Labs public clients.
# # Only do this once a week or so (Tue 4:20am EST or so).

# # 2. Get the most recent 100 samples for each client.
# errors = []
# test_results = []
# for client in clients:
#     try:
#         results = get_sc_labs_test_results(client, page_limit=1)
#         test_results += results
#         if test_results:
#             print('Collected samples for client:', client)
#             clients.append(client)
#         sleep(0.2)
#     except:
#         errors.append(client)

# # 3a. Get the details for the most recent samples.
# total = len(test_results)
# for i, test_result in enumerate(test_results):
#     sample = test_result['lab_results_url'].split('/')[-1]
#     print('Collecting (%i/%i):' % (i + 1, total), sample)
#     details = get_sc_labs_sample_details(sample)
#     test_results[i] = {**test_result, **details}

# # TODO: Process the data before saving it the the database.

# # 3b. Save the most recent samples.
# # col = 'public/data/lab_results/{}'
# # refs = [col.format(x['sample_id']) for x in test_results]
# # update_documents(refs, test_results)


#-----------------------------------------------------------------------
# Future work: Processing the raw data.
#-----------------------------------------------------------------------

# TODO: Augment lab data:
# - lab_id
# - lab_name
# - lab_url
# - lab_license_number
# - lab_latitude, lab_longitude

# TODO: Augment the `state`.


# TODO: Find the `county` for the `zip_code`.


# TODO: Normalize the `results`, `images`.


# TODO: Standardize the `product_type` and `status`.


# Separate `lod` and `loq`.


# Rename `mu` to `margin_of_error`.
# Remove: ±


# Separate `batch_units` from `batch_size`.


# Handle values and units.
# result-mass -> mg_g
# result-percent -> value
# units = 'percent'


# Rename `compound` to `name` and add `key`.
# Rename `action-limit` to `limit`
# `result-mass` to `value`
# `result-pf` to `status`


# Handle:
# - total_terpenoids_mgtog, total_terpenoids_percent

# TODO: Standardize `analyses`.

# TODO: Standardize the analyte names!

# TODO: Standardize `strain_name`.


#-----------------------------------------------------------------------
# Future work: Analyzing the data.
#-----------------------------------------------------------------------

# Future work: Calculate average results by state, county, and zip code.


# Research question: Where in California has the most potent flower?
