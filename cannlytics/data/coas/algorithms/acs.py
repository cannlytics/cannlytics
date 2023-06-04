"""
Parse ACS Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 6/4/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse ACS Labs COA PDFs.

Data Points:

    - lab_id
    ✓ product_name
    ✓ product_type
    - batch_number
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight
    - sample_id
    - strain_name
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number
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
    - producer
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    - distributor
    - distributor_address
    - distributor_street
    - distributor_city
    - distributor_state
    - distributor_zipcode
    - distributor_license_number
    - date_collected
    - date_tested
    - date_received
    - images
    ✓ analyses
    ✓ {analysis}_status
    ✓ coa_urls
    ✓ lab_results_url
    ✓ status
    - methods
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    - results
        - cannabinoids
        ✓ terpenes
        ✓ pesticides
        ✓ heavy_metals
        - microbes
        ✓ mycotoxins
        - residual_solvents
        ✓ foreign_matter
        ✓ water_activity
        - moisture

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
import json
import re
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.constants import STANDARD_UNITS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
ACS_LABS = {
    'coa_algorithm': 'acs.py',
    'coa_algorithm_entry_point': 'parse_acs_coa',
    'lims': 'ACS Labs',
    'url': 'https://portal.acslabcannabis.com',
    'lab': 'ACS Labs',
    'lab_license_number': 'CMTL-0003',
    'lab_image_url': 'https://global-uploads.webflow.com/630470e960f8722190672cb4/6305a2e849811b34bf18777d_Desktop%20Logo.svg',
    'lab_address': '721 Cortaro Dr, Sun City Center, FL 33573',
    'lab_street': '721 Cortaro Dr',
    'lab_city': 'Sun City Center',
    'lab_county': 'Hillsborough County',
    'lab_state': 'FL',
    'lab_zipcode': '33573',
    'lab_phone': '813-634-4529',
    'lab_email': 'info@acslabcannabis.com',
    'lab_website': 'https://www.acslabcannabis.com/',
    'lab_latitude': 27.713506,
    'lab_longitude': -82.371029,
}
ACS_LABS_COA = {
    'analyses': {
        'Potency': 'cannabinoids',
        'Terpenes': 'terpenes',
        'Pesticides': 'pesticides',
        'Heavy Metals': 'heavy_metals',
        'Pathogenic': 'microbes',
        'Microbiology (qPCR)': 'microbes',
        'Mycotoxins': 'mycotoxins',
        'Residual Solvents': 'residuals_solvents',
        'Filth and Foreign': 'foreign_matter',
        'Total Contaminant Load': 'foreign_matter',
        'Water Activity': 'water_activity',
        'Moisture': 'moisture',
    },
}


def parse_acs_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a TerpLife Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """

    # Get the lab's analyses.
    # lab_analyses = GREEN_LEAF_LAB_ANALYSES
    # coa_parameters = GREEN_LEAF_LAB_COA
    # standard_analyses = list(lab_analyses.keys())
    # analysis_names = [x['name'] for x in lab_analyses.values()]

    # TODO: If the `doc` is a URL, then download the PDF to `temp_path`.
    if temp_path is None:
        # FIXME: Get the user's temp_path
        temp_path = '/tmp'

    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]
    front_page = report.pages[0]

    # Add optional ability to collect the image.
    # - Get the image data.
    # - Save the image to Firebase Storage
    # - Create a dynamic link for the image.

    # TODO: Get the lab details.

    # TODO: Get the sample details.

    # TODO: Get the client details.

    # TODO: Get the analyses.

    # TODO: Get the results.


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc
    from dotenv import dotenv_values

    # Set a Google Maps API key.
    # config = dotenv_values('../../../.env')
    # os.environ['GOOGLE_MAPS_API_KEY'] = config['GOOGLE_MAPS_API_KEY']

    # [✓] TEST: Identify LIMS from a COA URL.
    parser = CoADoc()
    url = 'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQzc0OS0wMTA1MjMtU0dMQzEyLVIzNS0wMjIxMjAyMw=='
    lims = parser.identify_lims(url, lims={'ACS Labs': ACS_LABS})
    assert lims == 'ACS Labs'

    # [✓] TEST: Identify LIMS from a COA PDF.
    parser = CoADoc()
    doc = 'D://data/florida/lab_results/.datasets/pdfs/acs/AAEK703_494480004136268_05082023_64595d681311d-COA_EN.pdf'
    lims = parser.identify_lims(doc, lims={'ACS Labs': ACS_LABS})
    assert lims == 'ACS Labs'
    
    # [ ] TEST: Parse a cannabinoid and terpene only COA from a URL.
    urls = [
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQzc0OS0wMTA1MjMtU0dMQzEyLVIzNS0wMjIxMjAyMw==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEVjIxMC0xMDI1MjItREJGSy1SMzUtMTIxMTIwMjI=',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRTI3OV8yNDEyNzAwMDM4MjU0NzZfMDMwOTIwMjNfNjQwYTcyMTFmMTAyMA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRDk5MV81NzEwNjAwMDM3MTk4MzRfMDMwNjIwMjNfNjQwNjgyN2Y2ZjU4Mg==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDc5N18zMjE1NjAwMDM5ODYxMzZfMDQxMDIwMjNfNjQzNDlhNTJlMmRlYg==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTk5MF8yOTM1MzAwMDM5NDA2MjBfMDQyMTIwMjNfNjQ0MmFhNTJlYjcxMw==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjM5MV8yOTUyNzAwMDQxMzQ3ODZfMDQyNTIwMjNfNjQ0ODFlOTQ1NDBlNQ==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFRjg3MV80OTQ0NzAwMDQwNDgxODVfMDMyMzIwMjNfNjQxY2FmNTllYjcxMA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQTU4NF81NTMxMjAwMDM3ODAxNTBfMDEzMDIwMjNfNjNkODZjNGI2MzQxZQ==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDSDEyMl8yNjU4LTE1OTQtNjk5NC0yNjg5XzEyMjgyMDIxXzYxY2I1MDA1M2YxZjk=',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjQ4OF81NTMwMDAwMDI4OTQ2MzNfMDIxMDIwMjNfNjNlNmM3N2Y1OWJjYw==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQjE5OV8xODM2MTAwMDM3MDUzNzVfMDIwODIwMjNfNjNlM2M5ZmMyMzY4ZQ==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzAwOS1ETFItNDEtU1RQQS1MUkM1LTA1MDEyMDIz',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEWjQ5Ny0xMjE0MjItOTlQUi1SMzUtMDEyMTIwMjM=',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzI3Ny1JRDI0Mi1MUi1RU0ZHLUxSNS0wNTAzMjAyMw==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSjU1Ml81NTc3MzAwMDQwOTUwNzJfMDQyODIwMjNfNjQ0YzFmNjc4YjM3Mg==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFESzE5NV8xODM2MjAwMDMwNTk0MTFfMDkxNTIwMjJfNjMyMzk5M2Y2NTU4MA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTYyOF82MzQyMjAwMDQwNDU4MjFfMDQxOTIwMjNfNjQzZmVjNDliNzk4MQ==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSDkxMS0wMzA2MjMtREJTRC1TSC1TRzM1LTA0MTAyMDIz',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEUTY3MV80OTQ0NzAwMDM0NDUwMTlfMTEwMTIwMjJfNjM2MWM3Y2Q5MGM3MA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzc4M180OTQ0NzAwMDM4NzY5MzZfMDUwOTIwMjNfNjQ1YTUwNWE2OTFmNA==',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDWjkxNl8xODM2MzAwMDI0NDc4NzlSMl8wNjI3MjAyMl82MmI5Y2E4YTI5YmI3',
        'https://www.trulieve.com/files/lab-results/18362_0003059411.pdf',
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSzcwM180OTQ0ODAwMDQxMzYyNjhfMDUwODIwMjNfNjQ1OTVkNjgxMzExZA==',
    ]

    # [ ] TEST: Parse a full panel COA from a URL.
    urls = [
        'https://www.trulieve.com/files/lab-results/27675_0002407047.pdf',
    ]


#-----------------------------------------------------------------------
# === DEV ===
#-----------------------------------------------------------------------

import base64
import re

import pdfplumber
from PIL import Image
import io
import os
import tempfile
from cannlytics import firebase
from cannlytics import __version__
from cannlytics.data.data import create_hash, create_sample_id
from cannlytics.data.coas import CoADoc


def save_image_data(image_data, image_file='image.png'):
    """Save image data to a file."""
    image_bytes = base64.b64decode(image_data)
    image_io = io.BytesIO(image_bytes)
    image = Image.open(image_io)
    image.save(image_file)


def upload_image_data(storage_ref, image_file):
    """Upload image data to Firebase Storage."""
    firebase.initialize_firebase()
    firebase.upload_file(storage_ref, image_file)


def get_rows_between_values(
        original_list,
        start: Optional[str] = '',
        stop: Optional[str] = '',
    ):
    """Get rows between two values."""
    start_index = None
    end_index = None
    for index, line in enumerate(original_list):
        if line.startswith(start) and start_index is None:
            start_index = index + 1
        elif line.startswith(stop) and start_index is not None:
            end_index = index
            break
    if start_index is not None and end_index is not None:
        return original_list[start_index:end_index]
    elif start_index is not None:
        return original_list[start_index:]
    elif end_index is not None:
        return original_list[:end_index]
    else:
        return []


def split_elements(elements, split_words):
    """Split elements in a list by a list of words."""
    cells = []
    for element in elements:
        for word_index, split_word in enumerate(split_words):
            splits = element.split(split_word)
            for split_index, split in enumerate(splits):
                # If it's not the first split, add split_word back.
                if split_index != 0:
                    split = split_word + split
                cells.append(split.strip())
        # Remove empty strings.
        cells = [i for i in cells if i]
    return cells


# DEV: Parse partial COA.
# doc = 'D://data/florida/lab_results/.datasets/pdfs/acs/AAEK703_494480004136268_05082023_64595d681311d-COA_EN.pdf'

# TODO: Parse full panel COA for a concentrate.
doc = './tests/assets/coas/acs/27675_0002407047.pdf'


# TODO: Parse a full panel COA for a flower.
doc = './tests/assets/coas/acs/49448_0004136268.pdf'


# === DEV ===
parser = CoADoc()
fields = {
    'Batch Date': 'date_packaged',
    'Completion Date': 'date_tested',
    'Cultivation Facility': 'producer_address',
    'Cultivars': 'strain_name',
    'Initial Gross Weight': 'sample_weight',
    'Lab Batch Date': 'date_received',
    'Lot ID': 'area_id',
    'Net Weight per Unit': 'serving_size',
    'Number of Units': 'servings_per_package',
    'Order #': 'lab_id',
    'Order Date': 'date_received',
    'Production Date': 'date_harvested',
    'Production Facility': 'distributor_address',
    'Sample #': 'sample_id',
    'Sampling Date': 'date_collected',
    'Sampling Method': 'method_sampling',
    'Seed to Sale #': 'traceability_id',
    'Total Number of Final Products': 'total_products',
    'FL License #': 'lab_license_number',
}


# Read the PDF.
obs = {}
if isinstance(doc, str):
    report = pdfplumber.open(doc)
    obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
else:
    report = doc
    obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

# Get the front page.
front_page = report.pages[0]
text = front_page.extract_text()
lines = text.split('\n')

# Get the lab results URL from the QR code.
coa_url = parser.find_pdf_qr_code_url(front_page)
obs['lab_results_url'] = coa_url

# Format `coa_urls`
if coa_url is not None:
    filename = coa_url.split('/')[-1].split('?')[0] + '.pdf'
    obs['coa_urls'] = json.dumps([{'url': coa_url, 'filename': filename}])

# Get front page text.
page = front_page
left = page.within_bbox((0, 0, page.width * 0.5, page.height))
right = page.within_bbox((page.width * 0.5, 0, page.width, page.height))
rows = left.extract_text().split('\n') + right.extract_text().split('\n')

# FIXME: Get dates.
# - date_collected
# - date_tested
# - date_received
# date_collected = re.findall(r"Sampling Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]
# date_tested = re.findall(r"Lab Batch Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]
# date_received = re.findall(r"Order Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]

# FIXME: Get producer data.
# - producer
# - producer_address
# - producer_street
# - producer_city
# - producer_state
# - producer_zipcode
# - producer_license_number (augment)

# FIXME: Get sample data.
# - lab_id
# - sample_id
# - strain_name
# ✓ product_name
# ✓ product_type
# - batch_number
# - product_size
# - serving_size
# - servings_per_package
# - sample_weight
# - traceability_id
# - area_id (Lot ID)
obs['product_name'] = lines[0]
obs['product_type'] = lines[2]

# Get the analyses and statuses.
tests = 'Potency' + text.split('Potency')[1].split('Product Image')[0]
tests = tests.replace('Not Tested', 'NT')
for k, v in ACS_LABS_COA['analyses'].items():
    tests = tests.replace(k, v)
tests = [x.split(' ') for x in tests.split('\n') if x]

# Determine status for each analysis.
analyses = []
overall_status = 'Pass'
for index, sublist in enumerate(tests):
    if index % 2 == 0:
        analyses.extend(sublist)
    else:
        test_types = analyses[-len(sublist):]
        for k, test_types in enumerate(test_types):
            status = sublist[k].replace('Passed', 'Pass').replace('Failed', 'Fail')
            obs[f'{test_types}_status'] = status
            if 'fail' in status.lower():
                overall_status = 'Fail'
obs['status'] = overall_status

# Parse front page rows.
for i, row in enumerate(rows):

    # FIXME: Get fields.
    for k, v in fields.items():
        pass

    # FIXME: Get cannabinoids.
    get_cannabinoids = False
    if rows.startswith('Delta-9 THC ') or get_cannabinoids:
        if row.startswith('Sample Prepared By'):
            get_cannabinoids = False
        else:
            get_cannabinoids = True

        continue        

    # FIXME: Get total cannabinoids.
    if row.startswith('Total THC'):
        break


# FIXME: Get cannabinoids.


# TODO: Get the methods.
methods = []


# Get results.
# FIXME: Ensure that this works for Flower COAs too.
results = []
page_count = len(report.pages)
# if page_count >= 2:
for page in report.pages[1:]:
    
    # Get page rows from the double column layout.
    page = report.pages[1]
    page_text = page.extract_text()
    left = page.within_bbox((0, 0, page.width * 0.5, page.height))
    right = page.within_bbox((page.width * 0.5, 0, page.width, page.height))
    rows = left.extract_text().split('\n') + right.extract_text().split('\n')

    # TODO: Get microbes.

    # TODO: Get residual solvents.
    
    # Get terpenes.
    if 'Terpenes' in rows:
        terpene_rows = get_rows_between_values(
            rows,
            start='Analyte Dilution',
            stop='Sample Prepared By',
        )
        for line in terpene_rows[1:]:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'lod': convert_to_numeric(values[1]),
                'name': name,
                'units': 'percent',
                'value': convert_to_numeric(values[-1]),
            })

    # Get mycotoxins.
    if 'Mycotoxins' in page_text:
        elements = get_rows_between_values(
            rows,
            start='Mycotoxins',
            stop='Batch Reviewed',
        )
        elements = get_rows_between_values(
            elements,
            start='Analyte',
            stop='Sample Prepared By',
        )
        cells = []
        for element in elements:
            element = element.replace('A\x00atoxin', 'Aflatoxin')
            aflatoxin_splits = element.split('Aflatoxin')
            for i, split in enumerate(aflatoxin_splits):
                second_splits = split.split('Ochratoxin')
                for j, second_split in enumerate(second_splits):
                    if i != 0 and j == 0:  # if it's not the first split, add 'Aflatoxin' back
                        second_split = 'Aflatoxin' + second_split
                    if j != 0:  # if it's not the first split, add 'Ochratoxin' back
                        second_split = 'Ochratoxin' + second_split
                    cells.append(second_split.strip())
        cells = [i for i in cells if i]
        for line in cells[1:]:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'mycotoxins',
                'key': key,
                'lod': convert_to_numeric(values[1]),
                'name': name,
                'units': 'ppb',
                'value': convert_to_numeric(values[-1]),
                'limit': convert_to_numeric(values[-2]),
            })

    # Get heavy metals.
    if 'Heavy Metals' in page_text:
        elements = get_rows_between_values(
            rows,
            start='Heavy Metals',
            stop='Batch Reviewed',
        )
        elements = get_rows_between_values(
            elements,
            start='Analyte',
            stop='Sample Prepared By',
        )
        cells = []
        for element in elements:
            first_split = element.split('Lead')
            for i, split in enumerate(first_split):
                second_splits = split.split('Mercury')
                for j, second_split in enumerate(second_splits):
                    if i != 0 and j == 0:
                        second_split = 'Lead' + second_split
                    if j != 0:
                        second_split = 'Mercury' + second_split
                    cells.append(second_split.strip())
        cells = [i for i in cells if i]
        for line in cells[1:]:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'heavy_metals',
                'key': key,
                'lod': convert_to_numeric(values[0]),
                'name': name,
                'units': 'ppb',
                'value': convert_to_numeric(values[-1]),
                'limit': convert_to_numeric(values[1]),
            })

    # Get pesticides.
    if 'Pesticides' in page_text:
        q1 = page.within_bbox((0, 0, page.width * 0.27, page.height))
        q2 = page.within_bbox((page.width * 0.27, 0, page.width * 0.5, page.height))
        texts = '\n'.join([q1.extract_text(), q2.extract_text()])
        texts = texts.replace('\x00', 'fl')
        cells = texts.split('\n')
        elements = get_rows_between_values(
            cells,
            start='Analyte',
            stop='Lab Batch #',
        )
        set1 = get_rows_between_values(
            elements,
            stop='Sample Prepared By',
        )
        set2 = get_rows_between_values(
            elements,
            start='Analyte',
            stop='Sample Analyzed By',
        )
        table = [x for x in set1 + set2 if len(x.split(' ')) > 1]
        for line in table:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'pesticides',
                'key': key,
                'name': name,
                'units': 'ppb',
                'loq': convert_to_numeric(values[1]),
                'limit': convert_to_numeric(values[2]),
                'value': convert_to_numeric(values[-1]),
            })

    # Get foreign matter.
    if 'Filth and Foreign Material' in page_text:
        elements = get_rows_between_values(
            rows,
            start='Filth and Foreign Material',
            stop='Batch Reviewed',
        )
        elements = get_rows_between_values(
            elements,
            start='Analyte',
            stop='Sample Prepared By',
        )
        split_words = ['Weight']
        cells = split_elements(elements, split_words)
        for line in cells[1:]:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'foreign_matter',
                'key': key,
                'name': name,
                'units': 'percent',
                'value': convert_to_numeric(values[-1]),
                'limit': convert_to_numeric(values[0]),
            })

    # Get water activity.
    if 'Water Activity' in page_text:
        for row in rows:
            if row.startswith('Water Activity 0.65'):
                first_value = find_first_value(row)
                name = row[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = row[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'water_activity',
                    'key': key,
                    'name': name,
                    'units': 'aw',
                    'value': convert_to_numeric(values[-1]),
                    'limit': convert_to_numeric(values[0]),
                })
                break

    # Get total yeast and mold.
    if 'Total Yeast/Mold' in page_text:
        for row in rows:
            if row.startswith('Total Yeast/Mold'):
                first_value = find_first_value(row)
                name = row[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = row[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'microbe',
                    'key': key,
                    'name': name,
                    'units': 'CFU/g',
                    'value': convert_to_numeric(values[-1]),
                    'status': values[-1],
                    'limit': convert_to_numeric(values[0]),
                })
                break


# Get the image data (Optional: Also get a URL for the image?).
# image_index = 5
# temp_dir = tempfile.gettempdir()
# file_ref = f'data/lab_results/images/{lab_id}/image_data.png'
# file_path = os.path.join(temp_dir, 'image_data.png')
# image_data = parser.get_pdf_image_data(front_page, image_index=image_index)
# save_image_data(image_data, image_file=file_path)
# firebase.initialize_firebase()
# firebase.upload_file(file_ref, file_path)
# obs['image_data_ref'] = file_ref

# DEV:
# image_index = coa_parameters['coa_image_index']
# obs['image_data'] = self.get_pdf_image_data(report.pages[0], image_index)
# obs['images'] = []
# temp_dir = tempfile.gettempdir()
# file_path = os.path.join(temp_dir, 'image_data.png')
# for i, image in enumerate(front_page.images):
# image_data = parser.get_pdf_image_data(front_page, image_index=5)
# image_bytes = base64.b64decode(image_data)
# image_io = io.BytesIO(image_bytes)
# image = Image.open(image_io)
# display(image)

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
obs = {**ACS_LABS, **obs}
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
