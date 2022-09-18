"""
Parse Sonoma Lab Works CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/2/2022
Updated: 9/7/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Sonoma Lab Works CoA PDFs.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ {analysis}_status
    ✓ batch_number
    ✓ batch_size
    ✓ date_collected
    ✓ date_tested
    ✓ date_received
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_county
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ distributor_latitude
    ✓ distributor_longitude
    - images
    x lab_results_url
    ✓ metrc_source_id
    ✓ producer
    ✓ producer_address
    ✓ producer_license_number
    ✓ producer_street
    ✓ producer_city
    ✓ producer_county
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_latitude
    ✓ producer_longitude
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ sample_weight
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_terpenes
    ✓ sample_id (generated)
    - strain_name
    ✓ lab_id
    ✓ lab
    ✓ lab_email
    ✓ lab_phone
    ✓ lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    ✓ lab_city
    ✓ lab_county (augmented)
    ✓ lab_state (augmented)
    ✓ lab_zipcode (augmented)
    ✓ lab_latitude (augmented)
    ✓ lab_longitude (augmented)

"""
# Standard imports.
from datetime import datetime
import json
from typing import Any, Optional

# External imports.
from dotenv import dotenv_values
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.data.gis import search_for_address
from cannlytics.utils.constants import (
    ANALYSES,
    ANALYTES,
    STANDARD_FIELDS,
)
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
    'lab_license_number': 'C8-0000015-LIC',
    'lab_image_url': 'https://images.squarespace-cdn.com/content/v1/6072f29fa4b8d3121b2f9fbc/1623325374642-KXUXXMCSCVBYPYMFPTUS/slw-logo.png?format=1500w',
    'lab_address': '1201 Corporate Center Parkway, Santa Rosa, CA 95407',
    'lab_street': '1201 Corporate Center Parkway',
    'lab_city': 'Santa Rosa',
    'lab_county': 'Sonoma',
    'lab_state': 'CA',
    'lab_zipcode': '95407',
    'lab_latitude': 38.421600,
    'lab_longitude': -122.752990,
    'lab_phone': '707-757-7757',
    'lab_email': 'testing@sonomalabworks.com',
    'lab_website': 'https://www.sonomalabworks.com/',
}


def parse_sonoma_coa(
        parser,
        doc: Any,
        google_maps_api_key: Optional[str] = None,
        **kwargs,
    ) -> Any:
    """Parse a Sonoma Lab Works CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.split('/')[-1]

    # Define fields to collect.
    analysis = None
    analyses = []
    columns = []
    results = []
    units = None

    # Get all of the tables.
    tables = []
    for page in report.pages:
        tables.extend(page.extract_tables())

    # Get the details from the front page.
    tables = report.pages[0].extract_tables()
    for table in tables:
        for row in table:
            initial_value = row[0]

            # Skip blank rows.
            if not initial_value:
                continue

            # Get standard fields.
            if ':' in initial_value:
                if len(row) == 2:
                    key = snake_case(initial_value)
                    key = STANDARD_FIELDS.get(key, key)
                    value = row[1]
                    obs[key] = value
                elif len(row) == 4:
                    key = snake_case(initial_value)
                    key = STANDARD_FIELDS.get(key, key)
                    value = row[1]
                    second_key = snake_case(row[2])
                    second_key = STANDARD_FIELDS.get(second_key, second_key)
                    second_value = row[3]
                    obs[key] = value
                    obs[second_key] = second_value

            # Get totals.
            elif 'Total' in initial_value:
                key = STANDARD_FIELDS.get(initial_value, snake_case(initial_value))
                obs[key] = convert_to_numeric(row[1])

            # Get analysis statuses and minor analysis results.
            elif 'Pass' in str(row[-1]) or 'Fail' in str(row[-1]):
                name = initial_value.split('(')[0].strip()
                analysis = ANALYSES.get(name, snake_case(name))
                status = row[-1].lower()
                obs[f'{analysis}_status'] = status

                # Hot-fix: Also collect minor analyses.
                special_analyses = {
                    'moisture_content': {'analysis': 'moisture_content', 'units': 'percent', 'limit': 15},
                    'water_activity': {'analysis': 'water_activity', 'units': 'percent', 'limit': 0.65},
                    'foreign_matter': {'analysis': 'foreign_matter', 'units': 'percent', 'limit': None},
                }
                if analysis in special_analyses.keys():
                    special_analysis = special_analyses[analysis]
                    results.append({
                        'key': special_analysis['analysis'],
                        'name': name,
                        'value': convert_to_numeric(row[1]),
                        'units': special_analysis['units'],
                        'limit': special_analysis.get('limit'),
                        'status': status,
                    })

    # Get the analyses and results.
    tables = report.pages[1].extract_tables()
    for table in tables:
        for row in table:

            # Skip the detail rows.
            if len(row) == 2 or not row[0]:
                continue

            # Find the analysis.
            elif '\n' in row[0]:
                parts = row[0].split('\n')
                analysis = ANALYSES.get(parts[0], snake_case(parts[0]))
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
                        result['key'] = ANALYTES.get(analyte, analyte)
                    key = STANDARD_FIELDS.get(column, snake_case(column))
                    if key in recorded_keys:
                        continue
                    try:
                        result[key] = convert_to_numeric(values[i])
                    except IndexError:
                        result[key] = None
                    recorded_keys.append(key)
                results.append(result)

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

    # Try to get the producer's address.
    try:
        location = search_for_address(obs['producer_address'], api_key=google_maps_api_key)
        for key, value in location.items():
            obs[f'producer_{key}'] = value
    except:
        pass

    # Try to get the distributor's address.
    try:
        location = search_for_address(obs['distributor_address'], api_key=google_maps_api_key)
        for key, value in location.items():
            obs[f'distributor_{key}'] = value
    except:
        pass

    # Future work: Standardize `product_type`.

    # Aggregate results.
    obs['analyses'] = list(set(analyses))
    obs['results'] = results

    # Finish data collection with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs['producer'],
    )
    obs['coa_parsed_at'] = datetime.now().isoformat()
    return {**SONOMA, **obs}


# === Test ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # Get Google Maps API Key.
    try:
        config = dotenv_values('../../../.env')
        google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    except:
        google_maps_api_key = None

    # [✓] TEST: Parse a Sonoma Lab Works CoA PDF.
    parser = CoADoc()
    doc = '../../../tests/assets/coas/LemonTree.pdf'
    lab = parser.identify_lims(doc)
    assert lab == 'Sonoma Lab Works'
    data = parse_sonoma_coa(parser, doc, google_maps_api_key=google_maps_api_key)
    assert data is not None
