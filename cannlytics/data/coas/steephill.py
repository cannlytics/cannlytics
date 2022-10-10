"""
CoADoc | Parse Steep Hill COAs
Copyright (c) 2022 Cannlytics

Authors:
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/23/2022
Updated: 10/10/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Steep Hill COA PDFs. Validated in:

        ✓ Massachusetts

Data Points:

    ✓ analyses
    ✓ methods
    - {analysis}_status TODO: Record the pass / fail status for each analysis.
    ✓ date_received
    ✓ date_tested
    ✓ lab_results_url
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ producer
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ results_hash
    ✓ sample_hash
    ✓ total_cannabinoids
    ✓ total_cbd (Calculated as total_cbd = cbd + 0.877 * cbda)
    ✓ total_thc (Calculated as total_thc = delta_9_thc + 0.877 * thca)
    ✓ total_terpenes

"""
# Standard imports.
from datetime import datetime
import json
import os
import re
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber
import requests

# Internal imports.
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.data.web import download_google_drive_file
from cannlytics.utils import convert_to_numeric, snake_case
from cannlytics.utils.constants import DECARB
    

# It is assumed that the lab has the following details.
STEEPHILL = {
    'coa_algorithm': 'steephill.py',
    'coa_algorithm_entry_point': 'parse_steephill_coa',
    'url': 'https://www.steephill.com',
    'lims': 'Steep Hill',
    'lab': 'Steep Hill',
    'lab_license_number': 'IL281277',
    'lab_image_url': '',
    'lab_address': '40 Speen Street Suite 301, Framingham, MA, 01701',
    'lab_street': '40 Speen Street Suite 301',
    'lab_city': 'Framingham',
    'lab_county': 'Middlesex',
    'lab_state': 'MA',
    'lab_zipcode': '01701',
    'lab_latitude': 42.312180,
    'lab_longitude': -71.389410,
    'lab_phone': '508-465-3470',
    'lab_email': 'support@steephill.com',
    'lab_website': 'www.steephill.com',
}

# It is assumed that there are the following analyses on each CoA.
STEEPHILL_ANALYSES = {
    'Cannabinoid': {
        'key': 'cannabinoids',
        'columns': ['loq', 'value', 'mg_g', 'mg_serving'],
        'units': 'percent',
    },
    'Heavy Metals': {
        'key': 'heavy_metals',
        'columns': ['loq', 'value', 'limit', 'status'],
        'units': 'ppb',
        # FIXME: Also has limit and status for edibles.
    },
    'Microbial Contaminants': {
        'key': 'microbes',
        'columns': ['value', 'notes', 'tested_at', 'limit', 'status'],
        'units': 'CFU/g',
    },
    'Pathogenic Bacteria': {
        'key': 'microbes',
        'columns': ['value', 'date_tested', 'limit', 'status'],
        'units': 'CFU/g',
    },
    'Mycotoxins': {
        'key': 'mycotoxins',
        'columns': ['loq', 'value', 'limit', 'status'],
        'units': 'ppb',
    },
    'Residual Solvent': {
        'key': 'residual_solvents',
        'columns': ['loq', 'value', 'limit', 'status'],
        'units': 'ppm',
    },
    'Pesticides': {
        'key': 'pesticides',
        'columns': ['loq', 'value', 'limit', 'status'],
        'units': 'ppb',
    },
    'Vitamin E Acetate': {
        'key': 'vitamin_e_acetate',
        'columns': ['loq', 'value', 'limit', 'status'],
        'units': 'ppb',
    },
    'Terpenes': {
        'key': 'terpenes',
        'columns': ['loq', 'value', 'mg_g'],
        'units': 'percent',
    },
}

# It is assumed that the CoA has the following parameters.
STEEPHILL_COA = {
    'fields': {
        'Production Stage': 'product_subtype',
        'Product Class': 'product_type',
        'Ingestion Only': 'cannabinoids_status',
        'Extraction Solvent': 'residual_solvent_status',
        'Retail Name': 'product_name',
    },
}


def parse_steephill_pdf(
        parser,
        doc: Any,
        coa_pdf: Optional[str] = '',
        **kwargs,
    ) -> dict:
    """Parse a Steep Hill CoA PDF.
    Args:
        parser (CoADoc): A CoADoc parsing client.
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        coa_pdf (str): A filename to use for the `coa_pdf` field (optional).
    Returns:
        (dict): The sample data.
    """
    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = coa_pdf or doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = coa_pdf or report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the lab data.
    front_page = report.pages[0]
    tables = front_page.extract_tables()
    lab_details = tables[0]
    lab_details = [[item for item in x if item] for x in lab_details]
    for row in lab_details:
        for cell in row:
            if 'Submitted:' in cell:
                obs['date_tested'] = cell.split('Submitted:')[-1].strip()
                break

    # Get the client data.
    client_details = tables[1][-1][0].split('\n')
    address_parts = client_details[2].split(',')
    obs['producer'] = client_details[0]
    obs['producer_street'] = client_details[1]
    obs['producer_city'] = address_parts[0]
    obs['producer_state'] = address_parts[-1].strip().split(' ')[0]
    obs['producer_zipcode'] = address_parts[-1].strip().split(' ')[-1]
    obs['producer_license_number'] = client_details[3].split(':')[-1].strip()
    obs['project_id'] = client_details[4].split(':')[-1].strip()
    obs['date_received'] = client_details[5].split(':')[-1].strip()

    # Get the sample IDs.
    sample_ids = tables[2][-1][0].split('\n')
    obs['batch_number'] = sample_ids[0].split(':')[-1].strip()
    obs['metrc_lab_id'] = sample_ids[1].split(':')[-1].strip()
    obs['metrc_source_id'] = sample_ids[2].split(':')[-1].strip()

    # Get the sample data.
    sample_data = tables[3][-1][0].split('\n')
    obs['sample_weight'] = sample_data[0].split(':')[-1].strip()
    obs['serving_size'] = sample_data[1].split(':')[-1].strip()

    # Get the product data, appending long rows to the row before.
    standard_fields = STEEPHILL_COA['fields']
    product_data = tables[4][1:]
    for row in product_data:
        cells = row[0].split('\n')
        for cell in cells:
            parts = cell.split(':')
            try:
                key = standard_fields[parts[0]]
            except KeyError:
                obs[key] = obs[key] + cell
                continue
            value = parts[-1].replace('---', '').strip()
            obs[key] = value

    # Get and standardize the analyses.
    analyses = []
    for table in tables:
        row = table[0]
        if len(row) == 2:
            if row[1] in ['Y', 'P', 'F']:
                analysis = row[0].replace('\n', '')
                analysis = parser.analyses.get(analysis, analysis)
                analyses.append(analysis)

    # Get the methods and results.
    methods, results = [], []
    for page in report.pages[1:]:

        # Stop at the QC section.
        page_text = page.extract_text()
        if 'QA/QC Section' in page_text:
            break

        # Find all of the tables, then extract the lines of each table.
        tables = page.find_tables()
        for table in tables:
            crop = page.within_bbox(table.bbox)
            text = crop.extract_text()
            lines = text.split('\n')
            for line in lines[:-1]: # Skip the footnote.

                # Get the analysis, e.g. "[H] Cannabinoid Profile Metrc...".
                if re.match(r'\[[A-Z]+\] ', line[:4]):
                    analysis_name = line[4:].split('Metrc')[0].strip()
                    analysis_name = analysis_name.replace(' Results', '') \
                        .replace(' Analysis', '') \
                        .replace(' Profile', '')
                    analysis_data = STEEPHILL_ANALYSES[analysis_name]
                    analysis = analysis_data['key']
                    units = analysis_data['units']
                    columns = analysis_data['columns']
                    continue

                # Skip column rows and detail rows.
                elif ';' in line:
                    continue
                elif line.startswith('Cannabinoid'):
                    continue
                elif line.startswith('Terpene'):
                    continue
                elif line.startswith('Analyte'):
                    continue
                elif line.startswith('LOQ'):
                    continue
                elif line.startswith('Datafile'):
                    continue
                elif line.startswith('Analyst'):
                    continue
                elif line.startswith('Result'):
                    continue

                # Collect the methods.
                elif 'were analyzed' in line or 'were measured' in line or \
                    'were incubated' in line or 'was determined' in line:
                    methods.append(line)
                    continue

                # Handle totals appropriately.
                elif line.startswith('Total Terpenes'):
                    value = line.split(' - ')[1]
                    obs['total_terpenes'] = convert_to_numeric(value)
                    continue
                elif line.startswith('Total Available Cannabinoids'):
                    value = value = line.split(' - ')[1]
                    obs['total_cannabinoids'] = convert_to_numeric(value)
                    continue
                elif line.startswith('Total Mycotoxins'):
                    continue

                # Record each result, skipping not-tested analytes.
                elif '(' in line:
                    name = line.split('(')[1].split(')')[0].strip()
                    values = line.split(')')[-1].strip().split(' ')
                    if len(values) < len(columns):
                        continue
                    key = snake_case(name)
                    key = parser.analytes.get(name, parser.analytes.get(key, key))
                    result = {
                        'analysis': analysis,
                        'units': units,
                        'key': key,
                        'name': name,
                    }
                    for i, column in enumerate(columns):
                        result[column] = convert_to_numeric(values[i])
                    results.append(result)
                    continue

                # Handle standard result lines.
                line = line.replace('Not Detected', 'ND')
                first_value = find_first_value(line, [' \d+', 'ND', 'NT'])
                name = line[:first_value].replace('\n', ' ').strip()
                key = snake_case(name)
                key = parser.analytes.get(name, parser.analytes.get(key, key))
                values = line[first_value:].strip().split(' ')
                if len(values) < len(columns):
                    continue
                result = {
                    'analysis': analysis,
                    'units': units,
                    'key': key,
                    'name': name,
                }
                for i, column in enumerate(columns):
                    result[column] = convert_to_numeric(values[i])
                results.append(result)

                # FIXME: microbes status is not correct.

    # Close the report.
    report.close()

    # Calculate total CBD and total THC if present.
    specials = {}
    total_keys = ['cbd', 'cbda', 'delta_9_thc', 'thca']
    for result in results:
        if result['key'] in total_keys:
            specials[result['key']] = result['value']
    if specials.get('cbd') and specials.get('cbda'):
        try:
            acidic = DECARB * specials['cbda']
        except:
            acidic = 0
        try:
            obs['total_cbd'] = specials['cbd'] + acidic
        except:
            obs['total_cbd'] = 'ND'
    if specials.get('delta_9_thc') and specials.get('thca'):
        try:
            acidic = DECARB * specials['thca']
        except:
            acidic = 0
        try:
            obs['total_thc'] = specials['delta_9_thc'] + acidic
        except:
            obs['total_thc'] = 'ND'
        
    # FIXME: Calculate total cannabinoids! Sum of cannabinoids!

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs = {**STEEPHILL, **obs}
    obs['analyses'] = json.dumps(analyses)
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['methods'] = json.dumps(methods)
    obs['results'] = results
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


def parse_steephill_url(
        parser,
        url: str,
        headers: Optional[Any] = None,
        temp_path: Optional[str] = '/tmp',
        **kwargs
    ) -> dict:
    """Parse a Steep Hill COA URL.
    Args:
        url (str): The COA URL.
        headers (Any): Optional headers for standardization.
        max_delay (float): The maximum number of seconds to wait
            for the page to load.
        persist (bool): Whether to persist the driver.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """
    # Ensure that the URL is direct to Google Drive.
    pdf_url = str(url)
    if not pdf_url.startswith('https://drive.google'):
        response = requests.get(pdf_url, headers=headers)
        pdf_url = response.url
    if not pdf_url.startswith('https://drive.google'):
        raise ValueError('COA URL not recognized as a Steep Hill URL.')

    # Download the PDF from Google Drive.
    temp_pdf = os.path.join(temp_path, 'coa.pdf')
    if not os.path.exists(temp_path): os.makedirs(temp_path)
    drive_id = pdf_url.split('/d/')[-1].split('/')[0]
    download_google_drive_file(drive_id, temp_pdf)

    # Extract the data with the PDF parsing algorithm and record the URL.
    data = parse_steephill_pdf(
        parser,
        temp_pdf,
        coa_pdf=url,
        **kwargs,
    )
    data['lab_results_url'] = pdf_url
    return data


def parse_steephill_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Steep Hill COA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        kwargs (arguments): Arguments to pass to the parsing algorithms.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('http'):
            return parse_steephill_url(parser, doc, **kwargs)
        elif doc.endswith('.pdf'):
            data = parse_steephill_pdf(parser, doc, **kwargs)
        else:
            data = parse_steephill_pdf(parser, doc, **kwargs)
    else:
        data = parse_steephill_pdf(parser, doc, **kwargs)
    if isinstance(doc, str):
        data['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    elif isinstance(doc, pdfplumber.pdf.PDF):
        data['coa_pdf'] = doc.stream.name.replace('\\', '/').split('/')[-1]
    return data


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # Specify testing constants.
    temp_path = '../../../tests/assets/coas/tmp'
    short_url = 'https://tinyurl.com/mr4cnhm3'
    long_url = 'https://drive.google.com/file/d/10S_odKnB5B76Zhgjd0ALb3ffkSp649sL/view'
    doc = '../../../tests/assets/coas/steep-hill/Dosi-Woah.pdf'
    coas = [short_url, long_url, doc] 

    # # [✓] TEST: Identify Steep Hill COAs.
    # parser = CoADoc()
    # for coa in coas:
    #     lab = parser.identify_lims(coa)
    #     assert lab == 'Steep Hill'

    # # [✓] Parse a Steep Hill COA from a short URL.
    # parser = CoADoc()
    # data = parse_steephill_url(parser, short_url, temp_path=temp_path)
    # assert data is not None
    # print('Parsed:', short_url) 

    # # [✓] Parse a Steep Hill COA from a long URL.
    # parser = CoADoc()
    # data = parse_steephill_url(parser, long_url, temp_path=temp_path)
    # assert data is not None
    # print('Parsed:', long_url) 

    # # [✓] TEST: Parse a Steep Hill COA from a PDF.
    parser = CoADoc()
    doc = '../../../tests/assets/coas/steep-hill/SEL.SL.220601.pdf'
    data = parse_steephill_pdf(parser, doc)
    assert data is not None
    print('Parsed:', doc)

    # # [✓] TEST: Parse each URL and PDF ambiguously.
    # parser = CoADoc()
    # coas = [short_url, long_url, doc]
    # for coa in coas:
    #     data = parser.parse(coa, temp_path=temp_path)
    #     assert data is not None
    # print('✓ Completed Steep Hill COA parsing tests.')
