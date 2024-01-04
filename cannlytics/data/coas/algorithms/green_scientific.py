"""
Parse Green Scientific Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/12/2023
Updated: 11/20/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Green Scientific Labs COA PDFs.

Data Points:

    - analyses
    - methods
    - coa_url
    - date_collected
    - date_tested
    - date_received
    ✓ image_url
    - lab_results_url
    - producer
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    - product_name
    - lab_id
    - product_type
    - batch_number
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight
    - results
    - status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    - sample_id
    - strain_name (augmented)
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number (augmented)
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_county (augmented)
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
import os
import re
from typing import Any, Optional

# External imports.
import cv2
import pandas as pd
import pdfplumber
try:
    import pytesseract
except ImportError:
    print('Unable to import `Tesseract` library. This tool is used for OCR.')

# Internal imports.
from cannlytics import firebase
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.constants import ANALYTES, STANDARD_UNITS
from cannlytics.utils.utils import (
    convert_to_numeric,
    download_file_from_url,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
GREEN_SCIENTIFIC_LABS = {
    'coa_algorithm': 'green_scientific.py',
    'coa_algorithm_entry_point': 'parse_green_scientific_coa',
    # 'url': 'https://www.verifycbd.com',
    'url': 'https://www.greenscienti', # The f parses incorrectly
    'lims': 'Green Scientific Labs',
    'lab': 'Green Scientific Labs',
    'lab_license_number': 'CMTL-0004',
    'lab_image_url': 'https://www.greenscientificlabs.com/assets/images/logo-blue.png',
    'lab_address': '4001 SW 47th Avenue, Suite 208, Davie, FL 33314',
    'lab_street': '4001 SW 47th Avenue, Suite 208',
    'lab_city': 'Davie',
    'lab_county': 'Broward',
    'lab_state': 'FL',
    'lab_zipcode': '33314',
    'lab_phone': '(954) 514-9343',
    'lab_email': 'info@greenscientificlabs.com',
    'lab_website': 'https://www.greenscientificlabs.com/',
    'lab_latitude': 26.071350,
    'lab_longitude': -80.210750,
}
GREEN_SCIENTIFIC_LABS_COLUMNS = {
    'Harvest/Lot ID': 'external_id',
    'Seed-to-Sale #': 'traceability_id',
    'Create Date': 'date_produced',
    'Total Qty.': 'batch_size',
    'Order #': 'project_id',
    'Exp. Date': 'date_expired',
    'Matrix': 'product_type',
    'Order Name': 'product_name',
    'Size': 'product_size',
    'Pickup Weight': 'sample_weight',
    'Retail Batch #': 'batch_number',
    'Received': 'date_received',
    'Cultivation Facility': 'producer',
    'Cultivars(s)': 'strain_name',
    'Complete': 'date_tested',
    'Processing Facility': 'distributor',
}


class GreenScientificLabs:
    """Green Scientific Labs COA parser."""

    def __init__(self, parser: Any):
        self.parser = parser
        self.metadata = GREEN_SCIENTIFIC_LABS

    def parse_coa(
            self,
            doc: str,
            temp_path=None,
            image_dir=None,
            save_to_firebase=False,
            verbose=False,
            columns=None,
        ) -> dict:
        """
        Parse a Green Scientific Labs COA.
        """
        # FIXME:
        obs = {}
        # temp_path, image_dir = initialize_paths(temp_path, image_dir)
        # report = read_pdf(doc, temp_path)
        # front_page_text, parsed_with_ocr = apply_ocr_if_needed(doc, report, verbose, temp_path)
        # front_page_text = clean_front_page_text(front_page_text)
        # lines = extract_front_page_data(report.pages[0])
        # save_to_firebase_if_needed(save_to_firebase, doc, image_dir, report.pages[0], obs)
        # analyses = find_analyses(front_page_text)
        # address = extract_producer_address(report.pages[0])
        # product_details = extract_product_details(lines, columns)
        # total_compounds = extract_total_compounds(front_page_text, lines)
        # obs = {**address, **product_details, **total_compounds}
        # obs['parsed_with_ocr'] = parsed_with_ocr
        return obs



def parse_green_scientific_coa(doc: str, **kwargs) -> dict:
    """
    Identify the lab.
    """
    gsl = GreenScientificLabs(parser=CoADoc())
    return gsl.parse_coa(doc, **kwargs)


# === Tests ===
if __name__ == '__main__':

    # === DEV ===
    from cannlytics.data.coas import CoADoc

    # Parameters.
    doc = '70897.pdf'
    doc = r"D:/data/florida/lab_results/.datasets/pdfs/MMTC-2017-0008/72619.pdf"
    image_dir = './'
    image_starting_index = 2
    image_ending_index = -1


    # Define the observation.
    obs = {}

    # Parse a full-panel COA.
    report = pdfplumber.open(doc)
    front_page = report.pages[0]
    front_page_text = front_page.extract_text()

    # [ ] TEST: Identify the lab.
    parser = CoADoc(lims={'Green Scientific Labs': GREEN_SCIENTIFIC_LABS})
    print(parser.identify_lims(doc))

    # TODO: Either use or find the COA URL.
    # - coa_url
    coa_url = parser.find_pdf_qr_code_url(doc)
    # - lab_results_url

    # Optional: Initialize Firebase.
    try:
        from cannlytics import firebase
        from firebase_admin import storage, get_app
        firebase.initialize_firebase()
        app = get_app()
        bucket_name = f'{app.project_id}.appspot.com'
    except:
        pass

    # Save the product image.
    try:
        image_index, _ = max(
            enumerate(front_page.images[image_starting_index:image_ending_index]),
            key=lambda img: img[1]['width'] * img[1]['height']
        )
        image_data = parser.get_pdf_image_data(front_page, image_index=image_index + image_starting_index)
        image_filename = doc.split('/')[-1].replace('.pdf', '.png')
        image_file = os.path.join(image_dir, image_filename)
        parser.save_image_data(image_data, image_file)
        image_ref = f'data/lab_results/images/green-scientific-labs/{image_filename}'
        firebase.upload_file(image_ref, image_file, bucket_name=bucket_name)
        image_url = firebase.get_file_url(image_ref, bucket_name=bucket_name)
        obs['image_url'] = image_url
    except:
        obs['image_url'] = None
    
    # Get the front page text.
    front_page = report.pages[0]
    number_of_pages = len(report.pages)
    front_page_text = report.pages[0].extract_text()

    # Process the text.
    front_page_text = front_page_text.replace('█', '\n')
    lines = front_page_text.split('\n')
    lines = [x for x in lines if x != '']

    # DEV
    create_date_match = re.search(r'Create Date: (\d{2}/\d{2}/\d{4})', front_page_text)
    obs['date_collected'] = create_date_match.group(1) if create_date_match else None

    order_name_match = re.search(r'Order Name: (.+?)\n', front_page_text)
    obs['product_name'] = order_name_match.group(1).strip() if order_name_match else None

    size_match = re.search(r'Size: ([\d,]+)', front_page_text)
    obs['product_size'] = size_match.group(1).replace(',', '') if size_match else None

    received_date_match = re.search(r'Received: (\d{2}/\d{2}/\d{4})', front_page_text)
    obs['date_received'] = received_date_match.group(1) if received_date_match else None

    matrix_match = re.search(r'Matrix: (.+?)\n', front_page_text)
    obs['product_type'] = matrix_match.group(1).strip() if matrix_match else None


    # Updated regular expressions
    batch_regex_updated = r'Retail Batch #:\s*([\d\s]+)'  # Assuming batch number is numeric
    product_name_regex_updated = r'Order Name:\s*([^\n]+)'  # Capture until the newline

    # Re-extract batch number and product name with updated regular expressions
    batch_number_updated = re.search(batch_regex_updated, front_page_text)
    product_name_updated = re.search(product_name_regex_updated, front_page_text)

    # Update the extracted data with refined results
    obs['batch_number'] = batch_number_updated.group(1) if batch_number_updated else None
    obs['product_name'] = product_name_updated.group(1) if product_name_updated else None

    # Regular expressions to find specific information in the text
    date_regex = r'(\d{2}/\d{2}/\d{4})'
    order_regex = r'Order #:\s*(\d+)'
    batch_regex = r'Retail Batch #:\s*([\w\s]+)'
    product_name_regex = r'Order Name:\s*([\w\s]+)'
    producer_regex = r'Facility:\s*([\w\s]+)'

    # Extracting dates
    dates = re.findall(date_regex, front_page_text)
    date_labels = ['date_produced', 'date_expired', 'date_received', 'date_tested']
    date_categorized = dict(zip(date_labels, dates))

    # Extracting order number, batch number, and product name
    order_number = re.search(order_regex, front_page_text)
    batch_number = re.search(batch_regex, front_page_text)
    product_name = re.search(product_name_regex, front_page_text)

    # Extracting producer information
    producer = re.search(producer_regex, front_page_text)

    # Organizing extracted data
    extracted_data = {
        'order_number': order_number.group(1) if order_number else None,
        'batch_number': batch_number.group(1) if batch_number else None,
        'product_name': product_name.group(1) if product_name else None,
        'producer': producer.group(1) if producer else None,
    }


    # TODO: Find the analyses.
    analyses = []


    # TODO: Find the methods.
    methods = []


    # TODO: Find the dates.
    # - date_collected
    # - date_tested
    # - date_received


    # TODO: Find the producer
    # - producer
    # - producer_address
    # - producer_street
    # - producer_city
    # - producer_state
    # - producer_zipcode
    # - producer_license_number


    # TODO: Find the product details.
    # - product_name
    # - lab_id
    # - product_type
    # - batch_number
    # - product_size
    # - serving_size
    # - servings_per_package
    # - sample_weight


    # TODO: Find the product status.
    # - status


    # TODO: Extract the totals.
    # - total_cannabinoids
    # - total_thc
    # - total_cbd
    # - total_terpenes
    # - sample_id
    cannabinoid_pattern = r'Total THC\s+TESTED\s+([%\d.]+)\s+Total CBD\s+([%\d.]+)'
    cannabinoid_match = re.search(cannabinoid_pattern, text)
    if cannabinoid_match:
        results['total_thc'] = cannabinoid_match.group(1)
        results['total_cbd'] = cannabinoid_match.group(2)

    terpenes_pattern = r'TERPENES\s+([%\d.]+)\s+'
    terpenes_match = re.search(terpenes_pattern, text)
    if terpenes_match:
        results['total_terpenes'] = terpenes_match.group(1)


    # TODO: Find the results.
    results = []



    # TODO: Get the strain name.
    # from cannlytics.data.strains.strains_ai import identify_strains
    # # - strain_name (augmented)



    # Close the report.
    report.close()

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs = {**GREEN_SCIENTIFIC_LABS, **obs}
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['methods'] = json.dumps(methods)
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    # return obs



    # === Tests ===

    # Test URLS.
    # urls = [
    #     'https://www.verifycbd.com/reportv2/6e2dz13003',
    #     'https://www.verifycbd.com/reportv2/69a1z12218',
    #     'https://www.verifycbd.com/reportv2/6b0ez12649',
    # ]
