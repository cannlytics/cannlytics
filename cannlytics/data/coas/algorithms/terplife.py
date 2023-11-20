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
TERPLIFE_LABS_COLUMNS = {
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


def extract_text_from_region(
        page,
        region_coords,
        split_str=None,
        section_str=None,
        split_at=None,
    ):
    """Extract text from a region of a COA PDF."""
    cropped_page = page.crop(region_coords)
    text = cropped_page.extract_text()
    if split_str and section_str:
        section = text.split(split_str)[1].split(section_str)[0]
        if split_at:
            section = section.split(split_at)[-1]
        return [x for x in section.split('\n') if x]
    return text


def process_analysis_block(
        page,
        analysis_type,
        region_coords,
        split_str,
        section_str,
        units,
    ):
    """Process a block of text from a COA PDF."""
    results_lines = extract_text_from_region(page, region_coords, split_str, section_str)
    results = []
    for line in results_lines:
        result = parse_results_line(line, analysis_type, units)
        results.append(result)
    return results


def parse_results_line(line, analysis_type, units):
    """Parse a line of text from a COA PDF."""
    first_value = find_first_value(line)
    name = line[:first_value].strip()
    key = snake_case(name)
    key = ANALYTES.get(key, key)
    values = [x.strip() for x in line[first_value:].split(' ') if x]
    result = {
        'analysis': analysis_type,
        'key': key,
        'name': name,
        'units': units
    }

    # Add additional data based on analysis type
    if analysis_type in ['pesticides', 'heavy_metals']:
        result.update({
            'dilution': convert_to_numeric(values[0]),
            'limit': convert_to_numeric(values[1]),
            'lod': convert_to_numeric(values[2]),
            'value': convert_to_numeric(values[3]),
            'status': values[-1]
        })
    elif analysis_type in ['mycotoxins', 'microbials', 'foreign_matter', 'water_activity', 'moisture_content']:
        result.update({
            'limit': convert_to_numeric(values[0]),
            'value': convert_to_numeric(values[1]),
            'status': values[-1]
        })
    elif analysis_type == 'terpenes':
        result.update({
            'dilution': convert_to_numeric(values[0]),
            'lod': convert_to_numeric(values[1]),
            'value': convert_to_numeric(values[2])
        })

    return result


def process_report_pages(report, number_of_pages):
    """Process the pages of a COA PDF."""
    all_results = []
    analyses = []

    if number_of_pages > 1:
        for page in report.pages[1:]:
            text = page.extract_text()

            # Example usage for pesticides
            if 'Pesticides' in text and 'Heavy Metals & Pesticides' not in text:
                analyses.append('pesticides')
                midpoint = page.width * 0.475
                left_half_coords = (0, 0, midpoint, page.height)
                right_half_coords = (midpoint, 0, page.width, page.height * 0.75)

                # Extract and process left half of the page
                left_results = process_analysis_block(page, 'pesticides', left_half_coords, 'Status', 'LOD =', 'ppb')

                # Extract and process right half of the page
                right_results = process_analysis_block(page, 'pesticides', right_half_coords, 'Status', 'LOD =', 'ppb')

                # Combine results from both halves
                all_results.extend(left_results + right_results)
                continue
            # if 'Pesticides' in text and 'Heavy Metals & Pesticides' not in text:
            #     analyses.append('pesticides')
            #     midpoint = page.width * 0.475
            #     results = process_analysis_block(page, 'pesticides', (0, 0, midpoint, page.height), 'Status', 'LOD =', 'ppb')
            #     all_results.extend(results)

            # Add similar blocks for other analysis types

    return analyses, all_results


def process_line_for_front_page(line, analytes, cannabinoids, terpenes):
    """Process a line of text from the front page of a COA PDF."""
    first_value = find_first_value(line)
    name = line[:first_value].strip()
    if name in analytes:
        return []
    key = snake_case(name)
    key = ANALYTES.get(key, key)
    values = [x.strip() for x in line[first_value:].split(' ') if x]
    if len(values) == 2:
        values.insert(0, None)
    analysis = None
    if name in cannabinoids:
        analysis = 'cannabinoids'
    elif name in terpenes:
        analysis = 'terpenes'
    return [{
        'analysis': analysis,
        'key': key,
        'name': name,
        'dilution': convert_to_numeric(values[0]),
        'lod': convert_to_numeric(values[1]),
        'value': convert_to_numeric(values[2]),
        'units': 'percent',
    }]


def initialize_paths(temp_path, image_dir):
    if temp_path is None:
        temp_path = tempfile.gettempdir()
    if image_dir is None:
        image_dir = tempfile.gettempdir()
    return temp_path, image_dir


def read_pdf(doc, temp_path):
    """Read a COA PDF."""
    if doc.startswith('https'):
        coa_pdf = download_file_from_url(doc, temp_path, ext='.pdf')
        return pdfplumber.open(coa_pdf)
    else:
        return pdfplumber.open(doc)


def apply_ocr_if_needed(doc, report, verbose, temp_path):
    """Apply OCR when necessary."""
    front_page_text = report.pages[0].extract_text()
    if front_page_text:
        return front_page_text, False

    if verbose:
        print('Applying OCR.')
    temp = tempfile.mkstemp('.pdf')[1]
    parser.pdf_ocr(doc, temp, temp_path=temp_path)
    report = pdfplumber.open(temp)
    front_page_text = report.pages[0].extract_text()
    return front_page_text, True


def clean_front_page_text(front_page_text):
    """Clean extraneous text from the front page of a COA PDF."""
    extras = [
        'Unless otherwise stated all quality control samples',
        ' performed within specifications established by the Laboratory.'
    ]
    text = front_page_text.split('The data contained')[0]
    for extra in extras:
        text = text.replace(extra, '')
    return text


def extract_front_page_data(front_page):
    """Extract the data from the front page of a COA PDF."""
    front_page_text = front_page.extract_text()
    lines = front_page_text.replace('█', '\n').split('\n')
    return [line for line in lines if line]


def save_to_firebase_if_needed(save_to_firebase, doc, image_dir, front_page, obs):
    """Save the product image and COA to Firebase Storage."""
    if not save_to_firebase:
        return
    

def find_analyses(front_page_text):
    analyses = []
    if 'Potency Summary' in front_page_text:
        analyses.append('cannabinoids')
    # Add other analysis types here...
    return analyses


def extract_producer_address(front_page):
    """Extract the producer's address from the front page of a COA PDF."""
    corner = (0, 0, front_page.width / 3, front_page.height / 4)
    top_corner = front_page.crop(corner)
    address_text = top_corner.extract_text()
    address_text = address_text.split('Client Lic#:')[-1].split('\n', maxsplit=1)[-1]
    phone_pattern = r'\(\d{3}\) \d{3}-\d{4}'
    address = re.split(phone_pattern, address_text, maxsplit=1)[0].strip().replace('\n', ' ')
    return parse_address(address)


def extract_product_details(lines, columns):
    """Extract product details from the front page of a COA PDF."""
    obs = {}
    for key, column in columns.items():
        for line in lines:
            if key in line:
                obs[column] = extract_detail_from_line(line, key, columns.keys())
                break
    return obs


def extract_total_compounds(front_page_text, lines):
    """Extract total terpenes, THC, CBD, and/or cannabinoids from the front page of a COA PDF."""
    # Extract total terpenes.
    compounds = {}
    if 'Terpenes Summary' in front_page_text:
        # analyses.append('terpenes')
        for line in lines:
            if 'Total Terpenes' in line:
                value = line.split('Total Terpenes')[-1].strip().split(' ')[0]
                compounds['total_terpenes'] = convert_to_numeric(value)
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
                compounds['total_thc'] = convert_to_numeric(values[0])
                compounds['total_cbd'] = convert_to_numeric(values[1])
                compounds['total_cannabinoids'] = convert_to_numeric(values[2])
                compounds['total_thc_wet'] = convert_to_numeric(values[3])
                compounds['total_cbd_wet'] = convert_to_numeric(values[4])
                compounds['total_cannabinoids_wet'] = convert_to_numeric(values[5])
            elif len(values) == 3:
                compounds['total_thc'] = convert_to_numeric(values[0])
                compounds['total_cbd'] = convert_to_numeric(values[1])
                compounds['total_cannabinoids'] = convert_to_numeric(values[2])
            elif len(values) >= 2:
                compounds['total_thc'] = convert_to_numeric(values[0])
                compounds['total_cbd'] = convert_to_numeric(values[1])
            break
    return compounds


def process_coa_pdf(
        doc,
        temp_path=None,
        image_dir=None,
        save_to_firebase=False,
        verbose=False,
        columns=None,
    ):
    """Parse a TerpLife Labs COA PDF."""
    if columns is None:
        columns = TERPLIFE_LABS_COLUMNS
    temp_path, image_dir = initialize_paths(temp_path, image_dir)
    report = read_pdf(doc, temp_path)
    front_page_text, parsed_with_ocr = apply_ocr_if_needed(doc, report, verbose, temp_path)
    front_page_text = clean_front_page_text(front_page_text)
    lines = extract_front_page_data(report.pages[0])
    save_to_firebase_if_needed(save_to_firebase, doc, image_dir, report.pages[0], obs)
    analyses = find_analyses(front_page_text)
    address = extract_producer_address(report.pages[0])
    product_details = extract_product_details(lines, columns)
    total_compounds = extract_total_compounds(front_page_text, lines)
    obs = {**address, **product_details, **total_compounds}
    obs['parsed_with_ocr'] = parsed_with_ocr
    return obs


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
            if 'Pesticides' in text and 'Heavy Metals & Pesticides' not in text:
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
    # FIXME: Read page half by half.
    # Extract the results on the front page.
    midpoint = front_page.width * 0.5
    left_half = (0, 0, midpoint, front_page.height)
    right_half = (midpoint, 0, front_page.width, front_page.height)
    left_lines = extract_text_from_region(front_page, left_half)
    left_results = []
    for line in left_lines:
        if 'Total' in line or 'Terpene results are' in line:
            continue
        left_results.extend(process_line_for_front_page(line, analytes, cannabinoids, terpenes))

    # Process the right half
    right_lines = extract_text_from_region(front_page, right_half)
    right_results = []
    for line in right_lines:
        if 'Total' in line or 'Terpene results are' in line:
            continue
        right_results.extend(process_line_for_front_page(line, analytes, cannabinoids, terpenes))

    # Combine results from both halves
    front_page_results = left_results + right_results
    # if 'Terpenes Summary' in front_page_text:
    #     results_text = front_page_text.split('Terpenes Summary')[-1].split('Terpenes Summary')[0]
    #     results_lines = results_text.split('Analyte Dilution')[-1].replace('Total', '\nTotal').split('\n')[2:]
    # else:
    #     results_text = front_page_text.split('Result\n')[-1].split('Total THC')[0]
    #     results_lines = results_text.split('\n')[1:]
    # results_lines = [x.strip() for x in results_lines if x.strip()]
    # for line in results_lines:

    #     # Skip totals.
    #     if 'Total Terpenes' in line:
    #         break
    #     elif 'Total THC' in line or 'Total CBD' in line:
    #         continue
    #     if 'Total Cannabinoids' in line and 'Terpenes Summary' in front_page_text:
    #         continue
    #     elif 'Total Cannabinoids' in line:
    #         break
    #     elif 'Terpene results are' in line:
    #         break

    #     # Extract a result, if not already extracted.
    #     first_value = find_first_value(line)
    #     name = line[:first_value].strip()
    #     if name in analytes:
    #         continue
    #     key = snake_case(name)
    #     key = ANALYTES.get(key, key)
    #     values = [x.strip() for x in line[first_value:].split(' ') if x]
    #     if len(values) == 2:
    #         values.insert(0, None)
    #     analysis = None
    #     if name in cannabinoids:
    #         analysis = 'cannabinoids'
    #     elif name in terpenes:
    #         analysis = 'terpenes'
    #     results.append({
    #         'analysis': analysis,
    #         'key': key,
    #         'name': name,
    #         'dilution': convert_to_numeric(values[0]),
    #         'lod': convert_to_numeric(values[1]),
    #         'value': convert_to_numeric(values[2]),
    #         'units': 'percent',
    #     })

    # Close the report.
    report.close()

    # TODO: Calculate moisture content if possible using dry and wet
    # concentrations if the full report is not available.

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
# Tested: 2023-11-16 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc
    from dotenv import dotenv_values

    # Initialize the parser.
    parser = CoADoc(lims={'TerpLife Labs': TERPLIFE_LABS})

    # # [✓] TEST: Identify LIMS.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229 TLMB0216202301.pdf'
    # lims = parser.identify_lims(doc)
    # assert lims == 'TerpLife Labs'
    # print('Identified LIMS as', lims)

    # # [✓] TEST: Parse a full-panel COA.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229 TLMB0216202301.pdf'
    # coa_data = parse_terplife_coa(parser, doc)
    # print('Parsed full-panel COA:', doc)

    # # [✓] TEST: Parse a cannabinoid-only COA.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/36782.pdf'
    # coa_data = parse_terplife_coa(parser, doc)
    # print('Parsed cannabinoid-only COA:', doc)

    # # [✓] TEST: Parse a cannabinoid and terpene COA.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU310823-2327TT.pdf'
    # coa_data = parse_terplife_coa(parser, doc)
    # print('Parsed cannabinoid and terpene COA:', doc)

    # # [✓] TEST: Parse a R&D COA.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU180222-6925CKC.pdf'
    # coa_data = parse_terplife_coa(parser, doc)
    # print('Parsed R&D COA:', doc)

    # # [✓] TEST: Parse a COA that requires OCR.
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU090222-9534DD.pdf'
    # coa_data = parse_terplife_coa(parser, doc)
    # print('Parsed COA with OCR:', doc)

    # [ ] TEST: Parse all COAs in a directory.
    all_data = []
    pdf_dir = 'D:/data/florida/lab_results/.datasets/pdfs/terplife'
    pdfs = [os.path.join(pdf_dir, x) for x in os.listdir(pdf_dir) if x.endswith('.pdf')]
    start = datetime.now()
    for pdf in pdfs:
        # try:
        coa_data = parse_terplife_coa(
            parser, pdf,
            # save_to_firebase=True,
            verbose=True,
        )
        all_data.append(coa_data)
        print('Parsed:', pdf)
        # except Exception as e:
        #     print('Error:', pdf)
        #     print(e)
        #     break

    # Calculate parsing statistics.
    end = datetime.now()
    print('Parsed %i of %i COAs.' % (len(all_data), len(pdfs)))
    print('Total Parsing Time:', end - start)
    print('Average Parsing Time per COA:', (end - start) / len(all_data))

    # # Save the data.
    # df = pd.DataFrame(all_data)
    # timestamp = datetime.now().strftime('%Y-%m-%d')
    # outfile = f'D:/data/florida/lab_results/.datasets/terplife-labs-coa-data-{timestamp}.xlsx'
    # parser.save(df, outfile)
    # print('Saved %i lab results to %s' % (len(df), outfile))
