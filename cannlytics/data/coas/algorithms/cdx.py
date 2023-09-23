"""
CoADoc | Parse CDX Analytics COAs
Copyright (c) 2022 Cannlytics

Authors:
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/25/2022
Updated: 11/25/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse CDX Analytics COA PDFs.

Data Points (✓):

    - analyses
    - methods
    - {analysis}_status
    - date_received
    - date_tested
    - lab_results_url
    - metrc_lab_id
    - metrc_source_id
    - producer
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    - product_name
    - product_type
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


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # Specify testing constants.
    doc = '../../../tests/assets/coas/cdx-analytics/Dosidos #22 - 120821DSDM22-5.pdf'
    parser = CoADoc()
    lims = parser.identify_lims(doc)

    report = pdfplumber.open(doc)
    for page in report.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            print(line)

            # Get sample details.

            # Get client details.

            # Get analyte results
            


