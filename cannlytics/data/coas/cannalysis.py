"""
Parse Cannalysis CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Cannalysis CoA PDF.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ {analysis}_status
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    ✓ date_produced
    ✓ batch_size
    ✓ lab_id
    ✓ lab_results_url
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ sample_id
    ✓ sample_size
    ✓ total_cannabinoids
    ✓ total_cbd
    ✓ total_thc
    ✓ total_terpenes

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
from cannlytics.utils.constants import ANALYSES, ANALYTES, STANDARD_FIELDS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
)

# It is assumed that the lab has the following details.
CANNALYSIS =  {
    'coa_algorithm': 'cannalysis.py',
    'coa_algorithm_entry_point': 'parse_cannalysis_coa',
    'url': 'www.cannalysis.com',
    'lims': 'Cannalysis',
    'lab': 'Cannalysis',
    'lab_license_number': 'C8-0000012-LIC',
    'lab_image_url': 'https://www.cannalysis.com/img/img.c5effdd3.png',
    'lab_address': '1801 Carnegie Ave, Santa Ana CA 92705',
    'lab_street': '1801 Carnegie Ave',
    'lab_city': 'Santa Ana',
    'lab_county': 'Orange',
    'lab_state': 'CA',
    'lab_zipcode': '92705',
    'lab_latitude': 33.712190,
    'lab_longitude': -117.844650,
    'lab_phone': '949-329-8378',
    'lab_email': 'support@cannalysislabs.com',
    'lab_website': 'www.cannalysis.com',
}

# It is assumed that the CoA has the following parameters.
CANNALYSIS_COA = {
    'coa_page_area': [
        '(0, 80, 305, 720)',
        '(305, 80, 612, 720)',
    ],
    'coa_sample_details_area': [
        '(220, 135, 612, 700)',
        '(0, 135, 220, 700)',
    ],
    'coa_result_fields': [
        'name',
        'value',
        'lod',
        'loq', 
        'limit',
        'status',
    ],
    'coa_skip_fields': [
        'ADDITIONAL',
        'Total',
        'undergone a calculation',
        'Individual Analyte',
        '   ',
        'AS',
    ],
}


def parse_cannalysis_coa(parser, doc: Any, **kwargs) -> Any:
    """Parse a Cannalysis CoA PDF.
    Args:
        parser (CoADoc): A CoADoc parsing client.
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """

    # Read the PDF.
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
    else:
        report = doc

    # Get the QR code from the last page.
    obs = {}
    obs['lab_results_url'] = parser.find_pdf_qr_code_url(report)

    # Get the lab specifics.
    coa_parameters = CANNALYSIS_COA
    standard_result_fields = coa_parameters['coa_result_fields']
    skip_fields = coa_parameters['coa_skip_fields']

    # Optional: Get the image data.

    # Define results to collect.
    analyses = []
    results = []

    # Get the sample details.
    front_page = report.pages[0]
    sample_details_area = coa_parameters['coa_sample_details_area']
    if isinstance(sample_details_area, str):
        sample_details_area = [sample_details_area]
    for area in sample_details_area:
        crop = front_page.within_bbox(literal_eval(area))
        lines = crop.extract_text().split('\n')
        analysis = None
        collect = False
        field = None
        for line in lines:

            # Determine any fields.
            potential_field = STANDARD_FIELDS.get(snake_case(line))
            if potential_field:
                field = potential_field
                collect = True
                continue
            if collect and field:
                if field == 'date_collected':
                    dates = tuple(line.split(', '))
                    obs['date_collected'] = dates[0]
                    obs['date_received'] = dates[1]
                elif field == 'batch_size':
                    dates = tuple(line.split(', '))
                    obs['batch_size'] = dates[0]
                    obs['sample_size'] = dates[1]
                else:
                    obs[field] = line
                collect = False
                field = None
            
            # Collect the data.
            elif collect and analysis:
                obs[f'{analysis}_status'] = line.lower()
                collect = False
                analysis = None

            # Determine any analyses.
            potential_analysis = ANALYSES.get(line)
            if potential_analysis:
                analysis = potential_analysis
                analyses.append(potential_analysis)
                collect = True
                continue

    # Get all page text, from the 2nd page on.
    areas = coa_parameters['coa_page_area']
    lines = []
    for page in report.pages[1:]:
        for area in areas:
            crop = page.within_bbox(literal_eval(area))
            lines += crop.extract_text().split('\n')

    # Identify important lines and extract results.
    analysis = None
    dates = []
    for line in lines:

        # Identify the analysis.
        # Note: Hot-Fix for foreign matter.
        if 'ANALYSIS' in line or 'FILTH' in line:
            analysis = line.split(' ANA')[0].title()
            analysis = ANALYSES.get(analysis)

        # Identify the columns (unnecessary).
        elif 'ANALYTE' in line:
            continue
            # parts = [snake_case(x) for x in line.split(' ')]
            # columns = [standard_fields.get(x, x) for x in parts]

        # Identify the units (under development).
        elif 'UNIT OF MEASUREMENT' in line:
            continue
            # units = line.split(':')[-1].strip()
            # units = line[line.find('(') + 1: line.find(')')]
        
        # Identify the instrument as the `method`.
        elif 'Instrument:' in line:
            method = line.split('Instrument: ')[-1].split(' Sample Analyzed:')[0]
            obs[f'{analysis}_method'] = method
        elif 'Method:' in line:
            continue

        # Get the totals.
        elif 'TOTAL' in line:
            parts = line.split(':')
            key = snake_case(parts[0].lower())
            value = parts[1]
            if '(' in value:
                value = value[value.find('(') + 1: value.find(')')]
                value = convert_to_numeric(value, strip=True)
            obs[key] = value

        # Get the dates tested.
        elif 'Sample Approved:' in line:
            date = pd.to_datetime(line.split('Sample Approved:')[-1].strip())
            dates.append(date)

        # Skip informational rows.
        elif any(s in line for s in skip_fields):
            continue

        # End at the end of the report.
        elif line.startswith('Thisreport'):
            break

        # Get the results.
        else:

            # Remove extraneous results.
            text = line.replace('mg/g', '').replace(' aw ', ' ')
            text = re.sub('[\(\[].*?[\)\]]', '', text)
            
            # Split at the first 'ND', '<', or number, preceded by a space.
            first_digit, first_nd, first_lt = None, None, None
            try:
                first_digit = text.index(re.search(' \d+', text).group())
            except AttributeError:
                pass
            try:
                first_nd = text.index(re.search('ND', text).group())
            except AttributeError:
                pass
            try:
                first_lt = text.index(re.search('<', text).group())
            except AttributeError:
                pass
            split_at = min([x for x in [first_digit, first_nd, first_lt] if x])

            # Standardize analytes.
            name = text[:split_at].strip()
            analyte = ANALYTES.get(name, snake_case(name))

            # Record the result value by using standard columns.
            result = {
                'analysis': None, # FIXME: <-- Add this data point!
                'key': analyte,
                'name': name,
                'units': None, # FIXME: <-- Add this data point!
            }
            values = text[split_at:].strip().split(' ')
            values = [x for x in values if x]
            for i, value in enumerate(values):
                key = standard_result_fields[i + 1]
                result[key] = convert_to_numeric(value)
            results.append(result)

    # Get the latest tested at date.
    obs['date_tested'] = max(dates)

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Hot-fix: Add 'Anonymous' producer for standardization.
    # Optional: Is there any way to identify the `producer`?
    obs['producer'] = 'Anonymous'

    # Finish data collection with a freshly minted sample ID.
    obs['analyses'] = list(set(analyses))
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=obs['producer'],
        public_key=obs['product_name'],
        salt=obs['date_tested'],
    )
    return {**CANNALYSIS, **obs}


# === Test ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # [✓] TEST: Parse a Cannalysis CoA PDF.
    parser = CoADoc()
    doc = '../../../.datasets/coas/Flore COA/Kiva/MothersMilk.pdf'
    lab = parser.identify_lims(doc, lims={'Cannalysis': CANNALYSIS})
    assert lab == 'Cannalysis'
    data = parse_cannalysis_coa(parser, doc)
    assert data is not None
