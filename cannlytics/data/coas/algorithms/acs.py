"""
Parse ACS Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 5/21/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse ACS Labs COA PDFs.

Data Points:

    - analyses
    - {analysis}_method
    - {analysis}_status
    - coa_urls
    - date_collected
    - date_tested
    - date_received
    - distributor
    - distributor_address
    - distributor_street
    - distributor_city
    - distributor_state
    - distributor_zipcode
    - distributor_license_number
    - images
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
    - metrc_ids
    - metrc_lab_id
    - metrc_source_id
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight
    - results
    - status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_cbg
    - total_thcv
    - total_cbc
    - total_cbdv
    - total_terpenes
    - sample_id
    - strain_name (augmented)
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
from cannlytics.data.data import create_sample_id
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


# TODO: Make this a main function.
def save_image_data(image_data, image_file='image.png'):
    """Save image data to a file."""
    image_bytes = base64.b64decode(image_data)
    image_io = io.BytesIO(image_bytes)
    image = Image.open(image_io)
    image.save(image_file)


# TODO: Make this a main function.
def upload_image_data(storage_ref, image_file):
    """Upload image data to Firebase Storage."""
    firebase.initialize_firebase()
    firebase.upload_file(storage_ref, image_file)


# DEV: Parse partial COA.
# doc = 'D://data/florida/lab_results/.datasets/pdfs/acs/AAEK703_494480004136268_05082023_64595d681311d-COA_EN.pdf'

# DEV: Parse full COA.
doc = 'D://data/florida/lab_results/.datasets/pdfs/acs/full/27675_0002407047.pdf'

# Read the PDF.
# TODO: Get `coa_urls`
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

# Split the text into lines
lines = text.split('\n')

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
    'Total Number of Final Products': 'total_products'
}

# FIXME: Get analysis data.
# - analyses
# - {analysis}_method
# - {analysis}_status
analyses = []
analyses = re.findall(r"(Potency|Terpenes|Heavy Metals|Mycotoxins|Pesticides|Residual Solvents|Moisture|Water Activity|Pathogenic Microbiology|Filth and Foreign Total Contaminant|Total Contaminant)\s+(Tested|Not Tested|Passed)", text)

# TODO: Get status.
# - status

# TODO: Get dates.
# - date_collected
# - date_tested
# - date_received
date_collected = re.findall(r"Sampling Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]
date_tested = re.findall(r"Lab Batch Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]
date_received = re.findall(r"Order Date:\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)[0]


# TODO: Get producer data.
# - producer
# - producer_address
# - producer_street
# - producer_city
# - producer_state
# - producer_zipcode
# - producer_license_number (augment)

# TODO: Get sample data.
# - lab_id
# - sample_id
# - strain_name
# - product_name
# - product_type
# - batch_number
# - product_size
# - serving_size
# - servings_per_package
# - sample_weight
# - traceability_id
# - area_id (Lot ID)

# - metrc_ids
# - metrc_lab_id
# - metrc_source_id



# TODO: Get totals.
# - total_cannabinoids
# - total_thc
# - total_cbd
# - total_terpenes

# TODO: Get the methods.
methods = []

# TODO: Get results.
# - results
results = []

# TODO: Get cannabinoids.

# TODO: Get heavy metals.

# TODO: Get terpenes.



# Get the image data (Optional: Also get a URL for the image?).
image_index = 5
temp_dir = tempfile.gettempdir()
file_ref = f'data/lab_results/images/{lab_id}/image_data.png'
file_path = os.path.join(temp_dir, 'image_data.png')
image_data = parser.get_pdf_image_data(front_page, image_index=image_index)
save_image_data(image_data, image_file=file_path)
firebase.initialize_firebase()
firebase.upload_file(file_ref, file_path)
obs['image_data_ref'] = file_ref

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

# Get the lab results URL from the QR code.
obs['lab_results_url'] = parser.find_pdf_qr_code_url(front_page)

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
obs['results'] = results
obs['results_hash'] = create_hash(results)
obs['sample_id'] = create_sample_id(
    private_key=json.dumps(results),
    public_key=obs['product_name'],
    salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
)
obs['sample_hash'] = create_hash(obs)
# return obs
