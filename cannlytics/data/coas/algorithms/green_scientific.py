"""
Parse Green Scientific Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/12/2023
Updated: 11/12/2023
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
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import STANDARD_UNITS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
GREEN_SCIENTIFIC_LABS = {
    'coa_algorithm': 'green_scientific.py',
    'coa_algorithm_entry_point': 'parse_green_scientific_coa',
    'url': 'https://www.greenscientificlabs.com',
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


# === DEV ===
from cannlytics.data.coas import CoADoc

# Parameters.
doc = '70897.pdf'
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
parser = CoADoc()
print(parser.identify_lims(doc))

# TODO: Either use or find the COA URL.
# - coa_url
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


# TODO: Find the analyses.
# - analyses


# TODO: Find the methods.
# - methods


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


# TODO: Find the results.
# - results



# TODO: Get the strain name.
from cannlytics.data.strains.strains_ai import identify_strains
# - strain_name (augmented)



# === Tests ===

# Test URLS.
# urls = [
#     'https://www.verifycbd.com/reportv2/6e2dz13003',
#     'https://www.verifycbd.com/reportv2/69a1z12218',
#     'https://www.verifycbd.com/reportv2/6b0ez12649',
# ]
