"""
Parse SC Labs COAs
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/8/2022
Updated: 12/26/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Tools to extract SC Labs test result data from COA PDFs and URLs.
    URL data is extracted from SC Labs client portal: <https://client.sclabs.com/>.

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
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ lab_id
    ✓ product_type
    ✓ batch_number
    ✓ metrc_ids
    - metrc_lab_id
    ✓ metrc_source_id
    ✓ product_size
    ✓ serving_size
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
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    ✓ lab_email
    ✓ lab_website
    ✓ lab_latitude (augmented)
    ✓ lab_longitude (augmented)

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
import json
import re
from time import sleep
from typing import Any
from urllib.parse import urljoin

# External imports.
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import requests

# Internal imports.
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
    parse_data_block,
)
from cannlytics.utils.constants import (
    ANALYSES,
    ANALYTES,
    DEFAULT_HEADERS,
    STANDARD_FIELDS,
    STANDARD_UNITS,
)
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    strip_whitespace,
)


# It is assumed that the lab has the following details.
SC_LABS = {
    'coa_algorithm': 'sclabs.py',
    'coa_algorithm_entry_point': 'parse_sc_labs_coa',
    'lims': 'SC Labs',
    'url': 'https://client.sclabs.com',
    'lab': 'SC Labs',
    'lab_image_url': 'https://www.sclabs.com/wp-content/uploads/2020/11/sc-labs-logo-white.png',
    'lab_email': 'info@sclabs.com',
    'lab_website': 'https://sclabs.com',
}

# It is assumed that the CoA has the following parameters.
SC_LABS_COA = {
    'coa_distributor_area': '(205, 150, 400, 230)',
    'coa_producer_area': '(0, 150, 204.0, 230)',
    'coa_page_area': [
        '(0, 80, 305, 720)',
        '(305, 80, 612, 720)',
    ],
    'coa_sample_details_area': [
        '(0, 225, 200, 350)',
        '(200, 225, 400, 350)',
    ],
}


def parse_sc_labs_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a SC Labs COA URL or PDF.
    Args:
        doc (str or PDF): A URL or a PDF file path or a PDF object.
    Returns:
        (dict): The extracted data.
    """
    try:
        data = parse_sc_labs_url(parser, doc, **kwargs)
    except (AttributeError, ConnectionError):
        data = parse_sc_labs_pdf(parser, doc, **kwargs)
        data['public'] = False
        if isinstance(doc, str):
            data['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
        elif isinstance(doc, pdfplumber.pdf.PDF):
            data['coa_pdf'] = doc.stream.name.replace('\\', '/').split('/')[-1]
    return data


def parse_sc_labs_url(
        parser,
        doc='',
        headers=None,
        **kwargs,
    ) -> dict:
    """Parse a SC Labs COA URL.
    Args:
        doc (str): A lab results URL or lab ID.
        headers (dict): Headers for the HTTP request (optional).
    Returns:
        (dict): A dictionary of sample details.
    """

    # Get the sample page, using either the passed URL or sample ID.
    base_url = SC_LABS['url']
    if doc.startswith(base_url):
        url = doc
    else:
        if headers is None:
            headers = DEFAULT_HEADERS
        url = urljoin(base_url, f'verify/{doc}/')
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the bulk of the details.
    els = soup.find_all('p', attrs={'class': 'sdp-summary-data'})
    obs = parse_data_block(els)

    # Get the product name.
    obs['product_name'] = soup.find('h2').text

    # Get the lab details.
    lab_details = soup.find('div', class_='sdp-sample-desc-legal')
    if lab_details:
        lab_text = lab_details.find_all('p')[-1].text.strip()
        values = lab_text.split(' | ')
        address = values[1].split(', ')
        obs['lab_phone'] = values[2]
        obs['lab_street'] = ', '.join(address[0:-2])
        obs['lab_city'] = address[-2]
        obs['lab_state'] = address[-1].split(' ')[0]
        obs['lab_zipcode'] = address[-1].split(' ')[1]
        obs['lab_address'] = ', '.join(address)
        try:
            obs['lab_license_number'] = values[4]
        except IndexError:
            obs['lab_license_number'] = ''

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
    try:
        el = soup.find('div', attrs={'id': 'cultivator-details'})
        producer_details = parse_data_block(el)
        obs['producer'] = producer_details['business_name']
        obs['producer_license_number'] = producer_details['license_number']
    except:
        producer_details = {'address': obs['address']}
        obs['producer'] = obs.get('business_name')
        obs['producer_license_number'] = obs.get('license_number')
        obs.pop('business_name', None)
        obs.pop('license_number', None)
    
    # Get the producer URL.
    samples_button = soup.find('a', string='See all samples')
    if samples_button:
        href = samples_button['href']
        producer_url = urljoin(base_url, href)
        obs['producer_url'] = producer_url

    # Try to get the producer if not found.
    if not obs['producer'] and samples_button:
        try:
            response = requests.get(producer_url, headers=headers)
            producer_soup = BeautifulSoup(response.content, 'html.parser')
            obs['producer'] = producer_soup.find('h2').text
        except:
            pass

    # If the producer is still not found, then delete that field.
    if not obs['producer']:
        del obs['producer']

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

    # Remove the `address` field to avoid confusion.
    try:
        del obs['address']
    except KeyError:
        pass

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
        el = soup.find('div', attrs={'class': 'sdp-masthead-data'})
        mm, dd, yyyy = el.find('p').text.split('/')
        obs['date_tested'] = '-'.join([yyyy, mm, dd])
    except:
        obs['date_tested'] = ''

    # Get the overall status: Pass / Fail.
    try:
        status = soup.find('p', attrs={'class': 'sdp-result-pass'}).text
        obs['status'] = status.replace('\n', '').strip()
    except AttributeError:
        try:
            status = soup.find('p', attrs={'class': 'sdp-result-fail'}).text
            obs['status'] = status.replace('\n', '').strip()
        except AttributeError:
            obs['status'] = ''

    # Format the dates.
    try:
        mm, dd, yyyy = obs['date_collected'].split('/')
        obs['date_collected'] = '-'.join([yyyy, mm, dd]) 
    except:
        obs['date_collected'] = ''
    try:
        mm, dd, yyyy = obs['date_received'].split('/')
        obs['date_received'] = '-'.join([yyyy, mm, dd])
    except:
        obs['date_received'] = ''
    
    # Rename desired fields.
    # Note: There may be a better way to do this.
    rename = {}
    for key, value in obs.items():
        try:
            standard_field = STANDARD_FIELDS[key]
            rename[standard_field] = value
        except KeyError:
            rename[key] = value
    obs = rename

    # Get the CoA ID.
    try:
        attributes = {'class': 'coa-id'}
        obs['coa_id'] = soup.find('p', attrs=attributes).text \
            .split(':')[-1]
    except AttributeError:
        obs['coa_id'] = ''

    # Remove any keys that begin with a digit.
    for key in list(obs.keys()):
        if not key or key[0].isdigit():
            del obs[key]

    # Optional: Try to get sample_weight.

    # Get all of the analyses and results.
    analyses = []
    results = []
    processing = False
    notes = None
    cards = soup.find_all('div', attrs={'class': 'analysis-container'})    
    for card in cards:

        # Get the analysis.
        analysis = card.find('h4').text
        if 'Notes' in analysis:
            div = card.find('div', attrs={'class': 'section-inner'})
            notes = div.find('p').text
        if 'Analysis' not in analysis:
            continue
        analysis = snake_case(analysis.split(' Analysis')[0])
        analysis = ANALYSES.get(analysis, analysis)
        analyses.append(analysis)

        # Skip analyses that are being processed.
        if 'Processing' in card.text:
            processing = True
            continue

        # Get the method for the analysis.
        bold = card.find('b')
        method = bold.parent.text.replace('Method: ', '')
        key = '_'.join([analysis, 'method'])
        obs[key] = method

        # Get analysis result values: value, units, margin_of_error, lod, loq.
        # Note: Skip cannabinoids edible table and get size fields for edibles.
        if analysis == 'cannabinoids':
            tables = [card.find('table')]
            title = card.find('h5', string='Unit Mass:')
            if title:
                obs['product_size'] = title.find_next('p').text
            title = card.find('h5', string='Serving Size:')
            if title:
                obs['serving_size'] = title.find_next('p').text
        else:
            tables = card.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                result = {}
                for cell in cells:
                    key = cell['class'][0].replace('table-', '')
                    key = STANDARD_FIELDS.get(key, key)
                    value = cell.text.replace('\n', '').strip()
                    result[key] = value
                result['analysis'] = analysis
                results.append(result)

    # Parse legacy results if no results collected at this stage.
    if not results and not processing:

        # Get details.
        try:
            el = soup.find('div', attrs={'id': 'detailQuickView'})
            items = el.find_all('li')
            mm, dd, yyyy = items[0].text.split(': ')[-1].split('-')
            obs['date_tested'] = f'{yyyy}-{mm}-{dd}'
            obs['product_type'] = items[-1].text.split(': ')[-1]
        except:
            pass

        # Get analysis cards.
        try:
            cards = soup.find_all('div', attrs={'class': 'detail-row'})
        except:
            cards = []
        for card in cards:
            
            # Get the analysis.
            try:
                title = card.find('h3').text.lower()
            except:
                continue
            if 'not tested' in title:
                continue
            text = title.split('test')[0]
            analysis = snake_case(strip_whitespace(text))
            if analysis == 'label_claims':
                continue
            analysis = SC_LABS_COA['analyses'].get(analysis, analysis)

            # Get the method for the analysis.
            method = card.find('p').text
            key = '_'.join([analysis, 'method'])
            obs[key] = method

            # Get analysis result values: value, units, margin_of_error, lod, loq.
            table = card.find('table')
            rows = table.find_all('tr')
            if rows:
                for row in rows[1:]:
                    cells = row.find_all('td')
                    result = {}
                    for cell in cells:
                        key = cell['class'][0].replace('table-', '')
                        key = STANDARD_FIELDS.get(key, key)
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
    cleaned_results = []
    for result in results:

        # Assign a `key` for the analyte.
        analyte = snake_case(result['name'])
        result_key = parser.analytes.get(analyte, analyte)

        # Skip the result if the key is 'sum_of_cannabinoids'.
        if result_key == 'sum_of_cannabinoids' or result_key == 'total_thc':
            continue

        # Clean the margin of error.
        try:
            margin = result['margin_of_error'].replace('±', '')
            result['margin_of_error'] = convert_to_numeric(margin)
        except KeyError:
            pass

        # Parse `units` from `value`. E.g. '71.742%'.
        value = result.get('value', '')
        result['value'] = re.sub('[^\d\.]', '', value)
        result['units'] = re.sub('[\d\.]', '', value)
        result['units'] = result['units'].replace('%', 'percent')

        # Try to ensure that the result values are numbers.
        result['value'] = convert_to_numeric(result['value'])
        result['mg_g'] = convert_to_numeric(result.get('mg_g'))
        result['lod'] = convert_to_numeric(result.get('lod'))
        result['loq'] = convert_to_numeric(result.get('loq'))
        result['limit'] = convert_to_numeric(result.get('limit'))
        result['key'] = result_key

        # Update the result.
        cleaned_results.append(result)

    # Update the results.
    results = cleaned_results
    if not results:
        results = []

    # Clean `total_{analyte}`s and `sum_of_cannabinoids`.
    columns = [x for x in obs.keys() if x.startswith('total_') or x.startswith('sum_')]
    for key in columns:
        obs[key] = convert_to_numeric(obs[key], strip=True)

    # Lowercase `{analysis}_status`
    columns = [x for x in obs.keys() if x.endswith('_status')]
    for key in columns:
        obs[key] = obs[key].lower()

    # Try to separate `batch_units` from `batch_size`.
    try:
        obs['batch_size'], obs['batch_units'] = tuple(obs['batch_size'].split(' '))
    except:
        pass

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Return the sample details with a new or re-minted `sample_id`.
    obs = { **SC_LABS, **obs}
    obs['analyses'] = analyses
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    # FIXME: The `lab_results_url` is nan.
    obs['lab_results_url'] = url
    obs['notes'] = notes
    obs['results'] = results
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


def parse_sc_labs_pdf(parser, doc: Any, **kwargs) -> dict:
    """Parse a SC Labs CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Read the PDF.
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
    else:
        report = doc

    # Get the lab-specific CoA page areas, standard analyses and analytes.
    obs = {}
    coa_parameters = SC_LABS_COA
    distributor_area = literal_eval(coa_parameters['coa_distributor_area'])
    producer_area = literal_eval(coa_parameters['coa_producer_area'])
    sample_details_area = coa_parameters['coa_sample_details_area']

    # Get producer details.
    front_page = report.pages[0]
    crop = front_page.within_bbox(producer_area)
    details = crop.extract_text().replace('\n', '')
    address = details.split('Address:')[-1].strip()
    business = details.split('Business Name:')[-1].split('License Number:')[0].strip()
    license_number = details.split('License Number:')[-1].split('Address:')[0].strip()
    parts = address.split(',')
    street = parts[0]
    subparts = parts[-1].strip().split(' ')
    city = ' '.join(subparts[:-2])
    try:
        state, zipcode = subparts[-2], subparts[-1]
    except IndexError:
        state, zipcode = '', ''
    obs['producer'] = business
    obs['producer_address'] = address
    obs['producer_street'] = street
    obs['producer_city'] = city
    obs['producer_state'] = state
    obs['producer_zipcode'] = zipcode
    obs['producer_license_number'] = license_number

    # Get distributor details.
    crop = front_page.within_bbox(distributor_area)
    details = crop.extract_text().replace('\n', ' ')
    address = details.split('Address:')[-1].strip()
    business = details.split('Business Name:')[-1].split('License Number:')[0].strip()
    license_number = details.split('License Number:')[-1].split('Address:')[0].strip()
    parts = address.split(',')
    street = parts[0]
    subparts = parts[-1].strip().split(' ')
    city = ' '.join(subparts[:-2])
    try:
        state, zipcode = subparts[-2], subparts[-1]
    except IndexError:
        state, zipcode = '', ''
    obs['distributor'] = business
    obs['distributor_address'] = address
    obs['distributor_street'] = street
    obs['distributor_city'] = city
    obs['distributor_state'] = state
    obs['distributor_zipcode'] = zipcode
    obs['distributor_license_number'] = license_number

    # Get sample details.
    # FIXME: May be mishandling `sum_of_cannabinoids` and `total_cannabinoids`.
    if isinstance(sample_details_area, str):
        sample_details_area = [sample_details_area]
    for area in sample_details_area:
        crop = front_page.within_bbox(literal_eval(area))
        details = crop.extract_text().split('\n')
        for d in details:
            if ':' not in d:
                continue
            values = d.split(':')
            key = snake_case(values[0])
            key = STANDARD_FIELDS.get(key, key)
            obs[key] = values[-1]

    # Get the date tested, product name, and sample type.
    front_page_text = front_page.extract_text()
    date_tested = front_page_text.split('DATE ISSUED')[-1].split('|')[0].strip()
    lines = front_page_text.split('SAMPLE NAME:')[1].split('\n')
    product_name = lines[0].strip()
    obs['product_type'] = lines[1]

    # Get the analyses.
    analyses = []
    for i, line in enumerate(lines):
        if 'ANALYSIS' in line:
            analysis = line.split(' ANALYSIS')[0].lower()
            analysis = ANALYSES.get(analysis, analysis)
            if analysis == 'safety':
                parts = ' '.join(lines[i+1:i+3]).split(':')
                parts = [x.replace('PASS', '').replace('FAIL', '').strip() for x in parts]
                parts = [ANALYSES.get(x, snake_case(x)) for x in parts if x]
                analyses.extend(parts)
            else:
                analyses.append(analysis)

    # Get the cannabinoid and terpene totals.

    value = front_page_text.split('Sum of Cannabinoids:')[-1].split('%')[0]
    obs['sum_of_cannabinoids'] = convert_to_numeric(value, strip=True)

    value = front_page_text.split('Total Cannabinoids:')[-1].split('%')[0]
    obs['total_cannabinoids'] = convert_to_numeric(value, strip=True)

    value = front_page_text.split('Total THC:')[-1].split('%')[0]
    obs['total_thc'] = convert_to_numeric(value, strip=True)

    value = front_page_text.split('Total CBD:')[-1].split('%')[0]
    obs['total_cbd'] = convert_to_numeric(value, strip=True)

    value = front_page_text.split('Total Terpenoids:')[-1].split('%')[0]
    obs['total_terpenes'] = convert_to_numeric(value, strip=True)

    # Get the moisture content analysis if present.
    try:
        value = front_page_text.split('Moisture:')[-1].split('%')[0]
        obs['moisture_content'] = convert_to_numeric(value, strip=True)
        analyses.append('moisture')
    except:
        pass

    # Get all page text, from the 2nd page on, column by column.
    areas = coa_parameters['coa_page_area']
    lines = []
    for page in report.pages[1:]:
        for area in areas:
            crop = page.within_bbox(literal_eval(area))
            lines += crop.extract_text().split('\n')

    # Map all the analytes to analyses.
    # TODO: Is it possible to either make these field dynamic or
    # add these fields to the constants?
    analyte_analysis_map = {
        'Total Sample Area Covered by Sand, Soil, Cinders, or Dirt': 'foreign_matter',
        'Caryophyllene Oxide': 'terpenes',
        'Pentachloronitro- benzene*': 'pesticides',
        'Piperonylbu- toxide': 'pesticides',
        'DDVP (Dichlorvos)': 'pesticides',
        'Methyl parathion': 'pesticides',
        'Chlorantranilip- role': 'pesticides',
        'Clofentezine': 'pesticides',
        'Total Sample Area Covered by Sand, Soil, Cinders, or Dirt': 'foreign_matter',
        'Total Sample Area Covered by Mold': 'foreign_matter',
        'Total Sample Area Covered by an Imbedded Foreign Material': 'foreign_matter',
        'Insect Fragment Count': 'foreign_matter',
        'Hair Count': 'foreign_matter',
        'Mammalian Excreta Count': 'foreign_matter',
        'Shiga toxin-producing Escherichia coli': 'microbes',
        'Salmonella spp.': 'microbes',
        'Aspergillus fumigatus': 'microbes',
        'Aspergillus flavus': 'microbes',
        'Aspergillus niger': 'microbes',
        'Aspergillus terreus': 'microbes',
    }
    for line in lines:
        if 'TEST RESULT' in line:
            analysis_name = line.split('TEST RESULT')[0].strip().title()
            analysis = ANALYSES.get(analysis_name)
        elif 'Method:' in line:
            # FIXME: Imperfect method collect (missing text on next line).
            obs[f'{analysis}_method'] = line.split('Method:')[-1].strip()
        else:
            first_value = find_first_value(line)
            name = line[:first_value].replace('\n', ' ').strip()
            analyte_analysis_map[name] = analysis

    # Get the results.
    results = []
    for page in report.pages[1:]:

        # Get the results from each result page.
        tables = page.extract_tables()
        for table in tables:
            for i, row in enumerate(table):

                # Determine the analysis, then the units.
                analyte = row[0].replace('\n', ' ').strip()
                analysis = analyte_analysis_map.get(analyte)
                key = snake_case(analyte)
                key = ANALYTES.get(key, key)
                units = STANDARD_UNITS.get(analysis)

                # Skip per unit values.
                if 'per_unit' in key:
                    continue

                # Hot-fix: Skip (non-)analytes that begin with a digit.
                # Note: It would be best to improve this logic.
                if key[0].isdigit():
                    continue

                # Determine the values, handling screens differently.
                parts = row[1].split(' / ')
                subparts = parts[-1].strip().split(' ')
                limit = None
                status = None
                if len(subparts) == 3:
                    limit = subparts[1]
                    value, status = tuple(row[-1].split(' '))
                else:
                    try:
                        mg_g, value = tuple(row[-1].split(' '))
                    except ValueError:
                        value = row[-1]

                # Record the result
                results.append({
                    'analysis': analysis,
                    'key': key,
                    'limit': limit,
                    'lod': convert_to_numeric(parts[0].strip()),
                    'loq': convert_to_numeric(subparts[0]),
                    'margin_of_error': convert_to_numeric(subparts[-1].replace('±', '')),
                    'mg_g': convert_to_numeric(mg_g),
                    'name': analyte,
                    'status': status,
                    'units': units,
                    'value': convert_to_numeric(value),
                })

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # FIXME: `total` is being included as a terpene.

    # FIXME: Results are not properly JSON-encoded and raise this error:
    # json.loads(obs['results'])
    # JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)

    # Finish data collection with a freshly minted sample ID.
    obs = {**SC_LABS, **obs}
    obs['analyses'] = json.dumps(analyses)
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['date_tested'] = date_tested
    obs['product_name'] = product_name
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


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

        # Note: This may not be working as intended.
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
            el = details.find('span', attrs=attributes)
            producer_url = el.find('a')['href']
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
                'sample_id': None,
                'total_cbd': total_cbd,
                'total_thc': total_thc,
                'total_terpenes': total_terpenes,
            }
            samples.append(sample)

    # Return all of the samples for the client.
    return samples


# === Tests ===
# Tested: 2023-12-31 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':
    pass

    # # Initialize tests.
    # from cannlytics.data.coas import CoADoc
    # parser = CoADoc()

    # # [✓] TEST: Get all test results for a specific client.
    # test_results = get_sc_labs_test_results(sample='2821')
    # assert test_results is not None

    # [✓] TEST: Get details for a specific lab ID.
    # sample_details = parse_sc_labs_url(parser, '220525L001')
    # assert sample_details is not None

    # # [✓] TEST: Get details for a specific sample URL.
    # doc = 'https://client.sclabs.com/verify/210727L001/'
    # parser = CoADoc()
    # lab = parser.identify_lims(doc)
    # assert lab == 'SC Labs'
    # data = parse_sc_labs_coa(parser, doc)
    # assert data is not None
    # print('Parsed:', doc)

    # # [✓] TEST: Test: Parse a failing COA.
    # doc = 'https://client.sclabs.com/verify/231221R001/'
    # parser = CoADoc()
    # data = parse_sc_labs_coa(parser, doc)
    # assert data is not None
    # print('Parsed:', doc)

    # # [✓] TEST: Parse a SC Labs CoA PDF (with cannabinoids and terpenes).
    # directory = '../../../tests/assets/coas/sc-labs'
    # doc = f'{directory}/Mattole Valley Jack H.pdf'
    # parser = CoADoc()
    # lab = parser.identify_lims(doc)
    # assert lab == 'SC Labs'
    # data = parse_sc_labs_pdf(parser, doc)
    # assert data is not None
    # print('Parsed:', doc)

    # # [✓] TEST: Parse a SC Labs CoA PDF (with safety screening).
    # directory = '../../../tests/assets/coas/sc-labs'
    # doc = f'{directory}/Cherry Punch.pdf'
    # parser = CoADoc()
    # lab = parser.identify_lims(doc)
    # assert lab == 'SC Labs'
    # data = parse_sc_labs_pdf(parser, doc)
    # assert data is not None
    # print('Parsed:', doc)
