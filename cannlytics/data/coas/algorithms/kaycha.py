"""
Parse Kaycha Labs COAs
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 5/20/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Kaycha Labs CoA PDF.

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
    - lab
    - lab_image_url
    - lab_license_number
    - lab_address
    - lab_street
    - lab_city
    - lab_county (augmented)
    - lab_state
    - lab_zipcode
    - lab_phone
    - lab_email
    - lab_website
    - lab_latitude (augmented)
    - lab_longitude (augmented)

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
KAYCHA_LABS = {
    'coa_algorithm': 'kaycha.py',
    'coa_algorithm_entry_point': 'parse_kaycha_coa',
    'lims': 'Kaycha Labs',
    'lab': 'Kaycha Labs',
    'lab_image_url': 'https://www.kaychalabs.com/wp-content/uploads/2020/06/newlogo-2.png',
    'lab_address': '4101 SW 47th Ave, Suite 105, Davie, FL 33314',
    'lab_street': '4101 SW 47th Ave, Suite 105',
    'lab_city': 'Davie',
    'lab_county': 'Broward',
    'lab_state': 'FL',
    'lab_zipcode': '33314',
    'lab_phone': '833-465-8378',
    'lab_email': 'info@kaychalabs.com',
    'lab_website': 'https://www.kaychalabs.com/',
    'lab_latitude': 26.071350,
    'lab_longitude': -80.210750,
}


def parse_kaycha_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a Kaycha Labs COA PDF.
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

    # [✓] TEST: Identify LIMS.
    parser = CoADoc()
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/MMTC-2019-0020/7240484786331-King_Louis_OG_Persy_Rosin.pdf'
    lims = parser.identify_lims(doc, lims={'Kaycha Labs': KAYCHA_LABS})
    assert lims == 'Kaycha Labs'

    # [ ] TEST: Parse Kaycha Labs COAs from URL.
    url = 'https://tn.yourcoa.com/api/coa-download?sample=KN20119003-002&wl_id=291'


    # [ ] TEST: Parse a cannabinoid and terpene only COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/MMTC-2019-0015/GA11104001-001.pdf'


    # [ ] TEST: Parse a full panel COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/MMTC-2019-0020/7240484786331-King_Louis_OG_Persy_Rosin.pdf'


# === DEV ===

fields = {
    'Matrix': '',
    'Sample': '',
    'Harvest/Lot ID': '',
    'Batch#': '',
    'Cultivation Facility': '',
    'Processing Facility': '',
    'Seed to Sale#': '',
    'Batch Date': '',
    'Sample Size Received': '',
    'Total Batch Size': '',
    'Retail Product Size': '',
    'Ordered': '',
    'Sampled': '',
    'Completed': '',
    'Sampling Method': '',
}

# Read the PDF.
report = pdfplumber.open(doc)

# TODO: Save the image to Firebase Storage.

# Get the text of the first page.
front_page = report.pages[0]
text = front_page.extract_text()
lines = text.split('\n')

product_name = lines[1]
strain_name = lines[2]
product_type = lines[3].split(':')[-1].strip()
lab_street = lines[4].title()
parts = lines[5].split(',')
city, state, zipcode = [x.strip() for x in parts[:3]]
city = city.title()

lab_id = lines[6].split(':')[-1].strip()

import json

# Certificate text
text = """
[Your Certificate Data Here]
"""

# Split the text into lines
lines = text.split('\n')

# Extract necessary data
analyses = ['Pesticides', 'Heavy Metals', 'Microbials', 'Mycotoxins', 'Residuals Solvents', 'Filth', 'Water Activity', 'Moisture', 'Terpenes', 'Cannabinoid']