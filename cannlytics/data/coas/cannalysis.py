"""
Parse Cannalysis CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/2/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Cannalysis CoA.

Data Points:

Static Data Points:

"""
# Standard imports.
from ast import literal_eval
import re
from typing import Any

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import (
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
CANNALYSIS =  {
    'coa_algorithm': 'cannalysis.py',
    'coa_algorithm_entry_point': 'parse_cannalysis_coa',
    'lims': 'Cannalysis',
    'lab': 'Cannalysis',
    'lab_website': '',
}


# DEV:
from cannlytics.data.coas import CoADoc

# DEV:
parser = CoADoc()
doc = '../../../.datasets/coas/Flore COA/Kiva/MothersMilk.pdf'


# Create the observation.
obs = {}

# Read the PDF.
if isinstance(doc, str):
    report = pdfplumber.open(doc)
else:
    report = doc
front_page = report.pages[0]

# Get the QR code from the last page.
lab_results_url = parser.find_pdf_qr_code_url(report)

# TODO: Get the sample details.
# - product_name
# - date_collected
# - date_received
{
    'sample_name': 'product_name',
    'matrix': 'product_type',
    'batch_id': 'metrc_source_id',
    'track_and_trace_test_package': 'metrc_lab_id',
    'collected': 'date_collected',
    'received': 'date_received',
    'batch_size': '',
    'sample_size': '',
    'manufacture_date': 'date_produced',
}

# TODO: Get the lab details.


# TODO: Get the distributor data.


# TODO: Get the producer data.


# TODO: Get the totals.
# - total_cannabinoids
# - total_thc
# - total_cbd

# TODO: Get the analyses and analysis statuses.

# TODO: Get the results.
# - key, name, value, lod, loq, limit, status, units




# Optional: Get the image data.


#--------------------------

# Aggregate results.
# obs['analyses'] = analyses
# obs['results'] = results
obs['lab_results_url'] = lab_results_url

# Turn dates to ISO format.
date_columns = [x for x in obs.keys() if x.startswith('date')]
for date_column in date_columns:
    try:
        obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
    except:
        pass

# Finish data collection with a freshly minted sample ID.
obs['sample_id'] = create_sample_id(
    private_key=obs['producer'],
    public_key=obs['product_name'],
    salt=obs['date_tested'],
)

print({**CANNALYSIS, **obs})

# [ ] TEST: Parse a Cannalysis CoA PDF.
