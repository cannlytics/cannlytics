"""
Parse Sonoma Lab Works CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/4/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Sonoma Lab Works CoA PDFs.

Data Points:

    - analyses
    ✓ {analysis}_method
    - {analysis}_status
    ✓ batch_number
    ✓ batch_size
    - classification
    - coa_urls
    ✓ date_collected
    ✓ date_tested
    ✓ date_received
    ✓ distributor
    ✓ distributor_address
    - distributor_street
    - distributor_city
    - distributor_county
    - distributor_state
    - distributor_zipcode
    - distributor_latitude
    - distributor_longitude
    - images
    - lab_results_url
    ✓ metrc_source_id
    - project_id
    ✓ producer
    ✓ producer_address
    ✓ producer_license_number
    - producer_street
    - producer_city
    - producer_county
    - producer_state
    - producer_zipcode
    - producer_latitude
    - producer_longitude
    ✓ product_name
    ✓ product_type
    - predicted_aromas
    - results
    ✓ sample_weight
    - total_cannabinoids (calculated)
    - total_thc
    - total_cbd
    - total_terpenes (calculated)
    ✓ sample_id (generated)
    - strain_name
    ✓ lab_id
    ✓ lab
    - lab_image_url
    - lab_license_number
    ✓ lab_address
    - lab_city
    - lab_county (augmented)
    - lab_state (augmented)
    - lab_zipcode (augmented)
    - lab_phone
    ✓ lab_email
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from typing import Any

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
)

# It is assumed that the lab has the following details.
SONOMA =  {
    'coa_algorithm': 'sonoma.py',
    'coa_algorithm_entry_point': 'parse_sonoma_coa',
    'lims': 'Sonoma Lab Works',
    'lab': 'Sonoma Lab Works',
    'lab_license_number': '',
    'lab_image_url': '',
    'lab_address': '1201 Corporate Center Parkway, Santa Rosa, CA 95407',
    'lab_street': '1201 Corporate Center Parkway',
    'lab_city': 'Santa Rosa',
    'lab_state': 'CA',
    'lab_zipcode': '95407',
    'lab_latitude': '38.421600',
    'lab_longitude': '-122.752990',
    'lab_phone': '',
    'lab_email': 'testing@sonomalabworks.com',
    'lab_website': 'https://www.sonomalabworks.com/',
}

SONOMA_COA = {
    'coa_analyses': {
        'Foreign Material': 'foreign_matter',
        'Heavy Metals Screen': 'heavy_metals',
        'Microbial Screen': 'microbes',
        'Mycotoxin Screen': 'mycotoxins',
        'Percent Moisture (%)': 'moisture_content',
        'Potency Test Result': 'cannabinoids',
        'Pesticide Screen Result - Category 1': 'pesticides',
        'Pesticide Screen Result - Category 2': 'pesticides',
        'Residual Solvent Screen - Category 1': 'residual_solvents',
        'Residual Solvent Screen - Category 2': 'residual_solvents',
        'Terpene Test Result': 'terpenes',
        'Water Activity (Aw)': 'water_activity',
    },
    'coa_analytes': {
        'delta_9_thc_d_9_thc': 'delta_9_thc',
        'delta_8_thc_d_8_thc': 'delta_8_thc',
        'escherichia_coli_stec': 'e_coli',
        'avermectin_b_1_a_abamectin': 'avermectin_b1a',
        'avermectin_b_1_a_abamectin': 'avermectin_b1b',
        'delta_limonene': 'd_limonene',
        'gama_terpinene': 'gamma_terpinene',
    },
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
        'LOD (mg/g)': 'lod',
        'LOQ (mg/g)': 'loq',
        'LOD (ug/g)': 'lod',
        'LOQ (ug/g)': 'loq',
        'LOD (ug/kg)': 'lod',
        'LOQ (ug/kg)': 'loq',
        'Pass/Fail': 'status',
        'PPM': 'value',
        'PPM (ug/g)': 'value',
        'PPM (ug/kg)': 'value',
        'PPB (ug/g)': 'value',
        'PPB (ug/kg)': 'value',
        'Threshold': 'value',
        'Microbiological Assay': 'name',
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

    # Implement the parsing routine here.


    return {**SONOMA, **obs}

#-----------------------------------------------------------------------
# DEV:
#-----------------------------------------------------------------------

from cannlytics.data.coas import CoADoc
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


#-----------------------------------------------------------------------
# Begin algorithm!
#-----------------------------------------------------------------------

# Get the fields.
standard_analyses = SONOMA_COA['coa_analyses']
standard_analytes = SONOMA_COA['coa_analytes']
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


# FIXME: Get:
# - total_cannabinoids
# - total_thc
# - total_cbd
# - total_terpenes
# - analyses
# - analysis status


# FIXME: Get analysis statuses.


# Get the analyses and results.
analysis = None
analyses = []
columns = []
methods = []
results = []
units = None
tables = report.pages[1].extract_tables()
for table in tables:
    for row in table:

        # Skip the detail rows.
        if len(row) == 2 or not row[0]:
            continue

        # Find the analysis.
        elif '\n' in row[0]:
            parts = row[0].split('\n')
            print(parts[0])
            analysis = standard_analyses.get(parts[0], snake_case(parts[0]))
            analyses.append(analysis)
            for part in parts:
                if 'Method:' in part:
                    method = part \
                        .split('Method:')[-1] \
                        .split('Date Tested:')[0] \
                        .strip()
                    obs[f'{analysis}_method'] = method
                    break

        # Find the table columns.
        elif row[0] == 'Target Analyte' or row[0] == 'Microbiological Assay':
            columns = [x for x in row if x is not None]

            # Identify the units.
            units = None
            for column in columns:
                if column and '(' in column:
                    units = column.split('(')[-1].split(')')[0]

        # Parse the result, standardizing the analyte keys and fields.
        else:
            values = [x for x in row if x is not None]
            result = {'analysis': analysis, 'units': units}
            recorded_keys = []
            for i, column in enumerate(columns):
                if not column:
                    continue
                elif i == 0:
                    analyte = snake_case(values[i])
                    result['key'] = standard_analytes.get(analyte, analyte)
                key = standard_fields.get(column, snake_case(column))
                if key in recorded_keys:
                    continue
                try:
                    result[key] = convert_to_numeric(values[i])
                except IndexError:
                    result[key] = None
                recorded_keys.append(key)
            results.append(result)


# FIXME: Also get:
# - moisture_content
# - water_activity
# - foreign_matter


#--------------------------
# Data cleaning
#--------------------------

# Hot-fix for cannabinoid units.
for i, result in enumerate(results):
    results[i]['units'] = 'percent'

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

# FIXME: Get street, city, state, county, zipcode, latitude, and longitude
# given the `producer_address` and `distributor_address`.


# Future work: Standardize `product_type`.


#--------------------------
# Data aggregation
#--------------------------

# Aggregate results.
obs['analyses'] = list(set(analyses))
obs['results'] = results

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

# [ ] TEST: Parse a Sonoma Lab Works CoA PDF.
# from cannlytics.data.coas import CoADoc
# parser = CoADoc()
# doc = '../../../.datasets/coas/Flore COA/Peak/LemonTree.pdf'
# lab = parser.identify_lims(doc)
# assert lab == 'Sonoma Lab Works'
# data = parse_sonomoa_coa(parser, doc)
# assert data is not None
