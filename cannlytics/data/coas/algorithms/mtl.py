"""
Parse Method Testing Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 5/21/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Method Testing Labs COA PDFs.

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
MTL_LABS = {
    'coa_algorithm': 'mtl.py',
    'coa_algorithm_entry_point': 'parse_mtl_coa',
    'url': 'http://mete.labdrive.net',
    'lims': 'Method Testing Labs',
    'lab': 'Method Testing Labs',
    'lab_image_url': '',
    'lab_address': '',
    'lab_street': '',
    'lab_city': '',
    'lab_county': '',
    'lab_state': 'FL',
    'lab_zipcode': '',
    'lab_phone': '',
    'lab_email': '',
    'lab_website': '',
    'lab_latitude': 0,
    'lab_longitude': 0,
}


def parse_mtl_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a Method Testing Labs COA PDF.
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

    # [✓] TEST: Identify LIMS from a COA URL.
    parser = CoADoc()
    url = 'http://mete.labdrive.net/s/KmXMdYTFR3dsceG'
    lims = parser.identify_lims(url, lims={'Method Testing Labs': MTL_LABS})
    assert lims == 'Method Testing Labs'

    # [✓] TEST: Identify LIMS from a COA PDF.
    parser = CoADoc()
    doc = 'D://data/florida/lab_results/.datasets/pdfs/mtl/COA_2305CBR0001-004.pdf'
    lims = parser.identify_lims(doc, lims={'Method Testing Labs': MTL_LABS})
    assert lims == 'Method Testing Labs'

    # [ ] TEST: Parse a Method Testing Labs COA from a URL.
    urls = [
        'http://mete.labdrive.net/s/KmXMdYTFR3dsceG',
        'http://mete.labdrive.net/s/KmXMdYTFR3dsceG/download/COA_2305CBR0001-004.pdf',
        'https://mete.labdrive.net/s/se8BcYZJAMqaYrE',
        'https://coaportal.com/sunburn/report/?search=0524324712189959',
        'https://coaportal.com/sunburn/report/?search=9586770498778201',
        'https://coaportal.com/sunburn/report/?search=8315430847060831',
        'https://coaportal.com/sunburn/report/?search=Sunburn-3807806169682269-2303CTB0044-003',
    ]
