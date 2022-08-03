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
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

from cannlytics.data.coas import CoADoc

parser = CoADoc()


# It is assumed that the CoA has the following parameters.
SC_LABS_COA = {
    'coa_qr_code_index': None,
    'coa_image_index': 2,
    'coa_page_area': '(0, 350, 612, 520)',
    'coa_distributor_area': '(205, 150, 400, 230)',
    'coa_producer_area': '(0, 150, 204.0, 230)',
    'coa_sample_details_area': [
        (0, 225, 200, 350),
        (200, 225, 400, 350),
    ],
    'coa_fields': {
        'sample_id': 'lab_id',
        'source_metrc_uid': 'metrc_source_id',
        'sample_size': 'sample_weight',
        'unit_mass': 'product_size',
    },
    'coa_replacements': {
        'b_caryophyllene': 'beta_caryophyllene',
        'a_humulene': 'humulene',
        'b_pinene': 'beta_pinene',
        'a_bisabolol': 'alpha_bisabolol',
        'a_pinene': 'alpha_pinene',
        'a_cedrene': 'alpha_cedrene',
        '3_carene': 'carene',
        'g_terpinene': 'gamma_terpinene',
        'r_pulegone': 'pulegone',
        'a_phellandrene': 'alpha_phellandrene',
        'a_terpinene': 'alpha_terpinene',
        'trans_b_farnesene': 'trans_beta_farnesene',
    },
}

DATA_DIR = '../../../.datasets/coas/Flore COA'
doc = DATA_DIR + '/Dylan Mattole/Mattole Valley - Marshmellow OG.pdf'

# DEV:
obs = {}

# Read the PDF.
if isinstance(doc, str):
    report = pdfplumber.open(doc)
else:
    report = doc
front_page = report.pages[0]

# TODO: Get sample details:
# - analyses
# - {analysis}_method
# ✓ product_name
# ✓ product_type
# ✓ producer
# ✓ producer_license_number
# ✓ producer_address
# ✓ distributor
# ✓ distributor_license_number
# ✓ distributor_address
# ✓ batch_number
# ✓ lab_id
# ✓ metrc_source_id
# ✓ date_collected
# ✓ date_received
# ✓ date_tested
# ✓ batch_size
# ✓ sample_weight
# ✓ product_size
# ✓ serving_size
# ✓ sum_of_cannabinoids
# ✓ total_cannabinoids
# ✓ total_thc
# ✓ total_cbd
# ✓ total_terpenes
# ✓ moisture

# Get the lab-specific CoA page areas.
page_area = literal_eval(SC_LABS_COA['coa_page_area'])
distributor_area = literal_eval(SC_LABS_COA['coa_distributor_area'])
producer_area = literal_eval(SC_LABS_COA['coa_producer_area'])
sample_details_area = SC_LABS_COA['coa_sample_details_area']

# Get producer details.
crop = front_page.within_bbox(producer_area)
details = crop.extract_text().replace('\n', '')
address = details.split('Address:')[-1].strip()
business = details.split('Business Name:')[-1].split('License Number:')[0].strip()
license_number = details.split('License Number:')[-1].split('Address:')[0].strip()
parts = address.split(',')
street = parts[0]
subparts = parts[-1].strip().split(' ')
city = ' '.join(subparts[:-2])
try:
    state, zipcode = subparts[-2], subparts[-1]
except IndexError:
    state, zipcode = '', ''
obs['producer'] = business
obs['producer_address'] = address
obs['producer_street'] = street
obs['producer_city'] = city
obs['producer_state'] = state
obs['producer_zipcode'] = zipcode
obs['producer_license_number'] = license_number

# Get distributor details.
crop = front_page.within_bbox(distributor_area)
details = crop.extract_text().replace('\n', ' ')
address = details.split('Address:')[-1].strip()
business = details.split('Business Name:')[-1].split('License Number:')[0].strip()
license_number = details.split('License Number:')[-1].split('Address:')[0].strip()
parts = address.split(',')
street = parts[0]
subparts = parts[-1].strip().split(' ')
city = ' '.join(subparts[:-2])
try:
    state, zipcode = subparts[-2], subparts[-1]
except IndexError:
    state, zipcode = '', ''
obs['distributor'] = business
obs['distributor_address'] = address
obs['distributor_street'] = street
obs['distributor_city'] = city
obs['distributor_state'] = state
obs['distributor_zipcode'] = zipcode
obs['distributor_license_number'] = license_number

# Get sample details.
standard_fields = SC_LABS_COA['coa_fields']
if isinstance(sample_details_area, str):
    sample_details_area = [sample_details_area]
for area in sample_details_area:
    crop = front_page.within_bbox(area)
    details = crop.extract_text().split('\n')
    for d in details:
        if ':' not in d:
            continue
        values = d.split(':')
        key = snake_case(values[0])
        key = standard_fields.get(key, key)
        obs[key] = values[-1]

# Get the date tested, product name, and sample type.
text = front_page.extract_text()
date_tested = text.split('DATE ISSUED')[-1].split('|')[0].strip()
lines = text.split('SAMPLE NAME:')[1].split('\n')
product_name = lines[0]
obs['product_type'] = lines[1]

# Get the moisture content.
value = text.split('Moisture:')[-1].split('%')[0]
obs['moisture'] = convert_to_numeric(value, strip=True)

# TODO: Get analyses.
rects = front_page.rects
for rect in rects:
    crop = front_page.within_bbox((rect['x0'], rect['y0'], rect['x1'], rect['y1']))
    text = crop.extract_text()
    if 'ANALYSIS' in text:
        print(text)
        break

# Get the totals.

value = text.split('Sum of Cannabinoids:')[-1].split('%')[0]
obs['sum_of_cannabinoids'] = convert_to_numeric(value, strip=True)

value = text.split('Total Cannabinoids:')[-1].split('%')[0]
obs['total_cannabinoids'] = convert_to_numeric(value, strip=True)

value = text.split('Total THC:')[-1].split('%')[0]
obs['total_thc'] = convert_to_numeric(value, strip=True)

value = text.split('Total CBD:')[-1].split('%')[0]
obs['total_cbd'] = convert_to_numeric(value, strip=True)

value = text.split('Total Terpenoids:')[-1].split('%')[0]
obs['total_terpenes'] = convert_to_numeric(value, strip=True)

# Get the results.
# FIXME: Is it possible to add `analysis` to the results?
columns = ['name', 'lod', 'loq', 'margin_of_error', 'mg_g', 'value']
results = []
standard_analytes = SC_LABS_COA['coa_replacements']
for page in report.pages[1:]:

    # Get the results from each result page.
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            key = snake_case(row[0])
            key = standard_analytes.get(key, key)
            parts = row[1].split('/')
            subparts = parts[-1].strip().split(' ')
            mg_g, value = tuple(row[-1].split(' '))
            results.append({
                'key': key,
                'lod': convert_to_numeric(parts[0].strip()),
                'loq': convert_to_numeric(subparts[0]),
                'margin_of_error': convert_to_numeric(subparts[-1].replace('±', '')),
                'mg_g': convert_to_numeric(mg_g),
                'name': row[0],
                'value': convert_to_numeric(value),
            })

    # FIXME:
    # Get the methods from the result page text.
    # page_text = page.extract_text()
    # texts = page_text.split('Method:')
    # for text in texts[1:]:
    #     if 'Analysis' in text:
    #         method = text.split('.')[0]
    #         analysis = method.split('Analysis of ')[-1].split(' by')[0].lower()
    #         print(analysis, method)

# Aggregate results.
obs['analyses'] = []
obs['date_tested'] = date_tested
obs['product_name'] = product_name
obs['results'] = results

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

print(obs)
