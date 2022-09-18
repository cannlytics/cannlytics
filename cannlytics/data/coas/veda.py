"""
Parse Veda Scientific CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/15/2022
Updated: 9/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Veda Scientific CoA PDF.

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ analysis_type
    ✓ {analysis}_status
    x coa_urls
    ✓ date_tested
    - date_received
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ distributor_license_number
    x images
    x lab_results_url
    ✓ producer
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ lab_id
    ✓ project_id
    ✓ product_type
    ✓ batch_number
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ date_collected
    ✓ date_received
    ✓ sample_size
    ✓ serving_size
    ✓ servings_per_package
    ✓ sample_weight
    - results
    ✓ status
    - total_cannabinoids (calculated)
    - total_thc
    - total_cbd
    - total_terpenes (calculated)
    ✓ sample_id (generated)
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_county (augmented)
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    ✓ lab_email
    ✓ lab_website
    ✓ lab_latitude (augmented)
    ✓ lab_longitude (augmented)

FIXME:

    This algorithm is under development!
    Please email dev@cannlytics.com if you want to help out.

    - [ ] Add `results`.

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
from cannlytics.data.data import create_sample_id, find_first_value
# from cannlytics.utils.constants import ANALYSES, ANALYTES
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)


# It is assumed that the lab has the following details.
VEDA_SCIENTIFIC = {
    'coa_algorithm': 'veda.py',
    'coa_algorithm_entry_point': 'parse_veda_coa',
    'url': 'vedascientific.co',
    'lims': 'Veda Scientific',
    'lab': 'Veda Scientific',
    'lab_image_url': 'https://images.squarespace-cdn.com/content/v1/5fab1470f012f739139935ac/58792970-f502-4e1a-ac29-ddca27b43266/Veda_Logo_Horizontal_RGB_Large.png?format=1500w', # <- Get this data.
    'lab_license_number': '', # <-- Get this static data point.
    'lab_address': '1601 W Central Ave Building A Unit A, Lompoc, CA',
    'lab_street': '1601 W Central Ave Building A Unit A',
    'lab_city': 'Lompoc',
    'lab_county': 'Santa Barbara',
    'lab_state': 'CA',
    'lab_zipcode': '93436',
    'lab_phone': '(805) 324-7728',
    'lab_email': 'info@vedascientific.co',
    'lab_website': 'vedascientific.co',
    'lab_latitude': 34.661520,
    'lab_longitude': -120.476520,
}

# It is assumed that there are the following analyses on each CoA.
VEDA_SCIENTIFIC_ANALYSES = {
    'cannabinoids': {
        'name': 'Cannabinoids',
        'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                    'mg_per_serving', 'mg_per_package'],
        'units': 'mg/g',
        # FIXME: It's better to have analytes dynamic.
        # 'analytes': [
        #     'cbd',
        #     'cbda',
        #     'cbdv',
        #     'cbdva',
        #     'cbg',
        #     'cbga',
        #     'cbl',
        #     'cbc',
        #     'cbca',
        #     'cbn',
        #     'cbna',
        #     'delta_9_thc',
        #     'thca',
        #     'delta_8_thc',
        #     'thcv',
        #     'thcva',
        # ],
    },
    'terpenes': {
        'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                    'mg_per_serving', 'mg_per_package'],
        'units': 'mg/g',
    },
    'moisture': {
        'columns': ['name', 'value'],
        'units': 'percent',
    },
    'water_activity': {
        'columns': ['name', 'value', 'limit', 'status'],
        'units': 'aW',
    },
    'pesticides': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
    },
    'mycotoxins': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/kg',
    },
    'heavy_metals': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
    },
    'foreign_matter': {
        'analytes': [
            'mold',
        ],
        'columns': ['name', 'limit', 'status'],
        'units': 'percent',
    },
    'microbials': {
        'columns': ['name', 'value', 'status'],
        'units': 'count',
    },
    'residual_solvents': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
    },
}

# It is assumed that the CoA has the following parameters.
VEDA_SCIENTIFIC_COA = {
    'coa_qr_code_index': None,
    'coa_image_index': 0,
    'coa_page_area': [0, 0.095, 1, 0.85],
    'coa_distributor_area': [0, 0.1, 0.5, 0.215],
    'coa_producer_area': [0.5, 0.1, 1, 0.215],
    'coa_sample_details_area': [0, 0.215, 1, 0.375],
    'coa_analyses': {
        'CANNABINOID': 'cannabinoids',
        'TERPENES': 'terpenes',
        'MOISTURE': 'moisture',
        'WATER ACTIVITY': 'water_activity',
        'PESTICIDES': 'pesticides',
        'MYCOTOXIN': 'mycotoxins',
        'FOREIGN MATERIALS': 'foreign_matter',
        'RESIDUAL SOLVENTS': 'residual_solvents',
        'HEAVY METALS': 'heavy_metals',
        'MICROBIAL IMPURITIES': 'microbes',
    },
    'coa_fields': {
        'Sample Name': 'product_name',
        'Collected': 'date_collected',
        'Lab ID': 'lab_id',
        'ReceiveEd': 'date_received',
        'Order Number': 'order_number',
        'Client Batch Size': 'batch_size',
        'Matrix Type': 'product_type',
        'Sample Size': 'sample_size',
        'Client Batch #': 'batch_number',
        'Serving Size': 'serving_size',
        'Lab Metrc Id': 'metrc_lab_id',
        'Servings': 'servings_per_package',
        'Client Metrc Id': 'metrc_source_id',
        'Density': 'sample_weight',
    },
    'coa_skip_values': [],
    'coa_replacements': [
        {'text': ' Per package', 'key': ''},
        {'text': 'Potency', 'key': 'Cannabinoids'},
        {'text': 'Foreign Materials', 'key': 'Foreign Matter'},
    ],
}


def get_page_rows(
        pdf_file: Any,
        index: list,
        analytes: dict,
    ) -> list:
    """Get the rows a given page.
    Split long rows at the first analyte!
    Args:

    Returns:
    """
    analyte_keys = list(set(analytes.keys()))
    analyte_values = list(set(analytes.values()))
    page_rows, texts = [], []
    for i in index:
        page = pdf_file.pages[i]
        text = page.extract_text()
        text = text \
            .replace('\xa0\xa0', '\n') \
            .replace('\xa0', ',') \
            .split('\n')
        texts.append(text)
    
    # TODO: Split into separate function?
    for text in texts:
        for row in text:
            parts = row.split(' ')
            initial_value = parts[0]
            analyte_key =  snake_case(strip_whitespace(initial_value))
            if initial_value in analyte_values:
                analyte_key = analytes[analyte_key]
            if analyte_key in analyte_keys:
                second_index = None
                for i, part in enumerate(parts[1:]):
                    second_key = snake_case(strip_whitespace(part))
                    if second_key in analyte_keys:
                        second_index = i + 1
                        break
                if second_index is None:
                    page_rows.append(parts)
                else:
                    double_rows = split_list(parts, second_index)
                    page_rows.append(double_rows[0])
                    page_rows.append(double_rows[1])
            else:
                page_rows.append(parts)
    return page_rows


def parse_veda_coa(parser, doc: Any, **kwargs) -> dict:
    """Parse a Veda Scientific CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]
    front_page = report.pages[0]
    w, h = front_page.width, front_page.height

    # Get the lab-specific CoA page areas.
    coa_parameters = VEDA_SCIENTIFIC_COA

    # If needed: Get lab CoA specific fields.
    coa_fields = coa_parameters['coa_fields']
    coa_replacements = coa_parameters['coa_replacements']
    sample_details_fields = list(coa_fields.keys())
    standard_analyses = coa_parameters['coa_analyses']
    # skip_values = coa_parameters['coa_skip_values']

    # Optional: Get the image data.
    # image_index = coa_parameters['coa_image_index']
    # obs['image_data'] = self.get_pdf_image_data(report.pages[0], image_index)
    obs['images'] = []

    # Get all distributor details.
    x0, y0, x1, y1 = tuple(coa_parameters['coa_distributor_area'])
    distributor_area = (x0 * w, y0 * h, x1 * w, y1 * h)
    crop = front_page.within_bbox(distributor_area)
    text = crop.extract_text()
    block = text.split('\n')
    distributor = text \
        .split('License Number')[0] \
        .split('Business Name')[-1] \
        .replace('\n', ' ').strip()
    license_number = text \
        .split('License Number')[-1] \
        .split('Address')[0].strip()
    street = block[-2]
    locales = block[-1].split(',')
    city = locales[0]
    subparts = locales[-1].strip().split(' ')
    state, zipcode = subparts[-2], subparts[-1]
    address = ', '.join([street, block[-1]])
    obs['distributor'] = distributor
    obs['distributor_address'] = address
    obs['distributor_street'] = street
    obs['distributor_city'] = city
    obs['distributor_state'] = state
    obs['distributor_zipcode'] = zipcode
    obs['distributor_license_number'] = license_number

    # Get all producer details.
    x0, y0, x1, y1 = tuple(coa_parameters['coa_producer_area'])
    producer_area = (x0 * w, y0 * h, x1 * w, y1 * h)
    crop = front_page.within_bbox(producer_area)
    text = crop.extract_text()
    block = text.split('\n')
    producer = text \
        .split('License Number')[0] \
        .split('Business Name')[-1] \
        .replace('\n', ' ').strip()
    license_number = text \
        .split('License Number')[-1] \
        .split('Address')[0].strip()
    street = block[-2]
    locales = block[-1].split(',')
    city = locales[0]
    subparts = locales[-1].strip().split(' ')
    state, zipcode = subparts[-2], subparts[-1]
    address = ', '.join([street, block[-1]])
    obs['producer'] = producer
    obs['producer_address'] = address
    obs['producer_street'] = street
    obs['producer_city'] = city
    obs['producer_state'] = state
    obs['producer_zipcode'] = zipcode
    obs['producer_license_number'] = license_number

    # Get the sample details.
    x0, y0, x1, y1 = tuple(coa_parameters['coa_sample_details_area'])
    sample_details_area = (x0 * w, y0 * h, x1 * w, y1 * h)
    crop = front_page.within_bbox(sample_details_area)
    text = crop.extract_text()
    for r in coa_replacements:
        text = text.replace(r['text'], r['key'])
    details = re.split('\n|' + '|'.join(sample_details_fields), text)
    index = 0
    for i, detail in enumerate(details[1:]):
        if detail:
            field = sample_details_fields[index]
            key = coa_fields[field]
            obs[key] = detail.lstrip(':').strip()
            index += 1 

    # Get the front page tables.
    tables = front_page.extract_tables()

    # Get the overall status.
    table_data = tables[0][0][0]
    analysis_details = table_data.replace('\xa0\xa0\xa0\xa0', '\n').split('\n')
    mm, dd, yyyy = analysis_details[2].split(':')[-1].strip().split('/')
    date_tested = f'{yyyy}-{mm}-{dd}'
    obs['date_tested'] = date_tested
    obs['analysis_type'] = analysis_details[0]
    obs['status'] = analysis_details[-1].split(':')[-1].strip().lower()

    # Get the statuses from the front page.
    analyses = []
    x0, y0, x1, y1 = tuple(coa_parameters['coa_page_area'])
    page_area = (x0 * w, y0 * h, x1 * w, y1 * h)
    crop = front_page.within_bbox(page_area)
    text = crop.extract_text()
    summary = text.split('Sample Certification')[0]
    summary = summary.split('SAFETY SUMMARY')[-1]
    summary = summary.replace('\xa0', '\n').split('\n')
    for row in summary:
        if row:
            parts = row.strip().split(' ')
            analysis_name = ' '.join(parts[:len(parts) - 1])
            for r in coa_replacements:
                analysis_name = analysis_name.replace(r['text'], r['key'])
            analysis = snake_case(analysis_name)
            status = parts[-1].strip().lower()
            obs[f'{analysis}_method'] = status
            # Future work: Ensure this excludes not tested analyses.
            # Will need to see an example CoA with not tested analyses.
            if status != 'not tested':
                analyses.append(analysis)
    
    # TODO: Get cannabinoid totals.
    # block = text.split('\n')
    # # - total_thc
    # # - total_cbd
    # # - total_cannabinoids

    # Get the lab license number.
    table_data = tables[-1][-1][0]
    lab_details = table_data.replace('\xa0', '\n').split('\n')
    lab_details = [x.strip() for x in lab_details if x.replace('|', '').strip() != '' ]
    for detail in lab_details:
        if 'license' in detail.lower():
            obs['lab_license_number'] = detail.split(':')[-1].strip()

    # Get all of the `results` rows.
    all_lines = []
    for page in report.pages[1:]:
        crop = page.within_bbox(page_area)
        rows = parser.get_page_rows(crop)
        for row in rows:
            if row in all_lines:
                pass
            else:
                all_lines.append(row)

    # Brute-force: The following probably needs to be refactored.
    analysis_keys = list(standard_analyses.keys())

    # Get all of the `results`!
    current_analysis = []
    collected_analytes = []
    results = []
    for line in all_lines:

        # Skip nuisance lines.
        if len(line) == 1 or ':' in line:
            continue

        # Get the analysis of the table, handling two columns.
        elif 'RESULTS' in line:
            current_analysis = []
            for key in analysis_keys:
                if key in line:
                    current_analysis.append(standard_analyses[key])
        
        # Get the analysis methods.
        elif 'Method:' in line:
            parts = line.split('Method:')
            methods = [
                x.split(' ,')[0].split('Procedures:')[0].strip() for x in parts if x
            ]
            for i, analysis in enumerate(current_analysis):
                try:
                    obs[f'{analysis}_method'] = methods[i]
                except IndexError:
                    pass

        # Optional: Identify the columns?

        # FIXME: Collect each individual result.
        else:

            # Add keys / values to the result, using standard fields.
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            analyte = snake_case(name)
            analyte = parser.fields.get(analyte, analyte)
            values = line[first_value:].strip().split(' ')
            values = [x for x in values if x]

            # Create a result object.
            result = {
                # 'analysis': analysis, # FIXME: Add `analysis.`
                'key': analyte,
                'name': name,
                # 'units': units, # FIXME: Add `units.
            }

            # TODO: Get the columns.
            
            # Match the values to the columns.
            # try:
            #     for i, v in enumerate(values):
            #         # FIXME: Get the correct column field here.
            #         key = parser.fields[i + 1]
            #         value = convert_to_numeric(v)
            #         result[key] = value
            # except IndexError:
            #     continue

            # Record the result.
            results.append(result)

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Return the sample with a freshly minted sample ID.
    obs['analyses'] = list(set(analyses))
    obs['date_tested'] = date_tested
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=producer,
    )
    return {**VEDA_SCIENTIFIC, **obs}


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # Specify where your test CoA lives.
    DATA_DIR = '../../../tests/assets/coas'
    doc = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'

    # [✓] TEST: Detect the lab / LIMS that generated the CoA.
    parser = CoADoc()
    known_lims = parser.identify_lims(doc)
    assert known_lims == 'Veda Scientific'

    # [ ] TEST: Parse the CoA.
    parser = CoADoc()
    data = parse_veda_coa(parser, doc)
    assert data is not None
