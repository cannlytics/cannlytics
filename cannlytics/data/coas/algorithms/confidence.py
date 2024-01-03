"""
CoADoc | Parse Confidence Analytics COAs
Copyright (c) 2022 Cannlytics

Authors:
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/26/2022
Updated: 9/29/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Confidence Analytics COA PDFs.

Data Points (✓):

    ✓ analyses
    ✓ methods
    - {analysis}_status
    ✓ date_harvested
    ✓ date_received
    ✓ date_tested
    ✓ external_id
    ✓ lab_id
    ✓ lab_results_url
    ✓ producer
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ producer_latitude
    ✓ producer_longitude
    ✓ product_id
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ results_hash
    ✓ sample_hash
    ✓ total_cannabinoids (calculated)
    ✓ total_cbd (Calculated as cbd + 0.877 * cbda)
    ✓ total_thc (Calculated as delta_9_thc + 0.877 * thca)
    ✓ total_terpenes (calculated)

"""
# Standard imports:
from datetime import datetime
import json
import os
import re
from typing import Any, Optional, List

# External imports:
from datasets import load_dataset
import pandas as pd
import pdfplumber

# Internal imports:
from cannlytics import __version__
from cannlytics.data.data import create_hash, create_sample_id
from cannlytics.data.gis import search_for_address
from cannlytics.utils import (
    convert_to_numeric,
    download_file_from_url,
    snake_case,
)
from cannlytics.utils.constants import DECARB


# It is assumed that the lab has the following details.
CONFIDENCE = {
    'coa_algorithm': 'confidence.py',
    'coa_algorithm_entry_point': 'parse_confidence_coa',
    'lims': 'Confidence Analytics',
    'url': 'https://certs.conflabs.com',
    'lab': 'Confidence Analytics',
    'lab_website': 'https://conflabs.com',
    'lab_license_number': '7939083039',
    'lab_image_url': 'https://www.conflabs.com/wp-content/uploads/2022/06/CA_3_transparent_registered-2.png',
    'lab_address': '14797 NE 95th St, Redmond, WA 98502',
    'lab_street': '14797 NE 95th St',
    'lab_city': 'Redmond',
    'lab_county': 'King',
    'lab_state': 'WA',
    'lab_zipcode': '98052',
    'lab_latitude': 47.685890,
    'lab_longitude': -122.143640,
    'lab_phone': '(206) 743-8843',
    'lab_email': 'info@conflabs.com',
}

CONFIDENCE_COA = {
    'analyses': {
        'Cannabinoids': 'cannabinoids',
        'Foreign Matter': 'foreign_matter',
        'GC Pesticides': 'pesticides',
        'LC Pesticides': 'pesticides',
        'Microbes': 'microbes',
        'Mycotoxins': 'mycotoxins',
        'Terpenes': 'terpenes',
        'Water Activity': 'water_activity',
    },
    'fields': [
        'name',
        'analysis',
        'value',
        'limit',
        'units',
        'lod',
        'loq',
        'status',
        'date_tested',
    ],
}


def calculate_total_cannabinoids(
        results: List[dict],
        analysis: Optional[str] = 'cannabinoids',
        decarb: Optional[float] = DECARB,
        decimal_places: Optional[int] = 4,
    ) -> float:
    """Calculates total cannabinoids, applying a decarb rate to acidic
    cannabinoids, given a list of results.
    """
    total_cannabinoids = 0.0
    for result in results:
        if result['analysis'] == analysis:
            value = result['value']
            if isinstance(value, float):
                if result['key'].endswith('a'):
                    total_cannabinoids += decarb * value
                else:
                    total_cannabinoids += value
    return round(total_cannabinoids, decimal_places)


def calculate_total_terpenes(
        results: List[dict],
        analysis: Optional[str] = 'terpenes',
        decarb: Optional[float] = 1,
        decimal_places: Optional[int] = 4,
    ) -> float:
    """Calculates total terpenes given a list of results.
    """
    return calculate_total_cannabinoids(
        results,
        decarb=decarb,
        analysis=analysis,
        decimal_places=decimal_places,
    )


def calculate_total_cbd(
        results: List[dict],
        cbd_key: Optional[str] = 'cbd',
        cbda_key: Optional[str] = 'cbda',
        decarb: Optional[float] = DECARB,
    ) -> float:
    """Calculates total CBD given a list of results.
    """
    results_data = pd.DataFrame(results)
    try:
        cbd = results_data.loc[results_data['key'] == cbd_key].iloc[0]['value']
    except IndexError:
        cbd = 0
    try:
        cbda = results_data.loc[results_data['key'] == cbda_key].iloc[0]['value']
    except IndexError:
        cbda = 0
    cbd = convert_to_numeric(cbd)
    if not isinstance(cbd, float):
        cbd = 0
    cbda = convert_to_numeric(cbda)
    if isinstance(cbda, float):
        cbd += cbda * decarb
    return cbd


def calculate_total_thc(
        results: List[dict],
        thc_key: Optional[str] = 'delta_9_thc',
        thca_key: Optional[str] = 'thca',
        decarb: Optional[float] = DECARB,
    ) -> float:
    """Calculates total THC given a list of results.
    """
    results_data = pd.DataFrame(results)
    try:
        thc = results_data.loc[results_data['key'] == thc_key].iloc[0]['value']
    except IndexError:
        thc = 0
    try:
        thca = results_data.loc[results_data['key'] == thca_key].iloc[0]['value']
    except IndexError:
        thca = 0
    thc = convert_to_numeric(thc)
    if not isinstance(thc, float):
        thc = 0
    thca = convert_to_numeric(thca)
    if isinstance(thca, float):
        thc += thca * decarb
    return thc


def parse_confidence_pdf(
        parser,
        doc: Any,
        coa_pdf: Optional[str] = '',
        **kwargs,
    ) -> dict:
    """Parse a Confidence Analytics COA PDF.
    Args:
        parser (CoADoc): A CoADoc parsing client.
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        coa_pdf (str): A filename to use for the `coa_pdf` field (optional).
    Returns:
        (dict): The sample data.
    """
    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = coa_pdf or doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = coa_pdf or report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the lab data.
    front_page = report.pages[0]
    front_page_text = front_page.extract_text()
    front_page_lines = front_page_text.split('\n')
    for i, line in enumerate(front_page_lines):

        # Get the sample number as the lab ID.
        if 'Sample #' in line:
            obs['lab_id'] = line.split('Sample # ')[-1]

        # Get the product name, product ID, and date received.
        elif 'Sample Name:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' ')
            obs['date_received'] = parts[-1]
            obs['product_id'] = parts[-2]
            obs['product_name'] = ' '.join(parts[0:-2])

        # Get the product type, external ID, and date tested.
        elif 'Type:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' ')
            obs['date_tested'] = parts[-1]
            obs['external_id'] = parts[-2]
            obs['product_type'] = ' '.join(parts[0:-2])

        # Get the producer.
        elif 'Origination:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(',')[0].split(' ')
            obs['producer_license_number'] = parts[-3]
            obs['producer'] = ' '.join(parts[0:-3])
        
        # Get the producer address.
        elif 'Address:' in line:
            next_line = front_page_lines[i + 1]
            parts = next_line.split(' Date of Harvest:')[0].split(' ')
            obs['producer_street'] = ' '.join(parts[0:-1])

            # Get the city, zip code, and date harvested from the next line.
            address_line = front_page_lines[i + 2]
            address_parts = address_line.split(',')
            zip_parts = address_parts[-1].strip().split(' ')
            obs['producer_city'] = address_parts[0].title()
            obs['producer_state'] = zip_parts[0]
            obs['producer_zipcode'] = zip_parts[1]
            obs['producer_address'] = ', '.join([
                obs['producer_street'],
                obs['producer_city'],
                obs['producer_state'] + ' ' + obs['producer_zipcode'],
            ])
            if '(not provided)' in address_line:
                obs['date_harvested'] = None
            else:
                obs['date_harvested'] = zip_parts[-1]
        
        # Get the sum of cannabinoids.
        elif 'Total Canna. (raw sum):' in line:
            value = float(line.split('%')[0].split(':')[-1])
            obs['sum_cannabinoids'] = round(value, 3)

        # TODO: Get the analysis statuses.
        # 'Foreign Matter + Seeds:PASS Microbes:PASS Pesticides:PASS',
        # 'Water Activity:PASS Mycotoxins:PASS Heavy Metals:NE',
        # 'Residual Solvents:NE   '

    # Get all of the lines of the document.
    all_lines = []
    for page in report.pages[1:]:
        all_lines.extend(page.extract_text().split('\n'))

    # Deprecated: Aggregate all of the analyte tables.
    # analyte_lines = []
    # header = False
    # for line in all_lines:
    #     if 'Analyte Name' in line:
    #         header = True
    #     elif 'Document Created' in line:
    #         header = False
    #     elif '[ END OF ANALYTE TABLE ]' in line:
    #         break
    #     elif header:
    #         analyte_lines.append(line)

    # Aggregate all of the analyte results.
    pattern = r'^\w+.*\d{4}-\d{2}-\d{2}$'
    analyte_lines = [line for line in all_lines if re.match(pattern, line)]
    analyte_lines = [line for line in analyte_lines if not line.startswith('Date of Rec')]

    # Remove blank lines from the analyte tables.
    analyte_lines = [x for x in analyte_lines if x.strip()]

    # Format the results.
    analyses, results = [], []
    standard_analyses = CONFIDENCE_COA['analyses']
    standard_fields = CONFIDENCE_COA['fields']
    analysis_names = list(standard_analyses.keys())
    analysis_keys = list(standard_analyses.values())
    for line in analyte_lines:

        # Identify the analysis.
        values = line.replace('< MRL', '<LOQ')
        for n, analysis in enumerate(analysis_names):
            if analysis in values:
                analysis_key = analysis_keys[n]
                values = values.replace(analysis, analysis_key)
                analyses.append(analysis_key)
                break

        # Remove extra spaces.
        values = values.split(' ')
        values = [x for x in values if x.strip()]

        # Parse the result for the analyte.
        result = {}
        for k, field in enumerate(reversed(standard_fields)):
            if field == 'name':
                name = ' '.join(values[0:-8])
                name = name.rstrip('3')
                key = snake_case(name)
                analyte = parser.analytes.get(key, key)
                result['name'] = name
                result['key'] = analyte
            else:
                # FIXME:
                result[field] = convert_to_numeric(values[-k - 1])

        # Skip totals.
        if analyte == 'raw' or analyte == 'total' or not analyte:
            continue
        
        # Record the analyte result.
        results.append(result)

    # Convert terpenes to percentages.
    for i, result in enumerate(results):
        if result['analysis'] == 'terpenes':
            result['units'] = 'percent'
            try:
                result['value'] = result['value'] / 10_000
            except TypeError:
                pass
            results[i] = result

    # Calculate total cannabinoids, terpenes, CBD, and THC.
    obs['total_cannabinoids'] = calculate_total_cannabinoids(results)
    obs['total_terpenes'] = calculate_total_terpenes(results)
    obs['total_cbd'] = calculate_total_cbd(results)
    obs['total_thc'] = calculate_total_thc(results)

    # Get the producer's latitude and longitude from the
    # `cannabis_licenses` dataset or by geocoding their address.
    # FIXME:
    wa_licenses = load_dataset('cannlytics/cannabis_licenses', 'wa')
    licenses = wa_licenses['data'].to_pandas()
    criterion = licenses['license_number'].str.contains(obs['producer_license_number'])
    match = licenses.loc[criterion]
    if len(match):
        licensee = match.iloc[0]
        obs['producer_county'] = licensee['premise_county']
        obs['producer_latitude'] = licensee['premise_latitude']
        obs['producer_longitude'] = licensee['premise_longitude']
    
    # FIXME: This my be expensive.
    # else:
    #     try:
    #         google_maps_api_key = os.environ['GOOGLE_MAPS_API_KEY']
    #         location = search_for_address(
    #             obs['producer_address'],
    #             api_key=google_maps_api_key
    #         )
    #         for key, value in location.items():
    #             obs[f'producer_{key}'] = value
    #     except:
    #         print("""Set `GOOGLE_MAPS_API_KEY` environment variable to
    #         get the producer's latitude and longitude.""")
    #         pass

    # Get the methods.
    methods = []
    lines = report.pages[-1].extract_text().split('\n')
    header = False
    for line in lines:
        if 'Analytical Methods Used' in line:
            header = True
        elif header:
            method = line.strip()
            if method:
                methods.append(method)
            else:
                break

    # Get the lab results URL from the QR code.
    obs['lab_results_url'] = parser.find_pdf_qr_code_url(front_page)
    
    # Close the report.
    report.close()

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs = {**CONFIDENCE, **obs}
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['methods'] = json.dumps(methods)
    obs['results'] = results
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


def parse_confidence_url(
        parser,
        url: str,
        temp_path: Optional[str] = '/tmp',
        **kwargs
    ) -> dict:
    """Parse a Confidence Analytics COA URL.
    Args:
        url (str): The COA URL.
        headers (Any): Optional headers for standardization.
        max_delay (float): The maximum number of seconds to wait
            for the page to load.
        persist (bool): Whether to persist the driver.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """
    # Download the PDF.
    coa_pdf = download_file_from_url(url, temp_path, ext='.pdf')

    # Extract the data with the PDF parsing algorithm.
    data = parse_confidence_pdf(parser, coa_pdf)

    # Record the URL.
    data['lab_results_url'] = url
    return data


def parse_confidence_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Confidence Analytics COA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        kwargs (arguments): Arguments to pass to the parsing algorithms.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('https'):
            return parse_confidence_url(parser, doc, **kwargs)
    return parse_confidence_pdf(parser, doc, **kwargs)


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc
    from dotenv import dotenv_values

    # Set a Google Maps API key.
    config = dotenv_values('../../../.env')
    os.environ['GOOGLE_MAPS_API_KEY'] = config['GOOGLE_MAPS_API_KEY']

    # Specify testing constants.
    coa_url = 'https://certs.conflabs.com/full/WA-kXIRbGqnLVBI-WA-221015-052.pdf'
    doc = '../../../tests/assets/coas/confidence-analytics/13232582566688421-Flower-Dirty-Banana-Breath-WA-221015-052.pdf'
    temp_path = '../../../tests/assets/coas/tmp'

    # [✓] TEST: Identify LIMS.
    parser = CoADoc()
    lims = parser.identify_lims(doc, lims={'Confidence Analytics': CONFIDENCE})
    assert lims == 'Confidence Analytics'

    # [✓] TEST: Parse COA PDF.
    parser = CoADoc()
    data = parse_confidence_pdf(parser, doc)
    assert data is not None

    # [✓] TEST: Parse COA URL.
    parser = CoADoc()
    data = parse_confidence_url(parser, coa_url, temp_path=temp_path)
    assert data is not None

    # [✓] TEST: Parse COA URL and PDF ambiguously.
    parser = CoADoc()
    coas = [coa_url, doc]
    for coa in coas:
        data = parser.parse(coa, temp_path=temp_path)
        assert data is not None
    print('✓ Completed Confidence Analytics COA parsing tests.')
