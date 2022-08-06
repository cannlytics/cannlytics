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

    ✓ lab_results_url

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
    'lab_license_number': '',
    'lab_image_url': '',
    'lab_address': '',
    'lab_street': '',
    'lab_city': '',
    'lab_county': '',
    'lab_state': 'CA',
    'lab_zipcode': '',
    'lab_latitude': 0,
    'lab_longitude': 0,
    'lab_phone': '',
    'lab_email': '',
    'lab_website': '',
}

CANNALYSIS_COA = {
    'coa_page_area': '(0, 198, 612, 693)',
    'coa_distributor_area': '(0, 79.2, 244.8, 142.56)',
    'coa_producer_area': '(244.8, 79.2, 612, 142.56)',
    'coa_sample_details_area': '(0, 126.72, 612, 205.92)',
    'coa_fields': {
        'sample_name': 'product_name',
        'matrix': 'product_type',
        'batch_id': 'metrc_source_id',
        'track_and_trace_test_package': 'metrc_lab_id',
        'collected': 'date_collected',
        'received': 'date_received',
        'batch_size': '',
        'sample_size': '',
        'manufacture_date': 'date_produced',
    },
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

# Get the lab specifics.
coa_parameters = CANNALYSIS_COA

# Get the lab-specific CoA page areas.
page_area = literal_eval(coa_parameters['coa_page_area'])
distributor_area = literal_eval(coa_parameters['coa_distributor_area'])
producer_area = literal_eval(coa_parameters['coa_producer_area'])
sample_details_area = literal_eval(coa_parameters['coa_sample_details_area'])

# Get all distributor details.
crop = front_page.within_bbox(distributor_area)
details = crop.extract_text().split('\n')
address = details[2]
parts = address.split(',')
street = parts[0]
subparts = parts[-1].strip().split(' ')
city = ' '.join(subparts[:-2])
state, zipcode = subparts[-2], subparts[-1]
address = ','.join([street, details[3]])
obs['distributor'] = details[1]
obs['distributor_address'] = address
obs['distributor_street'] = street
obs['distributor_city'] = city
obs['distributor_state'] = state
obs['distributor_zipcode'] = zipcode
obs['distributor_license_number'] = details[-1]


# TODO: Get the sample details.
# - product_name
# - date_collected
# - date_received

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

# # Aggregate results.
# # obs['analyses'] = analyses
# # obs['results'] = results
# obs['lab_results_url'] = lab_results_url

# # Turn dates to ISO format.
# date_columns = [x for x in obs.keys() if x.startswith('date')]
# for date_column in date_columns:
#     try:
#         obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
#     except:
#         pass

# # Finish data collection with a freshly minted sample ID.
# obs['sample_id'] = create_sample_id(
#     private_key=obs['producer'],
#     public_key=obs['product_name'],
#     salt=obs['date_tested'],
# )

# print({**CANNALYSIS, **obs})


# === Test ===
# if __name__ == '__main__':

#     from cannlytics.data.coas import CoADoc

    # [ ] TEST: Parse a Cannalysis CoA PDF.
    # parser = CoADoc()
    # doc = '../../../.datasets/coas/Flore COA/Peak/LemonTree.pdf'
    # lab = parser.identify_lims(doc)
    # assert lab == 'Sonoma Lab Works'
    # data = parse_cannalysis_coa(parser, doc)
    # assert data is not None
