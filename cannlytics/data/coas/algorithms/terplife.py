"""
Parse TerpLife Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 11/14/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse TerpLife Labs COA PDFs.

Data Points:

    ✓ analyses
    - methods
    ✓ date_produced
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    ✓ image_url
    - coa_url
    - lab_results_url
    ✓ producer
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ lab_id
    ✓ product_type
    ✓ batch_number
    ✓ product_size
    ✓ sample_weight
    ✓ results
    - status
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_terpenes
    ✓ sample_id
    ✓ strain_name
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number (augmented)
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

"""
# Standard imports.
from datetime import datetime
import json
import os
import re
import tempfile
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber

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
    download_file_from_url,
    snake_case,
)


# It is assumed that the lab has the following details.
TERPLIFE_LABS = {
    'coa_algorithm': 'terplife.py',
    'coa_algorithm_entry_point': 'parse_terplife_coa',
    'url': 'www.terplifelabs.com',
    'lims': 'TerpLife Labs',
    'lab': 'TerpLife Labs',
    'lab_license_number': 'CMTL-00010',
    'lab_image_url': 'https://www.terplifelabs.com/wp-content/uploads/2022/03/website-logo.png',
    'lab_address': '10350 Fisher Ave, Tampa',
    'lab_street': '10350 Fisher Ave',
    'lab_city': 'Tampa',
    'lab_county': 'Hillsborough',
    'lab_state': 'FL',
    'lab_zipcode': '33619',
    'lab_phone': '813-726-3103',
    'lab_email': 'info@terplifelabs.com',
    'lab_website': 'https://www.terplifelabs.com/',
    'lab_latitude': 27.959174,
    'lab_longitude': -82.3278,
}

# Known TerpLife cannabinoids and terpenes.
terpenes = [
    'D-Limonene', 'E-Caryophyllene', 'Farnesene', 'alpha-Humulene',
    'Guaiol', 'alpha-Pinene', 'beta-Pinene', 'beta-Myrcene', 
    'Linalool', 'alpha-Fenchyl alcohol, (+)-', 'alpha Bisabolol, L', 
    'alpha-Terpineol', 'beta-Ocimene', 'E-Nerolidol', 'Camphene', 
    'Borneol', 'Terpinolene', 'Caryophyllene Oxide', 'Fenchone', 
    '3-Carene (+)-', 'alpha-Cedrene', 'alpha-Phellandrene', 
    'alpha-Terpinene', 'Camphor', 'Cedrol', 'Eucalyptol', 
    'gamma-Terpinene', 'Geraniol', 'Geranyl Acetate', 'Isoborneol', 
    'Isopulegol', 'Menthol', 'Nerol', 'p-Cymene', 'Pulegone', 
    'Sabinene', 'Sabinene hydrate', 'Valencene', 'Z-Nerolidol'
]
cannabinoids = [
    'Cannabichromene (CBC)', 'Cannabidiol (CBD)', 'Cannabidiolic acid (CBDA)',
    'Cannabidivarin (CBDV)', 'Cannabigerol (CBG)', 'Cannabigerolic acid (CBGA)',
    'Cannabinol (CBN)', 'd8 - Tetrahydrocannabinoid (d8-THC)',
    'd9 - Tetrahydrocannabinoid (d9-THC)', 'd9 - Tetrahydrocannabinolic acid (THCA)',
    'Tetrahydrocannabivarin (THCV)'
]


def parse_terplife_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        image_dir: Optional[str] = None,
        image_starting_index: Optional[int] = 0,
        image_ending_index: Optional[int] = -1,
        save_to_firebase: Optional[bool] = False,
        verbose: Optional[bool] = False,
        **kwargs,
    ) -> dict:
    """Parse a TerpLife Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Initialize.
    obs = {}
    if temp_path is None:
        temp_path = tempfile.gettempdir()
    if image_dir is None:
        image_dir = tempfile.gettempdir()

    # Read the PDF.
    # Note: If the `doc` is a URL, then it is downloaded to `temp_path`.
    if isinstance(doc, str):
        if doc.startswith('https'):
            coa_pdf = download_file_from_url(doc, temp_path, ext='.pdf')
            report = pdfplumber.open(coa_pdf)
        else:
            report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the front page text.
    front_page = report.pages[0]
    number_of_pages = len(report.pages)
    front_page_text = report.pages[0].extract_text()

    # Apply OCR when necessary.
    if not front_page_text:
        if verbose:
            print('Applying OCR.')
        temp = tempfile.mkstemp('.pdf')[1]
        parser.pdf_ocr(doc, temp, temp_path=temp_path)
        report = pdfplumber.open(temp)
        front_page = report.pages[0]
        number_of_pages = len(report.pages)
        front_page_text = report.pages[0].extract_text()
        obs['parsed_with_ocr'] = True

    # Clean extraneous text from the front page.
    extras = [
        'Unless otherwise stated all quality control samples',
        ' performed within specifications established by the Laboratory.'
    ]
    front_page_text = front_page_text.split('The data contained')[0]
    for extra in extras:
        front_page_text = front_page_text.replace(extra, '')

    # Process the text.
    front_page_text = front_page_text.replace('█', '\n')    
    lines = front_page_text.split('\n')
    lines = [x for x in lines if x != '']

    # Optional: Save product image and COA to Firebase Storage.
    if save_to_firebase:

        # Initialize Firebase.
        try:
            from cannlytics import firebase
            from firebase_admin import get_app
            firebase.initialize_firebase()
            app = get_app()
            bucket_name = f'{app.project_id}.appspot.com'
        except:
            pass

        # Optional: Save the product image.
        try:
            image_index, _ = max(
                enumerate(front_page.images[image_starting_index:image_ending_index]),
                key=lambda img: img[1]['width'] * img[1]['height']
            )
            image_data = parser.get_pdf_image_data(front_page, image_index=image_index + image_starting_index)
            image_filename = doc.split('/')[-1].replace('.pdf', '.png')
            image_file = os.path.join(image_dir, image_filename)
            parser.save_image_data(image_data, image_file)
            image_ref = f'data/lab_results/images/terplife/{image_filename}'
            firebase.upload_file(image_ref, image_file, bucket_name=bucket_name)
            image_url = firebase.get_file_url(image_ref, bucket_name=bucket_name)
            obs['image_url'] = image_url
        except:
            obs['image_url'] = None

        # Optional: Save the COA PDF.
        try:
            filename = obs['coa_pdf']
            coa_ref = f'data/lab_results/pdfs/terplife/{filename}'
            firebase.upload_file(coa_ref, doc, bucket_name=bucket_name)
            coa_url = firebase.get_file_url(coa_ref, bucket_name=bucket_name)
            obs['coa_url'] = coa_url
        except:
            obs['coa_url'] = None

    # Find the analyses.
    analyses = []
    if 'Potency Summary' in front_page_text:
        analyses.append('cannabinoids')

    # TODO: Find the methods.
    methods = []

    # TODO: Keep track of the kind of COA.

    # Find the producer's address.
    corner = (0, 0, front_page.width / 3, front_page.height / 4)
    top_corner = front_page.crop(corner)
    address_text = top_corner.extract_text()
    address_text = address_text.split('Client Lic#:')[-1].split('\n', maxsplit=1)[-1]
    phone_pattern = r'\(\d{3}\) \d{3}-\d{4}'
    address = re.split(phone_pattern, address_text, maxsplit=1)[0]
    address = address.replace('\n', ' ').strip()
    parts = address.split(', ')
    state_zip = parts[-1].split(' ')
    obs['producer_address'] = address
    obs['producer_street'] = parts[0]
    obs['producer_city'] = parts[1]
    obs['producer_state'] = state_zip[0]
    obs['producer_zipcode'] = state_zip[1]

    # Get the product name
    for line in lines:
        if 'Total Sample Received' in line:
            name = line.split('Total Sample Received')[0].strip()
            name = name.replace('Sample Name:', '').strip()
            obs['product_name'] = name
            break

    # Find the product details.
    obs['project_id'] = lines[2]
    columns = {
        'Seed to Sale': 'traceability_id',
        'Retail Batch#': 'batch_number',
        'Client Lic#': 'producer_license_number',
        'Retail Batch Total Wt/Vol': 'batch_size',
        'Cultivar': 'strain_name',
        'Cultivation Facility': 'producer',
        'Processing Facility': 'distributor',
        'Compliance for Retail': 'status',
        'Total Units Received': 'sample_units',
        'Total Sample Received': 'sample_weight',
        'Retail Batch Date': 'date_produced',
        'Date Sampled': 'date_collected',
        'Date Received': 'date_received',
        'Date Reported': 'date_tested',
        'Matrix': 'product_type',
        'Unit Weight': 'product_size',
        'CCB ID': 'external_id',
        'Sample ID': 'lab_id',
    }
    keys = list(columns.keys())
    for key in keys:
        for line in lines:
            if key in line:
                part = line.split(key)[-1].split(':')[1].strip()
                for value in keys:
                    if value in part:
                        part = part.replace(value, '').strip()
                obs[columns[key]] = part
                break

    # Clean certain fields.
    try:
        obs['status'] = obs['status'].title()
    except:
        pass

    # Extract total terpenes.
    if 'Terpenes Summary' in front_page_text:
        analyses.append('terpenes')
        for line in lines:
            if 'Total Terpenes' in line:
                value = line.split('Total Terpenes')[-1].strip().split(' ')[0]
                obs['total_terpenes'] = convert_to_numeric(value)
                break

    # Extract total THC, CBD, and/or cannabinoids.
    if 'Terpenes Summary' in front_page_text:
        summary = front_page_text.split('Potency Summary')[-1].split('Terpenes Summary')[0]
    elif 'Potency Summary' in front_page_text:
        summary = front_page_text.split('Potency Summary')[-1].split('Cannabinoids')[0]
    else:
        summary = ''
    for line in summary.split('\n'):
        if '%' in line:
            values = [x.strip() for x in line.split('%') if x]
            if len(values) == 6:
                obs['total_thc'] = convert_to_numeric(values[0])
                obs['total_cbd'] = convert_to_numeric(values[1])
                obs['total_cannabinoids'] = convert_to_numeric(values[2])
                obs['total_thc_wet'] = convert_to_numeric(values[3])
                obs['total_cbd_wet'] = convert_to_numeric(values[4])
                obs['total_cannabinoids_wet'] = convert_to_numeric(values[5])
            elif len(values) == 3:
                obs['total_thc'] = convert_to_numeric(values[0])
                obs['total_cbd'] = convert_to_numeric(values[1])
                obs['total_cannabinoids'] = convert_to_numeric(values[2])
            elif len(values) >= 2:
                obs['total_thc'] = convert_to_numeric(values[0])
                obs['total_cbd'] = convert_to_numeric(values[1])
            break

    # Get results from full-panel reports, keeping track of analytes.
    analytes, results = [], []
    if number_of_pages > 1:
        for page in report.pages[1:]:
            text = page.extract_text()

            # Extract pesticide data.
            if 'Pesticides' in text:
                analyses.append('pesticides')
                midpoint = page.width * 0.475
                left_half = (0, 0, midpoint, page.height)
                left_half_page = page.crop(left_half)
                left_text = left_half_page.extract_text()
                left_section = left_text.split('Status')[1].split('LOD =')[0]
                left_section = left_section.split('ppb ppb ppb')[-1]
                left_lines = [x for x in left_section.split('\n') if x]
                right_half = (midpoint, 0, page.width, page.height * 0.75)
                right_half_page = page.crop(right_half)
                right_text = right_half_page.extract_text()
                right_section = right_text.split('Status')[1].split('LOD =')[0]
                right_section = right_section.split('ppb ppb ppb')[-1]
                right_lines = [x for x in right_section.split('\n') if x]
                for line in left_lines + right_lines:
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    values = [x.strip() for x in line[first_value:].split(' ') if x]
                    results.append({
                        'analysis': 'pesticides',
                        'key': key,
                        'name': name,
                        'dilution': convert_to_numeric(values[0]),
                        'limit': convert_to_numeric(values[1]),
                        'lod': convert_to_numeric(values[2]),
                        'value': convert_to_numeric(values[3]),
                        'status': values[-1],
                        'units': 'ppb',
                    })
                continue


            # Extract mycotoxins data.
            if 'Mycotoxins' in text:
                analyses.append('mycotoxins')
                midpoint = page.width / 2
                left_half = (0, 0, midpoint, page.height)
                left_half_page = page.crop(left_half)
                left_text = left_half_page.extract_text()
                section = left_text.split('Mycotoxins')[1].split('LOD =')[0]
                section = section.split('ppb ppb ppb')[-1]
                results_lines = [x for x in section.split('\n') if x]
                for line in results_lines:
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    values = [x.strip() for x in line[first_value:].split(' ') if x]
                    results.append({
                        'analysis': 'mycotoxins',
                        'key': key,
                        'name': name,
                        'dilution': convert_to_numeric(values[0]),
                        'limit': convert_to_numeric(values[1]),
                        'lod': convert_to_numeric(values[2]),
                        'value': convert_to_numeric(values[3]),
                        'status': values[-1],
                        'units': 'ppb',
                    })

            # Extract microbial data.
            if 'Microbials' in text:
                analyses.append('microbials')
                midpoint = page.width / 2
                right_half = (midpoint, 0, page.width, page.height)
                right_half_page = page.crop(right_half)
                right_text = right_half_page.extract_text()
                section = right_text.split('Microbials')[1].split('LOD =')[0]
                section = section.split('cfu/g cfu/g cfu/g')[-1]
                results_lines = [x for x in section.split('\n') if x]
                for line in results_lines:
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    values = [x.strip() for x in line[first_value:].split(' ') if x]
                    results.append({
                        'analysis': 'microbials',
                        'key': key,
                        'name': name,
                        'limit': convert_to_numeric(values[0]),
                        'lod': convert_to_numeric(values[1]),
                        'value': convert_to_numeric(values[2]),
                        'status': values[-1],
                        'units': 'cfu/g',
                    })

            # Extract foreign matter data.
            if 'Foreign Materials' in text:
                analyses.append('foreign_matter')
                midpoint = page.width / 2
                right_half = (midpoint, 0, page.width, page.height)
                right_half_page = page.crop(right_half)
                right_text = right_half_page.extract_text()
                section = right_text.split('Foreign Materials')[1].split('ND =')[0]
                section = section.split('Status')[-1]
                results_lines = [x for x in section.split('\n') if x]
                line = results_lines[0]
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                results.append({
                    'analysis': 'foreign_matter',
                    'key': key,
                    'name': name,
                    'limit': convert_to_numeric(values[0]),
                    'value': convert_to_numeric(values[1]),
                    'status': values[-1],
                    'units': 'percent',
                })

            # Extract water activity data.
            if 'Water Activity' in text:
                analyses.append('water_activity')
                midpoint = page.width / 2
                right_half = (midpoint, 0, page.width, page.height)
                right_half_page = page.crop(right_half)
                right_text = right_half_page.extract_text()
                section = right_text.split('Water Activity', maxsplit=1)[1].split('ND =')[0]
                section = section.split('Status')[-1]
                results_lines = [x for x in section.split('\n') if x]
                line = results_lines[-1]
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                results.append({
                    'analysis': 'water_activity',
                    'key': key,
                    'name': name,
                    'limit': convert_to_numeric(values[0]),
                    'value': convert_to_numeric(values[1]),
                    'status': values[-1],
                    'units': 'aW',
                })

            # Extract moisture content data.
            if 'Moisture Content' in text:
                analyses.append('moisture_content')
                midpoint = page.width / 2
                right_half = (midpoint, 0, page.width, page.height)
                right_half_page = page.crop(right_half)
                right_text = right_half_page.extract_text()
                section = right_text.split('Moisture Content', maxsplit=1)[1].split('Unless')[0]
                section = section.split('Status')[-1]
                results_lines = [x for x in section.split('\n') if x]
                line = results_lines[-1]
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                results.append({
                    'analysis': 'moisture_content',
                    'key': key,
                    'name': name,
                    'limit': convert_to_numeric(values[0]),
                    'value': convert_to_numeric(values[1]),
                    'status': values[-1],
                    'units': 'percent',
                })

            # Extract heavy metals data.
            if 'Heavy Metals' in text:
                analyses.append('heavy_metals')
                midpoint = page.width / 2
                left_half = (0, 0, midpoint, page.height)
                left_half_page = page.crop(left_half)
                left_text = left_half_page.extract_text()
                section = left_text.split('Heavy Metals')[2].split('LOD =')[0]
                section = section.split('ppb ppb ppb')[-1]
                results_lines = [x for x in section.split('\n') if x]
                for line in results_lines:
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    values = [x.strip() for x in line[first_value:].split(' ') if x]
                    results.append({
                        'analysis': 'heavy_metals',
                        'key': key,
                        'name': name,
                        'dilution': convert_to_numeric(values[0]),
                        'limit': convert_to_numeric(values[1]),
                        'lod': convert_to_numeric(values[2]),
                        'value': convert_to_numeric(values[3]),
                        'status': values[-1],
                        'units': 'ppb',
                    })
                continue

            # Extract terpenes not already collected.
            if 'Terpenes Summary' in text:
                results_text = text.split('Analyte Dilution LOD Results')[-1].split('Total Terpenes')[0]
                results_lines = results_text.split('\n')[2:-1]
                for line in results_lines:
                    line = line.replace('█', '')
                    first_value = find_first_value(line)
                    name = line[:first_value].strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    values = [x.strip() for x in line[first_value:].split(' ') if x]
                    analytes.append(name)
                    results.append({
                        'analysis': 'terpenes',
                        'key': key,
                        'name': name,
                        'dilution': convert_to_numeric(values[0]),
                        'lod': convert_to_numeric(values[1]),
                        'value': convert_to_numeric(values[2]),
                        'units': 'percent',
                    })
                continue

            # TODO: Extract residual solvents data.


            # Optional: Extract full-panel cannabinoids.


    # Extract the results on the front page.
    if 'Terpenes Summary' in front_page_text:
        results_text = front_page_text.split('Terpenes Summary')[-1].split('Terpenes Summary')[0]
        results_lines = results_text.split('Analyte Dilution')[-1].split('\n')[2:]
    else:
        results_text = front_page_text.split('Result\n')[-1].split('Total THC')[0]
        results_lines = results_text.split('\n')[1:]
    results_lines = [x.strip() for x in results_lines if x]
    for line in results_lines:

        # Skip totals.
        if 'Total Terpenes' in line:
            break
        elif 'Total THC' in line or 'Total CBD' in line:
            continue
        if 'Total Cannabinoids' in line and 'Terpenes Summary' in front_page_text:
            continue
        elif 'Total Cannabinoids' in line:
            break

        # Extract a result, if not already extracted.
        first_value = find_first_value(line)
        name = line[:first_value].strip()
        if name in analytes:
            continue
        key = snake_case(name)
        key = ANALYTES.get(key, key)
        values = [x.strip() for x in line[first_value:].split(' ') if x]
        analysis = None
        if name in cannabinoids:
            analysis = 'cannabinoids'
        elif name in terpenes:
            analysis = 'terpenes'
        results.append({
            'analysis': analysis,
            'key': key,
            'name': name,
            'dilution': convert_to_numeric(values[0]),
            'lod': convert_to_numeric(values[1]),
            'value': convert_to_numeric(values[2]),
            'units': 'percent',
        })

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
    obs = {**TERPLIFE_LABS, **obs}
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
    from dotenv import dotenv_values

    # [ ] TEST: Identify LIMS.
    parser = CoADoc(lims={'TerpLife Labs': TERPLIFE_LABS})
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229%20TLMB0216202301.pdf'
    # lims = parser.identify_lims(doc)
    # assert lims == 'TerpLife Labs'

    # [ ] TEST: Parse a full-panel COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229 TLMB0216202301.pdf'
    # coa_data = parse_terplife_coa(parser, doc)


    # [ ] TEST: Parse a cannabinoid and terpene COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU310823-2327TT.pdf'

    # [ ] TEST: Parse a R&D COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU180222-6925CKC.pdf'


    # [ ] TEST: Parse a COA that requires OCR.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU090222-9534DD.pdf'


    # [ ] TEST: Parse a cannabinoid-only COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/36782.pdf'


    # Parse all COAs in a directory.
    all_data = []
    pdf_dir = 'D:/data/florida/lab_results/.datasets/pdfs/terplife'
    pdfs = [os.path.join(pdf_dir, x) for x in os.listdir(pdf_dir) if x.endswith('.pdf')]
    start = datetime.now()
    for pdf in pdfs:
        # try:
        coa_data = parse_terplife_coa(parser, pdf, verbose=True)
        all_data.append(coa_data)
        print('Parsed:', pdf)
        # except:
        #     print('Error:', pdf)

    # Calculate parsing statistics.
    end = datetime.now()
    print('Parsed %i of %i COAs.' % (len(all_data), len(pdfs)))
    print('Total Parsing Time:', end - start)
    print('Average Parsing Time per COA:', (end - start) / len(all_data))

    # Analyze the data.
    df = pd.DataFrame(all_data)
    print(df['product_size'].unique())

    # Save the data.
    timestamp = datetime.now().strftime('%Y-%m-%d')
    outfile = f'D:/data/florida/lab_results/.datasets/terplife-labs-coa-data{timestamp}.xlsx'
    parser.save(df, outfile)
    print('Saved %i lab results to %s' % (len(df), outfile))
    


    # === DEV === 

    # # Initialize the parser.
    # parser = CoADoc()

    # # Get the front page text.
    # report = pdfplumber.open(doc)
    # front_page = report.pages[0]
    # front_page_text = report.pages[0].extract_text()

    # # Clean extraneous text from the front page.
    # extras = [
    #     'Unless otherwise stated all quality control samples',
    #     ' performed within specifications established by the Laboratory.'
    # ]
    # front_page_text = front_page_text.split('The data contained')[0]
    # for extra in extras:
    #     front_page_text = front_page_text.replace(extra, '')
    # print(front_page_text)

    # # Process the text.
    # front_page_text = front_page_text.replace('█', '\n')    
    # lines = front_page_text.split('\n')
    # lines = [x for x in lines if x != '']

    # # Optional: Initialize Firebase.
    # try:
    #     from cannlytics import firebase
    #     from firebase_admin import get_app
    #     firebase.initialize_firebase()
    #     app = get_app()
    #     bucket_name = f'{app.project_id}.appspot.com'
    # except:
    #     pass

    # # Save the product image.
    # try:
    #     image_index, _ = max(
    #         enumerate(front_page.images[image_starting_index:image_ending_index]),
    #         key=lambda img: img[1]['width'] * img[1]['height']
    #     )
    #     image_data = parser.get_pdf_image_data(front_page, image_index=image_index + image_starting_index)
    #     image_filename = doc.split('/')[-1].replace('.pdf', '.png')
    #     image_file = os.path.join(image_dir, image_filename)
    #     parser.save_image_data(image_data, image_file)
    #     image_ref = f'data/lab_results/images/terplife/{image_filename}'
    #     firebase.upload_file(image_ref, image_file, bucket_name=bucket_name)
    #     image_url = firebase.get_file_url(image_ref, bucket_name=bucket_name)
    #     obs['image_url'] = image_url
    # except:
    #     obs['image_url'] = None


    # # TODO: Handle different length pages.
    # number_of_pages = len(report.pages)


    # === Parse with AI ===
    from openai import OpenAI
    from dotenv import dotenv_values


    # Instructional prompt.
    INSTRUCTIONAL_PROMPT = 'Return JSON.'

    
    # Prompt to parse metadata from the first page.
    COA_PROMPT = """Given text, extract any of the following fields you see as JSON. Fields:

    | Field | Example | Description |
    |-------|---------|-------------|
    | `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
    | `status` | "pass" | The overall pass, fail, or N/A status for pass / fail analyses.   |
    | `methods` | [{"analysis: "cannabinoids", "method": "HPLC"}] | The methods used for each analysis. |
    | `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
    | `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
    | `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
    | `lab` | "MCR Labs" | The lab that tested the sample. |
    | `lab_address` | "85 Speen St, Framingham, MA 01701" | The lab's address. |
    | `lab_street` | "85 Speen St" | The lab's street. |
    | `lab_city` | "Framingham" | The lab's city. |
    | `lab_state` | "MA" | The lab's state. |
    | `lab_zipcode` | "01701" | The lab's zipcode. |
    | `distributor` | "Fred's Dispensary" | The name of the product distributor, if applicable. |
    | `distributor_address` | "420 State Ave, Olympia, WA 98506" | The distributor address, if applicable. |
    | `distributor_street` | "420 State Ave" | The distributor street, if applicable. |
    | `distributor_city` | "Olympia" | The distributor city, if applicable. |
    | `distributor_state` | "WA" | The distributor state, if applicable. |
    | `distributor_zipcode` | "98506" | The distributor zip code, if applicable. |
    | `distributor_license_number` | "L-123" | The distributor license number, if applicable. |
    | `producer` | "Grow House" | The producer of the sampled product. |
    | `producer_address` | "3rd & Army, San Francisco, CA 55555" | The producer's address. |
    | `producer_street` | "3rd & Army" | The producer's street. |
    | `producer_city` | "San Francisco" | The producer's city. |
    | `producer_state` | "CA" | The producer's state. |
    | `producer_zipcode` | "55555" | The producer's zipcode. |
    | `producer_license_number` | "L2Calc" | The producer's license number. |
    | `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
    | `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
    | `product_type` | "flower" | The type of product. |
    | `batch_number` | "Order-0001" | A batch number for the sample or product. |
    | `traceability_ids` | ["1A4060300002199000003445"] | A list of relevant traceability IDs. |
    | `product_size` | 2000 | The size of the product in milligrams. |
    | `serving_size` | 1000 | An estimated serving size in milligrams. |
    | `servings_per_package` | 2 | The number of servings per package. |
    | `sample_weight` | 1 | The weight of the product sample in grams. |
    | `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
    | `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
    | `total_thc` | 14.00 | The analytical total of THC and THCA. |
    | `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
    | `total_terpenes` | 0.42 | The sum of all terpenes measured. |
    | `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, try to parse the `strain_name` from the `product_name`. |
    """

    # Prompt used to parse results from all pages.
    RESULTS_PROMPT = """Given text, extract JSON. Extract only `results` as a list of JSON objects, e.g.:

    {
        "results": [
            {
                "analysis": str,
                "key": str,
                "name": str,
                "value": float,
                "mg_g": float,
                "units": str,
                "limit": float,
                "lod": float,
                "loq": float,
                "status": str
            }
        ]
    }

    Where:

    | Field | Example| Description |
    |-------|--------|-------------|
    | `analysis` | "pesticides" | The analysis used to obtain the result. |
    | `key` | "pyrethrins" | A standardized key for the result analyte. |
    | `name` | "Pyrethrins" | The lab's internal name for the result analyte |
    | `value` | 0.42 | The value of the result. |
    | `mg_g` | 0.00000042 | The value of the result in milligrams per gram. |
    | `units` | "ug/g" | The units for the result `value`, `limit`, `lod`, and `loq`. |
    | `limit` | 0.5 | A pass / fail threshold for contaminant screening analyses. |
    | `lod` | 0.01 | The limit of detection for the result analyte. Values below the `lod` are typically reported as `ND`. |
    | `loq` | 0.1 | The limit of quantification for the result analyte. Values above the `lod` but below the `loq` are typically reported as `<LOQ`. |
    | `status` | "pass" | The pass / fail status for contaminant screening analyses. |
    """


    # Initialize OpenAI
    os.environ['OPENAI_API_KEY'] = dotenv_values('.env')['OPENAI_API_KEY']
    openai_api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI()

    # TODO: Parse TerpLife Labs COAs.

    # # Define the parsing prompt.
    # coa_prompt = COA_PROMPT
    # metadata_prompt = 'Text: ' + front_page_text + '\n\nJSON:'
    # instructional_prompt = INSTRUCTIONAL_PROMPT
    # messages = [
    #     {'role': 'system', 'content': coa_prompt},
    #     {'role': 'system', 'content': instructional_prompt},
    #     {'role': 'user', 'content': metadata_prompt},
    # ]
    # temperature = 0.0
    # user = 'cannlytics'
    # max_tokens = 4_096

    # # Prompt AI to extract COA metadata as JSON.
    # completion = client.chat.completions.create(
    #     model='gpt-4-1106-preview',
    #     messages=messages,
    #     max_tokens=max_tokens,
    #     temperature=temperature,
    #     user=user,
    # )
    # print(completion.choices[0].message)
    # usage = completion.model_dump()['usage']
    # content = completion.choices[0].message.content
    # extracted_json = content.lstrip('```json\n').rstrip('\n```')
    # extracted_data = json.loads(extracted_json)

    # # Prompt AI to extract COA results as JSON.
    # # FIXME: Get all results!
    # results_prompt = RESULTS_PROMPT
    # messages = [
    #     {'role': 'system', 'content': results_prompt},
    #     {'role': 'system', 'content': instructional_prompt},
    # ]
    # content = 'Text: ' + front_page_text #  + '\n\nList of results as JSON:'
    # messages.append({'role': 'user', 'content': content})
    # results_completion = client.chat.completions.create(
    #     model='gpt-4-1106-preview',
    #     messages=messages,
    #     max_tokens=max_tokens,
    #     temperature=temperature,
    #     user=user,
    # )
    # print(results_completion.choices[0].message)
    # usage = results_completion.model_dump()['usage']
    # content = results_completion.choices[0].message.content
    # extracted_json = content.lstrip('```json\n').rstrip('\n```')
    # extracted_data = json.loads(extracted_json)
