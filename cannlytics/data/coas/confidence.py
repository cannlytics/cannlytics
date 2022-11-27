"""
CoADoc | Parse Confidence Analytics COAs
Copyright (c) 2022 Cannlytics

Authors:
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/26/2022
Updated: 11/27/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Confidence Analytics COA PDFs.

Data Points (✓):

    - analyses
    - methods
    - {analysis}_status
    ✓ date_received
    ✓ date_tested
    ✓ external_id
    ✓ lab_id
    - lab_results_url
    - metrc_lab_id
    - metrc_source_id
    ✓ producer
    ✓ producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    ✓ producer_license_number
    ✓ product_id
    ✓ product_name
    ✓ product_type
    - results
    - results_hash
    - sample_hash
    - total_cannabinoids
    - total_cbd (Calculated as total_cbd = cbd + 0.877 * cbda)
    - total_thc (Calculated as total_thc = delta_9_thc + 0.877 * thca)
    - total_terpenes

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
CONFIDENCE = {
    'coa_algorithm': 'confidence.py',
    'coa_algorithm_entry_point': 'parse_confidence_coa',
    'lims': 'Confidence Analytics',
    'url': 'https://certs.conflabs.com',
    'lab': 'Confidence Analytics',
    'lab_website': 'https://conflabs.com',
    'lab_license_number': '7939083039',
    'lab_image_url': 'https://www.conflabs.com/wp-content/uploads/2022/06/CA_3_transparent_registered-2.png',
    'lab_address': '14797 NE 95th St, Redmond, WA 98502',
    'lab_street': '14797 NE 95th St',
    'lab_city': 'Redmond',
    'lab_county': 'King',
    'lab_state': 'WA',
    'lab_zipcode': '98052',
    'lab_latitude': 47.685890,
    'lab_longitude': -122.143640,
    'lab_phone': '(206) 743-8843',
    'lab_email': 'info@conflabs.com',
}


def parse_confidence_pdf(
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
    front_page_text = front_page.extract_text()
    front_page_lines = front_page_text.split('\n')
    for i, line in enumerate(front_page_lines):

        # Get the sample number as the lab ID.
        if 'Sample #' in line:
            obs['lab_id'] = line.split('Sample # ')[-1]

        # Get the product name, product ID, and date received.
        if 'Sample Name:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' ')
            obs['date_received'] = parts[-1]
            obs['product_id'] = parts[-2]
            obs['product_name'] = ' '.join(parts[0:-2])
        
        # Get the product type, external ID, and date tested.
        if 'Type:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' ')
            obs['date_tested'] = parts[-1]
            obs['external_id'] = parts[-2]
            obs['product_type'] = ' '.join(parts[0:-2])

        # Get the producer.
        if 'Origination:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(',')[0].split(' ')
            obs['producer_license_number'] = parts[-3]
            obs['producer'] = ' '.join(parts[0:-3])
        
        # Get the producer address.
        if 'Address:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' Date of Harvest:')[0].split(' ')
            obs['producer_street'] = ' '.join(parts[0:-1])

            # TODO: Get the city, zip code, and date harvested from the next line.
            # obs['producer_city'] = 
            # obs['producer_state'] = 
            # obs['producer_zipcode'] = 

        # TODO: Get the analyses and analysis statuses.
        # 'Foreign Matter + Seeds:PASS Microbes:PASS Pesticides:PASS',
        # 'Water Activity:PASS Mycotoxins:PASS Heavy Metals:NE',
        # 'Residual Solvents:NE   '

    # TODO: Geocode the producer's address to get latitude and longitude.



    # # Get the sample IDs.
    # obs['project_id'] = 
    # obs['batch_number'] = 
    # obs['metrc_lab_id'] = 
    # obs['metrc_source_id'] = 

    # # Get the sample data.
    # obs['sample_weight'] = 
    # obs['serving_size'] = 

    # Get the product data, appending long rows to the row before.

    # Get and standardize the analyses.
    analyses = []

    # Get the methods and results.
    methods, results = [], []

        # Format the result.
        # result = {
        #     'analysis': analysis,
        #     'units': units,
        #     'key': key,
        #     'name': name,
        # }
    
    # Close the report.
    report.close()

    # FIXME: Calculate total cannabinoids! Sum of cannabinoids!
    # Calculate total CBD and total THC if needed.
    
    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs = {**CONFIDENCE, **obs}
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


def parse_confidence_url(
        parser,
        url: str,
        headers: Optional[Any] = None,
        temp_path: Optional[str] = '/tmp',
        **kwargs
    ) -> dict:
    """Parse a Confidence Analytics COA URL.
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
    # TODO: Download the PDF.
    temp_pdf = 'coa.pdf'

    # Extract the data with the PDF parsing algorithm and record the URL.
    data = parse_confidence_pdf(
        parser,
        temp_pdf,
        coa_pdf=url,
        **kwargs,
    )
    data['lab_results_url'] = url
    return data


def parse_confidence_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Confidence Analytics COA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        kwargs (arguments): Arguments to pass to the parsing algorithms.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('http'):
            return parse_confidence_url(parser, doc, **kwargs)
        elif doc.endswith('.pdf'):
            data = parse_confidence_pdf(parser, doc, **kwargs)
        else:
            data = parse_confidence_pdf(parser, doc, **kwargs)
    else:
        data = parse_confidence_pdf(parser, doc, **kwargs)
    if isinstance(doc, str):
        data['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    elif isinstance(doc, pdfplumber.pdf.PDF):
        data['coa_pdf'] = doc.stream.name.replace('\\', '/').split('/')[-1]
    return data


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # Specify testing constants.
    coa_url = 'https://certs.conflabs.com/full/WA-kXIRbGqnLVBI-WA-221015-052.pdf'
    doc = '../../../tests/assets/coas/confidence-analytics/13232582566688421-Flower-Dirty-Banana-Breath-WA-221015-052.pdf'
    temp_path = '../../../tests/assets/coas/tmp'

    # [✓] TEST: Identify LIMS.
    # parser = CoADoc()
    # lims = parser.identify_lims(doc, lims={'Confidence Analytics': CONFIDENCE})
    # assert lims == 'Confidence Analytics'

    # [ ] TEST: Parse COA PDF.
    parser = CoADoc()
    data = parse_confidence_pdf(parser, doc)
    print(data)

    # [ ] TEST: Parse COA URL.


    # [ ] TEST: Parse each URL and PDF ambiguously.
    # parser = CoADoc()
    # coas = [short_url, long_url, doc]
    # for coa in coas:
    #     data = parser.parse(coa, temp_path=temp_path)
    #     assert data is not None
    # print('✓ Completed Confidence Analytics COA parsing tests.')
