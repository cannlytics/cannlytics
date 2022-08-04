"""
Parse Sonoma Lab Works CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/2/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Sonoma Lab Works CoA.

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
SONOMA =  {
    'coa_algorithm': 'sonoma.py',
    'coa_algorithm_entry_point': 'parse_sonoma_coa',
    'lims': 'Sonoma Lab Works',
    'lab': 'Sonoma Lab Works',
    'lab_address': '1201 Corporate Center Parkway, Santa Rosa, CA 95407',
    'lab_street': '1201 Corporate Center Parkway',
    'lab_city': 'Santa Rosa',
    'lab_state': 'CA',
    'lab_zipcode': '95407',
    'lab_latitude': '38.421600',
    'lab_longitude': '-122.752990',
    'lab_email': 'testing@sonomalabworks.com',
    'lab_website': 'https://www.sonomalabworks.com/',
}

SONOMA_COA = {
    'coa_fields': {
        'client': 'producer',
        'client_address': 'producer_address',
        'client_license_number': 'producer_license_number',
        'dates_of_analysis': 'date_tested',
        'sample_code': 'lab_id',
        'sample_type': 'product_type',
        'sample_matrix': 'matrix',
        'sample_name': 'product_name',
        'metrc_tag': 'metrc_source_id',
        'total_batch': 'batch_size',
        'primary_sample': 'sample_weight',
        'Target Analyte': 'name',
        '% Test': 'value',
        'mg/g': 'mg_g',
        'LOD mg/g': 'lod',
        'LOQ mg/g': 'loq',
        'Pass/Fail': 'status',
    },
    'coa_titles': [
        'Test Summary',
        'Sample Information',
    ],
}


def parse_sonomoa_coa(self, doc: Any) -> Any:
    """Parse a Sonoma Lab Works CoA PDF."""
    obs = {}

    # Read the PDF.
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
    else:
        report = doc
    front_page = report.pages[0]

    # TODO: Implement the parsing routine here.


    return {**SONOMA, **obs}


# DEV:
from cannlytics.data.coas import CoADoc

# DEV:
parser = CoADoc()
doc = '../../../.datasets/coas/Flore COA/Peak/LemonTree.pdf'

# Create the observation.
obs = {}

# Read the PDF.
if isinstance(doc, str):
    report = pdfplumber.open(doc)
else:
    report = doc
front_page = report.pages[0]

# Get the fields.
standard_fields = SONOMA_COA['coa_fields']

# Get all of the tables.
tables = []
for page in report.pages:
    tables.extend(page.extract_tables())

# Get the details from the front page.
tables = report.pages[0].extract_tables()
for table in tables:
    for row in table:
        if ':' in str(row[0]):
            if len(row) == 2:
                key = snake_case(row[0])
                key = standard_fields.get(key, key)
                value = row[1]
                obs[key] = value
            elif len(row) == 4:
                key = snake_case(row[0])
                key = standard_fields.get(key, key)
                value = row[1]
                second_key = snake_case(row[2])
                second_key = standard_fields.get(second_key, second_key)
                second_value = row[3]
                obs[key] = value
                obs[second_key] = second_value
    
        # Not necessary to get these other details?
        # else:
        #     for skip in SONOMA_COA['coa_titles']:
        #         if row[0] == skip:
        #             continue
        #     if len(row) == 2:
        #         key = snake_case(row[0])
        #         value = row[1]
        #         print(key, value)
        #         obs[key] = value
        #     else:
        #         pass
            
# TODO: Get:
# - total_cannabinoids
# - total_thc
# - total_cbd
# - total_terpenes
# - analyses
# - analysis status

# TODO: Get analyses.

# TODO: Get analysis statuses.

# TODO: Get results.
analysis = None
analyses = []
columns = []
methods = []
results = []
tables = report.pages[1].extract_tables()
for table in tables:
    for row in table:

        # Skip the detail rows.
        if len(row) == 2 or not row[0]:
            continue

        # FIXME: Elegantly find the analysis.
        elif '\n' in row[0]:
            parts = row[0].split('\n')
            analysis = parts[0]
            # print(analysis)

        # Skip certain rows.
        # for title in SONOMA_COA['coa_titles']:
        #     if row[0] == title:
        #         continue

        # TODO: Get the headers.
        elif row[0] == 'Target Analyte':
            columns = row
            print(row)


        # TODO: Parse the result!
        else:
            result = {'analysis': analysis}

            # FIXME: Get the units!

            for i, column in enumerate(columns):
                key = standard_fields.get(column, snake_case(column))
                result[key] = row[i]
            results.append(result)

        # if len(row) == 5:
        #     print(row)

        # if len(row) == 6:
        #     print(row)

        # if len(row) >= 6:
        #     print(row)

        # if len(row) > 2 and len(row) < 6:
        #     print(row)

        


#--------------------------

# Aggregate results.
# obs['analyses'] = analyses
# obs['results'] = results

# Hot-fix for sample type and sample matrix.
obs['product_type'] = ', '.join([obs['matrix'], obs['product_type']])

# Hot-fix for `date_tested`, e.g. '7/6/2021 - 7/8/2021'.
obs['date_tested'] = obs['date_tested'].split(' - ')[-1]

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

print({**SONOMA, **obs})


#--------------------------
# Tests
#--------------------------

# lab = parser.identify_lims(report, 'Sonoma Lab Works')

# [ ] TEST: Parse a Sonoma Lab Works CoA PDF.
