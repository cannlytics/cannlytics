"""
Parse Green Leaf Lab CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/23/2022
Updated: 9/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Green Leaf Labs CoA PDF.

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
    ✓ batch_size
    x coa_urls
    ✓ date_harvested
    ✓ date_tested
    ✓ date_received
    ✓ date_sampled
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ distributor_license_number
    x images
    ✓ image_data
    x lab_results_url
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ producer
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ sample_weight
    ✓ sample_size
    ✓ sampling_method
    ✓ status
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_terpenes
    ✓ sample_id (generated)
    - strain_name (augmented)
    ✓ lab_id
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number (should be dynamic)
    ✓ lab_address (should be dynamic)
    ✓ lab_street (should be dynamic)
    ✓ lab_city (should be dynamic)
    ✓ lab_county (augmented)
    ✓ lab_state (should be dynamic)
    ✓ lab_zipcode (should be dynamic)
    ✓ lab_phone (should be dynamic)
    - lab_email
    ✓ lab_website
    ✓ lab_latitude (augmented) (should be dynamic)
    ✓ lab_longitude (augmented) (should be dynamic)

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
import json
import re
from typing import Any

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
# Future work: Make this dynamic to handle multiple lab locations.
# E.g. Green Leaf Lab has a California and an Oregon location.
GREEN_LEAF_LAB = {
    'coa_algorithm': 'greenleaflab.py',
    'coa_algorithm_entry_point': 'parse_green_leaf_lab_pdf',
    'lims': 'Green Leaf Lab',
    'lab': 'Green Leaf Lab',
    'lab_image_url': 'https://cdn-djjmk.nitrocdn.com/MuWSCTBsUZpIUufaWqGQkErSrYFMxIqD/assets/static/optimized/rev-a199899/wp-content/uploads/2018/12/greenleaf-logo.png',
    'lab_license_number': ' C8-0000078-LIC', # <- Make dynamic.
    'lab_address': '251 Lathrop Way Suites D&E Sacramento, CA 95815', # <- Make dynamic.
    'lab_street': '251 Lathrop Way Suites D&E', # <- Make dynamic.
    'lab_city': 'Sacramento', # <- Make dynamic.
    'lab_county': 'Sacramento', # <- Make dynamic.
    'lab_state': 'CA', # <- Make dynamic.
    'lab_zipcode': '95815', # <- Make dynamic.
    'lab_phone': '916-924-5227', # <- Make dynamic.
    'lab_email': '', # <- Make dynamic.
    'lab_website': 'https://greenleaflab.org/',
    'lab_latitude': 38.596060, # <- Make dynamic.
    'lab_longitude': -121.459870, # <- Make dynamic.
}

# It is assumed that there are the following analyses on each CoA.
GREEN_LEAF_LAB_ANALYSES = {
    'cannabinoids': {
        'name': 'Potency Analysis by HPLC',
        'columns': ['name', 'lod', 'loq', 'value', 'mg_g'],
    },
    'pesticides': {
        'name': 'Pesticide Analysis by GCMS/LCMS',
        'columns': ['name', 'value', 'limit', 'lod', 'loq', 'units'],
        'double_column': True,
    },
    'water_activity': {
        'name': 'Water Activity by Aqua Lab',
        'columns': ['name', 'value', 'units', 'lod', 'loq'],
    },
    'moisture_content': {
        'name': 'Moisture by Moisture Balance',
        'columns': ['name', 'value', 'units'],
    },
    'terpenes': {
        'name': 'Terpene Analysis by GCMS',
        'columns': ['name', 'value', 'mg_g'],
        'double_column': True,
    },
    'heavy_metals': {
        'name': 'Metals Analysis by ICPMS',
        'columns': ['name', 'value', 'limit', 'lod', 'loq', 'units'],
    },
    'mycotoxins': {
        'name': 'Mycotoxins by LCMSMS',
        'columns': ['name', 'value', 'limit', 'loq', 'loq', 'units'],
    },
    'microbials': {
        'name': 'Microbials by PCR',
        'columns': ['name', 'status', 'limit', 'lod', 'loq', 'units', 'value'],
    },
    'foreign_matter': {
        'name': 'Filth and Foreign Material Inspection by Magnification',
        'columns': ['name', 'status', 'limit', 'lod', 'loq', 'units'],
    },
}

# It is assumed that the CoA has the following parameters.
GREEN_LEAF_LAB_COA = {
    'coa_qr_code_index': None,
    'coa_page_area': '(0, 198, 612, 693)',
    'coa_distributor_area': '(0, 79.2, 244.8, 142.56)',
    'coa_producer_area': '(244.8, 79.2, 612, 142.56)',
    'coa_sample_details_area': '(0, 126.72, 612, 205.92)',
    'coa_sample_detail_fields': [
        'Test RFID',
        'Source RFID',
        'Lab Sample ID',
        'Sampling Method/SOP',
        'Source Batch ID',
        'Matrix',
        'Batch Size',
        'Sample Size',
        'Date Sampled',
        'Date Received',
        'Harvest/Processing Date',
        'Product Density',
    ],
    'coa_skip_values': [
        'Date/Time',
        'Analysis Method',
        'Analyte',
        'ND - Compound not detected',
        '<LOQ - Results below the Limit of Quantitation',
        'Results above the Action Level',
        'Sesquiterpenes',
        'Monoterpenes',
    ],
    # TODO: Make this field obsolete.
    'coa_replacements': [
        {'text': '< LOQ', 'key': '<LOQ'},
        {'text': '< LOD', 'key': '<LOD'},
        {'text': 'No detection in 1 gram', 'key': 'ND'},
        {'text': 'Ocimene isomer II', 'key': 'beta-ocimene'},
        {'text': 'Ocimene isomer I', 'key': 'alpha-ocimene'},
        {'text': 'p-Mentha-1,5-diene', 'key': 'p-Mentha-1-5-diene'},
        {'text': 'Methyl parathion', 'key': 'Methyl-parathion'},
        {'text': 'Caryophyllene Oxide', 'key': 'beta_caryophyllene_oxide'},
    ],
}


def augment_analyte_result(
        analytes: dict,
        result: dict,
        columns: list,
        parts: list,
    ) -> dict:
    """Quickly augment / add keys and values to an analyte result.
    Args:
        analytes (dict): A map of analytes to standard analytes.
        result (dict): A dictionary of results.
        columns (list): A list of keys to add to the result.
        parts (list): A list of values to add to the result.
    Returns:
        (dict): The updated result.
    """
    r = result.copy()
    if len(parts) > len(columns):
        break_point = len(parts) - len(columns) + 1
        name = ' '.join(parts[:break_point])
        analyte = snake_case(name)
        analyte = analytes.get(analyte, analyte)
        r['name'] = name
        r['key'] = analyte
        for i, part in enumerate(parts[break_point:]):
            r[columns[i + 1]] = convert_to_numeric(part)
    else:
        for i, part in enumerate(parts):
            if i == 0:
                analyte = snake_case(part)
                analyte = analytes.get(analyte, analyte)
                r['name'] = part
                r['key'] = analyte
            else:
                r[columns[i]] = convert_to_numeric(part)
    return r


def parse_green_leaf_lab_pdf(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Green Leaf Lab CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Get the lab / LIMS analyses and CoA parameters.
    obs = {}
    lab_analyses = GREEN_LEAF_LAB_ANALYSES
    coa_parameters = GREEN_LEAF_LAB_COA

    # Get the lab's analyses.
    standard_analyses = list(lab_analyses.keys())
    analysis_names = [x['name'] for x in lab_analyses.values()]

    # Read the PDF.
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]
    front_page = report.pages[0]

    # Get the lab-specific CoA page areas.
    page_area = literal_eval(coa_parameters['coa_page_area'])
    distributor_area = literal_eval(coa_parameters['coa_distributor_area'])
    producer_area = literal_eval(coa_parameters['coa_producer_area'])
    sample_details_area = literal_eval(coa_parameters['coa_sample_details_area'])

    # Get lab CoA specific fields.
    # coa_fields = coa_parameters['coa_fields']
    coa_replacements = coa_parameters['coa_replacements']
    sample_details_fields = coa_parameters['coa_sample_detail_fields']
    skip_values = coa_parameters['coa_skip_values']

    # Get all distributor details.
    # Note: This could / should be more general.
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
    
    # Get all producer details.
    # Note: This could / should be more general.
    crop = front_page.within_bbox(producer_area)
    details = crop.extract_text().split('\n')
    producer = details[1]
    street = details[2]
    parts = details[3].split(',')
    city = parts[0]
    state, zipcode = tuple(parts[-1].strip().split(' ')[-2:])
    address = ','.join([street, details[3]])
    obs['producer'] = producer
    obs['producer_address'] = address
    obs['producer_street'] = street
    obs['producer_city'] = city
    obs['producer_state'] = state
    obs['producer_zipcode'] = zipcode
    obs['producer_license_number'] = details[-1]

    # Optional: Get the image data.
    # image_index = coa_parameters['coa_image_index']
    # obs['image_data'] = parser.get_pdf_image_data(report.pages[0], image_index)
    obs['images'] = []

    # Get the sample details.
    crop = front_page.within_bbox(sample_details_area)
    details = crop.extract_text()
    details = re.split('\n|' + '|'.join(sample_details_fields), details)
    product_name = details[0]
    index = 0
    for i, detail in enumerate(details[1:]):
        if detail:
            field = sample_details_fields[index]
            key = parser.fields[field]
            obs[key] = detail.replace(':', '').strip()
            index += 1  

    # Get the `analyses` and `{analysis}_status`.
    analyses = []
    table = report.pages[0].extract_table()
    for rows in table:
        for row in rows:
            cells = row.split('\n')
            for cell in cells:
                parts = cell.split(':')
                key = snake_case(parts[0])
                try:
                    value = strip_whitespace(parts[1])
                except IndexError:
                    continue
                field = parser.fields.get(key, key)
                obs[field] = value.lower()
                if field != 'status':
                    analysis = field.replace('_status', '')
                    analyses.append(analysis)

    # Identify `{analysis}_method`s.
    # Also find the times for all of the tests and find when all
    # tests were completed. Future work: record finish time of analyses.
    methods = []
    tested_at = []
    for page in report.pages[1:]:
        text = page.extract_text()
        parts = text.split('Analysis Method/SOP')
        for part in parts[1:]:
            method = part.split('\n')[0].replace(':', '').strip()
            method = method.split('Date/Time')[0] # <-- Hot-fix.
            methods.append(method)
        try:
            parts = text.split('Analyzed:')
            date = parts[1].split('\n')[0].strip()
            tested_at.append(pd.to_datetime(date))
        except:
            pass
    date_tested = max(tested_at).isoformat()

    # Get all of the `results` rows.
    all_rows = []
    for page in report.pages[1:]:
        crop = page.within_bbox(page_area)
        rows = parser.get_page_rows(crop)
        for row in rows:
            if row in all_rows:
                pass
            else:
                all_rows.append(row)

    # Iterate over all rows to get the `results` rows
    # seeing if row starts with an analysis or analyte.
    results = []
    current_analysis = None
    for row in all_rows:

        # Identify the analysis.
        analysis = current_analysis
        for i, name in enumerate(analysis_names):
            if name in row:
                analysis = standard_analyses[i]
                break
        if analysis != current_analysis:
            current_analysis = analysis
            continue

        # Skip detail rows.
        detail_row = False
        for skip_value in skip_values:
            if row.startswith(skip_value):
                detail_row = True
                break
        if detail_row:
            continue

        # Get the analysis details.
        analysis_details = lab_analyses[current_analysis]
        columns = analysis_details['columns']
        double_column = analysis_details.get('double_column')

        # Get the result!
        values = row
        for replacement in coa_replacements:
            values = values.replace(replacement['text'], replacement['key'])
        values = values.split(' ')
        values = [x for x in values if x]
        units = STANDARD_UNITS.get(analysis)
        result = {'analysis': analysis, 'units': units}

        # Skip the analysis title row and short detail rows.
        # Note: There is probably a better way to do this that can not
        # accidentally exclude results. This method may not be perfect.
        if snake_case(values[0]) == current_analysis or len(values) < len(columns):
            continue

        # Hot-fix for `total_terpenes`.
        # Note: There may be a better way to do this.
        if values[0] == 'Total' and values[1] == 'Terpenes':
            values = ['Total Terpenes'] + values[2:]

        # Hot-fix for `mycotoxins`.
        # Note: There may be a better way to do this.
        if values[0] == 'aflatoxin':
            values.insert(2, 20)

        # Split the row if double_column.
        # Note: This code could probably be refactored.
        if double_column and len(values) > len(columns):
            multi_part = split_list(values, int(len(values) / 2))

            # Parse the first column.
            entry = augment_analyte_result(
                parser.analytes,
                result,
                columns,
                multi_part[0],
            )
            if entry['name'] != 'mgtog' and entry['name'] != 'action':
                results.append(entry)

            # Parse the second column.
            entry = augment_analyte_result(
                parser.analytes,
                result,
                columns,
                multi_part[1],
            )
            if entry['name'] != 'mgtog' and entry['name'] != 'action':
                results.append(entry)
        
        # Parse a single column.
        else:
            entry = augment_analyte_result(
                parser.analytes,
                result,
                columns,
                values,
            )
            if entry['name'] != 'mgtog' and entry['name'] != 'action':
                results.append(entry)

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass
    
    # Finish data collection with a freshly minted sample ID.
    obs['analyses'] = analyses
    obs['date_tested'] = date_tested
    obs['methods'] = methods
    obs['product_name'] = product_name
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=product_name,
        salt=producer,
    )
    obs['coa_parsed_at'] = datetime.now().isoformat()

    # Optional: Lowercase `status` in each of the `results`.

    # Future work: Standardize the `product_type`.

    # Future work: Attempt to identify `strain_name` from `product_name`.

    return {**GREEN_LEAF_LAB, **obs}


if __name__ == '__main__':

    # Test parsing a Green Leaf Lab CoA
    from cannlytics.data.coas import CoADoc

    # Specify where your test CoA lives.
    DATA_DIR = '../../../tests/assets/coas'
    # coa_pdf = f'{DATA_DIR}/Raspberry Parfait.pdf' # Alternative.
    coa_pdf = f'{DATA_DIR}/Flore COA/Swami Select/MagicMelon.pdf'

    # [✓] TEST: Detect the lab / LIMS that generated the CoA.
    parser = CoADoc()
    lab = parser.identify_lims(coa_pdf)
    assert lab == 'Green Leaf Lab'

    # [✓] TEST: Parse a Green Leaf Lab CoA.
    parser = CoADoc()
    data = parse_green_leaf_lab_pdf(parser, coa_pdf)
    assert data is not None
