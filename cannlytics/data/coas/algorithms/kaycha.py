"""
Parse Kaycha Labs COAs
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/17/2022
Updated: 6/3/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Kaycha Labs COA PDFs.

Data Points:

    ✓ lab_id
    ✓ product_name
    ✓ product_type
    ✓ batch_number
    ✓ product_size
    - serving_size
    - servings_per_package
    ✓ sample_weight
    ✓ sample_id (augmented)
    ✓ strain_name
    ✓ lab
    ✓ lab_image_url
    - lab_license_number
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
    ✓ producer
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    - distributor_license_number
    ✓ date_collected
    ✓ date_tested
    ✓ date_received
    - images
    ✓ analyses
    ✓ {analysis}_status
    ✓ status
    ✓ lab_results_url
    ✓ coa_urls
    ✓ methods
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_terpenes
    ✓ results
        ✓ cannabinoids
        ✓ terpenes
        ✓ pesticides
        ✓ heavy_metals
        ✓ microbes
        ✓ mycotoxins
        ✓ residual_solvents
        ✓ foreign_matter
        ✓ water_activity
        ✓ moisture
"""
# Standard imports.
from ast import literal_eval
import base64
from datetime import datetime
import json
import io
import re
import os
import tempfile
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber
from PIL import Image

# Internal imports.
from cannlytics import firebase
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.constants import ANALYTES
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
KAYCHA_LABS = {
    'coa_algorithm': 'kaycha.py',
    'coa_algorithm_entry_point': 'parse_kaycha_coa',
    'lims': 'Kaycha Labs',
    'lab': 'Kaycha Labs',
    'lab_image_url': 'https://www.kaychalabs.com/wp-content/uploads/2020/06/newlogo-2.png',
    'lab_address': '4101 SW 47th Ave, Suite 105, Davie, FL 33314',
    'lab_street': '4101 SW 47th Ave, Suite 105',
    'lab_city': 'Davie',
    'lab_county': 'Broward',
    'lab_state': 'FL',
    'lab_zipcode': '33314',
    'lab_phone': '833-465-8378',
    'lab_email': 'info@kaychalabs.com',
    'lab_website': 'https://www.kaychalabs.com/',
    'lab_latitude': 26.071350,
    'lab_longitude': -80.210750,
    # FIXME: Make license number dynamic as Kaycha Labs operate in multiple states.
    'lab_license_number': 'CMTL-0002',
}
KAYCHA_LABS_COA = {
    'fields': {
        'Matrix': 'product_type',
        'Sample': 'lab_id',
        'Harvest/Lot ID': 'source_id',
        'Batch#': 'batch_number',
        'Cultivation Facility': 'producer',
        'Processing Facility': 'processor',
        'Distributor Facility': 'distributor',
        'Source Facility': 'source',
        'Seed to Sale': 'traceability_id',
        'Batch Date': 'date_harvested', # FIXME: This date is not being parsed correctly.
        'Sample Size Received': 'sample_weight',
        'Total Batch Size': 'batch_size',
        'Retail Product Size': 'product_size',
        'Ordered': 'date_received',
        'Sampled': 'date_collected',
        'Completed': 'date_tested',
        # 'Sampling Method': 'method_sampling',
    },
    'screening_analyses': [
        'pesticides',
        'heavy_metals',
        'microbes',
        'mycotoxins',
        'residuals_solvents',
        'foreign_matter',
        'water_activity',
        'moisture',
        'terpenes',
    ],
    'screening_statuses': {
        'PASSED': 'Pass',
        'FAILED': 'Fail',
        'TESTED': 'Tested',
        'NOT TESTED': 'N/A',
    },
}


def get_kaycha_terpenes(parser, page, obs, results):
    """Get terpenes from a Kaycha Labs COA PDF."""
    # Check if the page has terpenes.
    if 'Terpenes TESTED' not in page.extract_text():
        return obs, results

    # Split the page in half.
    left = page.within_bbox((0, 0, page.width * 0.5, page.height)).extract_text()
    right = page.within_bbox((page.width * 0.5, 0, page.width, page.height)).extract_text()

    # Get the relevant portions.
    left = left.split('TOTAL TERPENES')[-1].split('This Kaycha Labs Certification shall not be reproduced')[0]
    right = right.split('(%)')[-1].split('Analyzed by')[0]
    left_lines = [x for x in left.split('\n') if x]
    right_lines = [x for x in right.split('\n') if x]

    # Get total terpenes.
    total = left_lines[-1].split('(%)')[-1].strip()
    obs['total_terpenes'] = convert_to_numeric(total, strip=True)

    # Get individual terpenes.
    lines = left_lines[1:-1] + right_lines
    for line in lines:
        first_value = find_first_value(line)
        name = line[:first_value].strip()
        key = parser.analytes.get(snake_case(name), snake_case(name))
        values = line[first_value:].strip().split(' ')
        results.append({
            'analysis': 'terpenes',
            'key': key,
            'lod': convert_to_numeric(values[0]),
            'name': name,
            'units': 'percent',
            'value': convert_to_numeric(values[-1]),
            'mg_unit': convert_to_numeric(values[1]),
        })

    # Return the observation and results.
    return obs, results


# UNDER DEVELOPMENT:
def parse_kaycha_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        coa_parameters: Optional[dict] = KAYCHA_LABS_COA,
        **kwargs,
    ) -> dict:
    """Parse a Kaycha Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """

    # FIXME: If the `doc` is a URL, then download the PDF to `temp_path`.
    # And then use the downloaded PDF as the doc.
    if temp_path is None:
        temp_path = tempfile.gettempdir()

    # Get the lab's parameters.
    screening_analyses = coa_parameters['screening_analyses']
    screening_statuses = coa_parameters['screening_statuses']

    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the text of the first page.
    front_page = report.pages[0]
    text = front_page.extract_text()
    text = text.split('This Kaycha Labs Certification shall not be reproduced')[0]
    lines = text.split('\n')

    # Get the lab results URL from the QR code.
    coa_url = parser.find_pdf_qr_code_url(front_page)
    obs['lab_results_url'] = coa_url

    # Format `coa_urls`
    if coa_url is not None:
        filename = coa_url.split('/')[-1].split('?')[0] + '.pdf'
        obs['coa_urls'] = json.dumps([{'url': coa_url, 'filename': filename}])

    # Get lab details.
    parts = lines[5].split(',')
    city, state, zipcode = [x.strip() for x in parts[:3]]
    obs['lab_street'] = lines[4].title()
    obs['lab_city'] = city.title()
    obs['lab_state'] = state
    obs['lab_zipcode'] = zipcode

    # Get sample details.
    obs['product_name'] = lines[1]
    obs['strain_name'] = lines[2]
    obs['product_type'] = lines[3].split(':')[-1].strip()
    obs['lab_id'] = lines[6].split(':')[-1].strip()

    # Get additional sample details.
    results = []
    totals = ['total_thc', 'total_cbd', 'total_cannabinoids']
    for i, line in enumerate(lines):

        # Get sample fields.
        for key, value in coa_parameters['fields'].items():
            field = key.lower()
            cell = line.lower()
            if f'{field}:' in cell or f'{field} :' in cell:
                obs[value] = line.split(':')[-1].strip()
            elif f'{field}#' in cell:
                obs[value] = line.split('#')[-1].strip()

        # Get distributor, distributor address, and testing status.
        if '|' in line:
            name = line.split('|')[-1]
            for k, v in screening_statuses.items():
                if k in line:
                    name = name.replace(k, '').strip()
                    obs['status'] = v
            street = lines[i + 1]
            city, state, zipcode, _ = [x.strip() for x in lines[i + 2].split(',')]
            obs['distributor'] = name
            obs['distributor_address'] = f'{street}, {city}, {state} {zipcode}'
            obs['distributor_street'] = street
            obs['distributor_city'] = city
            obs['distributor_state'] = state
            obs['distributor_zipcode'] = zipcode
        
        # Get totals.
        if 'Total THC' in line and obs.get('total_thc') is None:
            values = [convert_to_numeric(x, strip=True) for x in lines[i + 1].split(' ')]
            for v, value in enumerate(values):
                obs[totals[v]] = value
        
        # Get cannabinoids.
        # Optional: Also record mg/unit, method, and instrument.
        if line.startswith('%'):
            analytes = lines[i - 1].split(' (DRY)')[0].split(' ')
            if len(analytes) <= 2:
                analytes = lines[i - 2].split(' ')
            keys = [parser.analytes.get(snake_case(x), snake_case(x)) for x in analytes]
            values = [convert_to_numeric(x) for x in line.split('Analyte')[0].lstrip('% ').split(' ') if x != '']
            if lines[i + 2].startswith('Analysis'):
                lod = [convert_to_numeric(x) for x in lines[i + 3].lstrip('LOD ').split(' ') if x != '']
            else:
                lod = [convert_to_numeric(x) for x in lines[i + 2].lstrip('LOD ').split(' ') if x != '']
            for k, key in enumerate(keys):
                results.append({
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': analytes[k],
                    'value': values[k],
                    'unit': 'percent',
                    'lod': lod[k],
                })
            break

    # FIXME: Get lab license number.
    # State License # CMTL-0002

    # TODO: Try to get producer details from licenses data.
    # - producer_address
    # - producer_street
    # - producer_city
    # - producer_state
    # - producer_zipcode
    # - producer_license_number

    # Get analyses and status data.
    analyses = []
    safety_results = text.split('SAFETY RESULTS')[-1].split('Cannabinoid')[0].split('\n')
    statuses = safety_results[2].replace('NOT TESTED', 'NOT_TESTED').split(' ')
    for i, status in enumerate(statuses):
        if status == 'NOT_TESTED':
            continue
        if status == 'Solvents':
            status = safety_results[3]
        analysis = screening_analyses[i]
        obs[f'{analysis}_status'] = screening_statuses.get(status, status)
        analyses.append(analysis)

    # Get terpene results.
    # Optional Add "Analysis Method" and "Instrument Used".
    num_of_pages = len(report.pages)
    if num_of_pages >= 2:
        page = report.pages[1]
        obs, results = get_kaycha_terpenes(parser, page, obs, results)

    # Get additional analyses for full panel COAs.
    rows = []
    if num_of_pages > 2:
        for page in report.pages[2:]:

            # Handle residual solvents page.
            page_text = page.extract_text()
            if 'Residual Solvents' in page_text:
                lines = page_text.split('Residual Solvents')[1].strip().split('\n')
                for line in lines[2:]:
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = parser.analytes.get(snake_case(name), snake_case(name))
                    values = line[first_value:].strip().split(' ')
                    results.append({
                        'analysis': 'residual_solvents',
                        'key': key,
                        'lod': convert_to_numeric(values[0]),
                        'name': name,
                        'units': values[1],
                        'value': convert_to_numeric(values[-1]),
                        'status': values[-2],
                        'limit': convert_to_numeric(values[2]),
                    })
                continue

            # Split the page in half.
            left = page.within_bbox((0, 0, page.width * 0.49, page.height)).extract_text()
            right = page.within_bbox((page.width * 0.49, 0, page.width, page.height)).extract_text()

            # Get the relevant portions.
            left = re.split(r'Page \d+ of \d+', left)[-1].split('This Kaycha Labs Certification shall not be reproduced')[0]
            left_lines = [x for x in left.split('\n') if x]
            right_lines = [x for x in right.split('\n') if x]

            # Remove unnecessary rows.
            left_lines = [x for x in left_lines if ':' not in x]
            right_lines = [x for x in right_lines if ':' not in x]
            rows.extend(left_lines + right_lines)

    # Keep only rows with values.
    rows = [x for x in rows if len(x.split(' ')) > 3]
    rows = [x for x in rows if x != obs['product_name']]
    rows = [x for x in rows if ', US' not in x]
    cells = [x for x in rows if x[:3].isupper() and not x.startswith('SOP.')]
    cells = [x .replace('*', '').replace('Not Present', 'ND') for x in cells]

    # Define contaminants.
    microbes = ['ASPERGILLUS', 'SALMONELLA', 'ESCHERICHIA', 'TOTAL YEAST']
    mycotoxins = ['AFLATOXIN', 'OCHRATOXIN']
    heavy_metals = ['TOTAL CONTAMINANT LOAD METALS', 'ARSENIC', 'CADMIUM', 'MERCURY', 'LEAD']
    contaminants = [{'name': microbe, 'analysis': 'microbes', 'units': 'CFU/g'} for microbe in microbes] + \
        [{'name': mycotoxin, 'analysis': 'mycotoxins', 'units': 'ppm'} for mycotoxin in mycotoxins] + \
        [{'name': metal, 'analysis': 'heavy_metals', 'units': 'ppm'} for metal in heavy_metals]

    # Get contaminants: microbes, mycotoxins, and heavy metals.
    remove = []
    for contaminant in contaminants:
        analyte = contaminant['name']
        analysis = contaminant['analysis']
        units = contaminant['units']
        for cell in cells:
            if analyte in cell:
                remove.append(cell)
                line = cell
                line = line.replace('TOTAL YEAST AND MOLD', 'MOLD')
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) == 2:
                    results.append({
                        'analysis': analysis,
                        'key': key,
                        'lod': None,
                        'name': name,
                        'units': units,
                        'value': convert_to_numeric(values[0]),
                        'status': values[-1],
                    })
                else:
                    results.append({
                        'analysis': analysis,
                        'key': key,
                        'lod': convert_to_numeric(values[0]),
                        'name': name,
                        'units': values[1],
                        'value': convert_to_numeric(values[2]),
                        'status': values[-2],
                        'limit': convert_to_numeric(values[-1]),
                    })

    # Remove collected cells.
    cells = [x for x in cells if x not in remove]

    # Get any pesticides analyzed.
    if cells:
        for line in cells:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'pesticides',
                'key': key,
                'lod': convert_to_numeric(values[0]),
                'name': name,
                'units': values[1],
                'value': convert_to_numeric(values[-1]),
                'status': values[-2],
                'limit': convert_to_numeric(values[2]),
            })

    # Get moisture content, water activity, and foreign matter.
    screens = [
        {'name': 'Filth and Foreign Material', 'key': 'foreign_matter', 'units': 'percent'},
        {'name': 'Moisture Content', 'key': 'moisture_content', 'units': 'percent'},
        {'name': 'Water Activity', 'key': 'water_activity', 'units': 'aW'},
    ]
    for screen in screens:
        name = screen['name']
        for row in rows:
            if row.startswith(name):
                values = row.replace(name, '').strip().split(' ')
                results.append({
                    'name': name,
                    'key': screen['key'],
                    'value': convert_to_numeric(values[2]),
                    'units': screen['units'],
                    'lod': convert_to_numeric(values[0]),
                    'limit': convert_to_numeric(values[-1]),
                    'status': values[-2]
                })
                break

    # FIXME: Save the image data to Firebase Storage.
    # image_index = 5
    # try:
    #     temp_dir = tempfile.gettempdir()
    #     file_ref = f'data/lab_results/images/{lab_id}/image_data.png'
    #     file_path = os.path.join(temp_dir, 'image_data.png')
    #     image_data = parser.get_pdf_image_data(front_page, image_index=image_index)
    #     parser.save_image_data(image_data, image_file=file_path)
    #     bucket_name = config['FIREBASE_STORAGE_BUCKET']
    #     firebase.upload_file(file_ref, file_path, bucket_name=bucket_name)
    #     download_url = firebase.get_file_url(file_ref, bucket_name=bucket_name)
    #     obs['images'] = [{'ref': file_ref, 'url': download_url, 'filename': 'image_data.png'}]
    # except:
    #     print('Failed to get image data.')
    #     obs['images'] = []

    # Get all the lines with methods.
    method_lines = ''
    for page in report.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if 'Analysis Method :' in line:
                method_lines += line + '\n'

    # Find all matches in the text and return them.
    pattern = r'SOP\.[\w\.\-\(\)]+'
    methods = re.findall(pattern, method_lines)

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
    obs = {**KAYCHA_LABS, **obs}
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['methods'] = json.dumps(methods)
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # [✓] TEST: Identify LIMS.
    parser = CoADoc()
    docs = [
        '../../../../tests/assets/coas/kaycha-labs/DA30318004-001-Original.pdf',
    ]
    for doc in docs:
        lims = parser.identify_lims(doc, lims={'Kaycha Labs': KAYCHA_LABS})
        assert lims == 'Kaycha Labs'

    # [ ] TEST: Parse a full panel COA PDF.
    doc = '../../../../tests/assets/coas/kaycha-labs/DA30318004-001-Original.pdf'
    data = parse_kaycha_coa(parser, doc)
    assert data is not None


    # [ ] TEST: Parse a cannabinoid and terpene only COA PDF.
    # doc = 'D://data/florida/lab_results/.datasets/pdfs/MMTC-2019-0015/GA11104001-001.pdf'


    # [ ] TEST: Parse a COA with residual solvent screening.
    doc = '../../../../tests/assets/coas/kaycha-labs/DA20330006-008.pdf'


    # [ ] TEST: Parse a non-mandatory COA PDF.
    # doc = 'D://data/florida/lab_results/.datasets/pdfs/MMTC-2019-0015/GA11104001-001.pdf'


    # [ ] TEST: Parse Kaycha Labs COAs from URL.
    # urls = [
    #     'https://tn.yourcoa.com/api/coa-download?sample=KN20119003-002&wl_id=291',
    # ]


    # [ ] TEST: Parse a full panel COA from a URL.
    # urls = [
    #     'https://getfluent.com/wp-content/uploads/2023/03/DA30318004-001-Original.pdf',
    # ]


    # [ ] TEST: Parse COAs for various product types.


    # [ ] TEST: Parse historic COAs.
    # doc = '../../../../tests/assets/coas/kaycha-labs/DA90911001-009.pdf'


    # TODO: Handle Evio Labs COAs.
