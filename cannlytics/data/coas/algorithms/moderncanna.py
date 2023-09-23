"""
Parse Modern Canna Science COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 5/21/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Modern Canna Science Labs COA PDFs.

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
MODERNCANNA = {
    'coa_algorithm': 'moderncanna.py',
    'coa_algorithm_entry_point': 'parse_moderncanna_coa',
    'lims': 'Modern Canna Science',
    'lab': 'Modern Canna Science',
    'lab_image_url': 'https://moderncanna.com/wp-content/uploads/2019/08/logo2019.png',
    'lab_address': 'https://moderncanna.com/',
    'lab_street': '4705 Old Rd 37',
    'lab_city': 'Lakeland',
    'lab_county': 'Polk County',
    'lab_state': 'FL',
    'lab_zipcode': '33813',
    'lab_phone': '863-608-7800',
    'lab_email': 'info@moderncanna.com',
    'lab_website': 'https://moderncanna.com/',
    'lab_latitude': 27.980038,
    'lab_longitude': -81.961967,
}


def parse_moderncanna_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a ModernCanna Labs COA PDF.
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

    # [ ] TEST: Identify LIMS.
    parser = CoADoc()
    doc = ''
    lims = parser.identify_lims(doc, lims={'Modern Canna Science': MODERNCANNA})
    assert lims == 'Modern Canna Science'


    # [ ] TEST: Parse a Modern Canna Science COA from a URL.
    urls = [
        'https://moderncanna.com/coa/HD10010-01.pdf',
        'https://moderncanna.com/coa/HD12005-01.pdf',
        'https://moderncanna.com/coa/HD19005-11.pdf',
    ]

