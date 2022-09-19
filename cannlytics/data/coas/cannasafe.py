"""
Parse CannaSafe CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 9/17/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a CannaSafe CoA PDF.

Data Points:

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
CANNASAFE = {
    'coa_algorithm': 'cannasafe.py',
    'coa_algorithm_entry_point': 'parse_cannasafe_coa',
    'lims': 'CannaSafe',
    'lab': 'CannaSafe',
    'lab_image_url': '',
    'lab_license_number': ' ', # <- Make dynamic.
    'lab_address': '', # <- Make dynamic.
    'lab_street': '', # <- Make dynamic.
    'lab_city': '', # <- Make dynamic.
    'lab_county': '', # <- Make dynamic.
    'lab_state': 'CA', # <- Make dynamic.
    'lab_zipcode': '', # <- Make dynamic.
    'lab_phone': '', # <- Make dynamic.
    'lab_email': '', # <- Make dynamic.
    'lab_website': '',
    'lab_latitude': 0, # <- Make dynamic.
    'lab_longitude': 0, # <- Make dynamic.
}


def parse_cannasafe_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a CannaSafe CoA PDF.
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


# TEST:
url = 'https://tracker.csalabs.com/public/samples/lllora'
doc = '../../../tests/assets/coas/cannasafe/Grape-CBD-Gummies.pdf'
report = pdfplumber.open(doc)


