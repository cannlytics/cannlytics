"""
Parse KCA Labs CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 9/19/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse KCA Labs CoA PDFs.

Data Points:

"""
# Standard imports.
from datetime import datetime
import json
import re
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber
import requests

# Internal imports.
from cannlytics import __version__
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
KCA_LABS = {
    'coa_algorithm': 'kcalabs.py',
    'coa_algorithm_entry_point': 'parse_kcalabs_coa',
    'url': 'https://kcalabs.com',
    'lims': 'KCA Labs',
    'lab': 'KCA Labs',
    'lab_image_url': 'https://kcalabs.com/wp-content/uploads/2021/07/KCALABS_FI-2.png',
    'lab_license_number': 'P_0058',
    'lab_address': '232 North Plaza Drive, Nicholasville, KY 40356',
    'lab_street': '232 North Plaza Drive',
    'lab_city': 'Nicholasville',
    'lab_county': 'Jessamine',
    'lab_state': 'KY',
    'lab_zipcode': '40356',
    'lab_phone': '+1-833-KCA-LABS',
    'lab_email': 'trustedresults@kcalabs.com',
    'lab_website': 'https://kcalabs.com',
    'lab_latitude': 37.904740,
    'lab_longitude': -84.566980,
}
KCA_LABS_ANALYSES = {
    'cannabinoids': {
        'columns': ['name', 'lod', 'loq', 'value', 'mg_g'],
    },
    # 'pesticides': {
    #     'name': 'Pesticide Analysis by GCMS/LCMS',
    #     'columns': ['name', 'value', 'limit', 'lod', 'loq', 'units'],
    #     'double_column': True,
    # },
    # 'water_activity': {
    #     'name': 'Water Activity by Aqua Lab',
    #     'columns': ['name', 'value', 'units', 'lod', 'loq'],
    # },
    # 'moisture_content': {
    #     'name': 'Moisture by Moisture Balance',
    #     'columns': ['name', 'value', 'units'],
    # },
    # 'terpenes': {
    #     'name': 'Terpene Analysis by GCMS',
    #     'columns': ['name', 'value', 'mg_g'],
    #     'double_column': True,
    # },
    # 'heavy_metals': {
    #     'name': 'Metals Analysis by ICPMS',
    #     'columns': ['name', 'value', 'limit', 'lod', 'loq', 'units'],
    # },
    # 'mycotoxins': {
    #     'name': 'Mycotoxins by LCMSMS',
    #     'columns': ['name', 'value', 'limit', 'loq', 'loq', 'units'],
    # },
    # 'microbials': {
    #     'name': 'Microbials by PCR',
    #     'columns': ['name', 'status', 'limit', 'lod', 'loq', 'units', 'value'],
    # },
    # 'foreign_matter': {
    #     'name': 'Filth and Foreign Material Inspection by Magnification',
    #     'columns': ['name', 'status', 'limit', 'lod', 'loq', 'units'],
    # },
}
KCA_LABS_COA = {
   'coa_skip_values': [
        'Summary',
        'Test Date Tested Status',
        'Normalization',
        'LOD LOQ Result Result',
        'Analyte',
        '(%) (%) (%) (mg/unit)',
    ],
    'coa_sample_detail_fields': {
        'Sample ID': 'lab_id',
        'Batch': 'batch_number',
        'Received': 'received_at',
        'Type': 'product_type',
        'Completed': 'completed_at',
        'Matrix': 'product_subtype',
        'Unit Mass (g)': 'sample_weight',
    },
}

# Constants
coa_skip_values = [
    'Summary',
    'Test Date Tested Status',
    'Normalization',
    'LOD LOQ Result Result',
    'Analyte',
    '(%) (%) (%) (mg/unit)',
]
coa_sample_detail_fields = {
    'Sample ID': 'lab_id',
    'Batch': 'batch_number',
    'Received': 'date_received',
    'Type': 'product_type',
    'Completed': 'date_completed',
    'Matrix': 'product_subtype',
    'Unit Mass (g)': 'sample_weight',
}
coa_numeric_columns = [
    'sample_weight',
]


def parse_kcalabs_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a KCA Labs CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    obs = {}

    # TODO: Get the lab's parameters.
    # lab_analyses = GREEN_LEAF_LAB_ANALYSES
    # coa_parameters = GREEN_LEAF_LAB_COA
    # standard_analyses = list(lab_analyses.keys())
    # analysis_names = [x['name'] for x in lab_analyses.values()]

    # If the `doc` is a URL, then download the PDF to `temp_path`.
    # Otherwise open a PDF file or use a PDF instance.
    if isinstance(doc, str):
        if doc.startswith('https'):
            if temp_path is None:
                # FIXME: Get the user's temp_path
                temp_path = '/tmp'
            filename = doc.split('/')[-1]
            filepath = f'{temp_path}/{filename}.pdf'
            # FIXME: Will need to get `coa_url`.
            with open(filepath, 'wb') as f:
                f.write(requests.get(url, headers=DEFAULT_HEADERS).content)
            report = pdfplumber.open(filepath)
            obs['coa_pdf'] = f'{filename}.pdf'
        else:
            report = pdfplumber.open(doc)
            obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]
    front_page = report.pages[0]

    raise NotImplementedError


# === Tests ===

from cannlytics.data.coas import CoADoc


# Initialize a COA parser.
parser = CoADoc()

# Parse a COA with cannabinoid-only testing.
url = 'https://kcalabs.qbench.net/pr/ee1b30d13037a54'
doc = '../../../tests/assets/coas/kca-labs/Tangie.pdf'

# Parse a COA with full QC testing.
# url = 'https://kcalabs.qbench.net/pr/c1f17c307ca6dc2'
# doc = '../../../tests/assets/coas/kca-labs/Elyxer-Gummies.pdf'

# Read the PDF.
report = pdfplumber.open(doc)
front_page = report.pages[0]

# TODO: Get the image.
# - Save the image locally from the image data.
# - Upload the image to Firebase Storage.
# - Create a dynamic link for the image (`sample_image_url`).
img = front_page.images[3]

# Get the front page text.
text = front_page.extract_text()
split = re.split('\d+ of \d+', text)
header = split[0]
body = split[-1].split('ND = Not Detected')[0]
lines = body.split('\n')
lines = [x for x in lines if x.strip()]

# Optional: Get the lab details from the header.
# block = header.split('\n')
# street = block[1].replace('https://kcalabs.com', '').strip()
# address_parts = block[2].split('Lic.#')
# obs['lab_license_number'] = address_parts[-1].strip()
# address = address_parts[0]

# TODO: Get the client details (if present).

# Future work: Get the moisture content and foreign matter.

# Iterate over lines to get sample details and cannabinoid results.
obs = {}
analyses = []
dates_tested = []
product_name = lines[0]
results = []
for line in lines[1:]:

    # Remove excess spaces from the lines.
    line_text = line.strip()

    # Skip nuisance rows.
    if line_text in coa_skip_values:
        continue

    # Get the sample details.
    # FIXME: Handle COAs with client details.
    elif ':' in line_text:
        fields = list(coa_sample_detail_fields.keys())
        for field in fields:
            if f'{field}:' in line_text:
                key = coa_sample_detail_fields[field]
                if obs.get(key):
                    continue
                detail = line_text.replace(f'{field}:', '').strip()
                secondary_detail = None
                for secondary_field in fields:
                    if secondary_field != field and f'{secondary_field}:' in detail:
                        parts = detail.split(f'{secondary_field}:')
                        secondary_detail = parts[-1].strip()
                        secondary_key = coa_sample_detail_fields[secondary_field]
                        obs[secondary_key] = secondary_detail
                        obs[key] = parts[0].strip()
                        continue
                if secondary_detail is None:
                    obs[key] = detail

    # Get the analyses and date tested.
    elif line_text.endswith('Tested'):
        parts = line_text.replace('Tested', '').strip().split(' ')
        date = pd.to_datetime(parts[-1])
        dates_tested.append(date)

    # Get the analysis method.
    elif ' by ' in line_text:
        parts = line_text.split(' by ')
        analysis = parts[0].lower()
        analysis = parser.analyses.get(analysis, analysis)
        method = parts[-1]
        obs[f'{analysis}_method'] = method

    # Get the total cannabinoids.
    elif line_text.startswith('Total') and not line_text.endswith('Internal Standard'):
        parts = line_text.split(' ')
        parts = [x for x in parts if x.strip()]
        key = snake_case(parts[0])
        if key == 'total':
            key = 'total_cannabinoids'
        key = parser.fields.get(key, key)
        obs[key] = convert_to_numeric(parts[1])

    # Get the cannabnoid results.
    else:
        parts = line_text.split(' ')
        parts = [x for x in parts if x.strip()]
        name = parts[0]
        analyte = snake_case(name)
        analyte = parser.analytes.get(analyte, analyte)
        columns = KCA_LABS_ANALYSES['cannabinoids']['columns']
        result = {
            'analysis': 'cannabinoids',
            'units': 'percent',
            'key': analyte,
        }
        for i, column in enumerate(columns):
            result[column] = convert_to_numeric(parts[i])
        if name == 'Total' or isinstance(result['name'], float):
            continue
        results.append(result)

# Get the results from the subsequent pages.
for page in report.pages[1:]:

    # Split at page number to remove the header,
    # then split at the note to remove the footer,
    # then remove the product name and sample details.
    text = page.extract_text()
    split = re.split('\d+ of \d+', text)
    body = split[-1].split('ND = Not Detected')[0]
    lines = body.split('\n')
    lines = [x for x in lines if x.strip()]
    lines = [x for x in lines if x != product_name and ':' not in x]

    # Get the analysis and analysis method.
    analysis_parts = lines[0].strip().split(' by ')
    analysis = snake_case(analysis_parts[0])
    analysis = parser.analyses.get(analysis, analysis)
    obs[f'{analysis}_method'] = analysis_parts[-1]
    analyses.append(analysis)

    # Get the columns.
    columns = lines[1].split(' ')
    columns = [x.lower() for x in columns if x and '(' not in x]
    columns = [x.replace('result', 'value').replace('analyte', 'name') for x in columns]
    units = lines[1].split('(')[-1].split(')')[0]
    if 'name' not in columns:
        if len(columns) == 6:
            columns = ['name'] + columns[:3] + ['name'] + columns[3:]
        else:
            columns.insert(0, 'name')

    # Compile the results.
    for line in lines[2:]:
        result = {'analysis': analysis, 'units': units}
        values = line.split(' ')

        # FIXME: If name is in the columns twice, then handle accordingly.
        # FIXME: Combine analyte names with spaces
        k = len(columns)
        if len(values) > k:
            half_point = round(k / 2)
            first_break = 1
            if k % 2 ==0 :
                first_break = 2
            second_break = - (half_point + 1)
            values = [' '.join(values[:first_break])] + values[first_break:half_point]
            values = [' '.join(values[half_point:second_break])] + values[second_break:]

        # Record the result values.
        for i, column in enumerate(columns):
            result[column] = convert_to_numeric(values[i])
            if column == 'name':
                analyte = snake_case(result['name'])
                analyte = parser.analytes.get(analyte, analyte)
                result['key'] = analyte
        results.append(result)

# Turn dates to ISO format.
date_columns = [x for x in obs.keys() if x.startswith('date')]
for date_column in date_columns:
    try:
        obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
    except:
        pass

# Ensure numeric columns are numeric.
for col in coa_numeric_columns:
    obs[col] = convert_to_numeric(obs[col])

# Finish data collection with a freshly minted sample ID.
date_tested = max(dates_tested).isoformat()
obs['analyses'] = analyses
obs['date_tested'] = date_tested
obs['product_name'] = product_name
obs['results'] = results

# TODO: Create `sample_hash` and `results_hash`.


obs['sample_id'] = create_sample_id(
    private_key=json.dumps(results),
    public_key=product_name,
    salt=date_tested,
)
obs['coa_parsed_at'] = datetime.now().isoformat()
obs['coa_algorithm_version'] = __version__
print({**KCA_LABS, **obs})


# Cannabis Data Science Exercise:
# Look at the Tangie relative to other Tangie test results from
# MCR Labs, SC Labs, and PSI Labs.
