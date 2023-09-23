"""
Parse ACS Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 6/5/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse ACS Labs COA PDFs.

Data Points:

    ✓ id
    ✓ lab_id
    ✓ product_name
    ✓ product_type
    ✓ batch_number
    ✓ product_size
    - serving_size
    ✓ units_per_package
    ✓ sample_weight
    ✓ strain_name
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
    ✓ producer
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    ✓ distributor
    - distributor_address
    - distributor_street
    - distributor_city
    - distributor_state
    - distributor_zipcode
    - distributor_license_number
    ✓ date_collected
    ✓ date_tested
    ✓ date_received
    ✓ date_harvested
    ✓ date_packaged
    - images
    ✓ analyses
    ✓ {analysis}_status
    ✓ coa_urls
    ✓ lab_results_url
    ✓ status
    - methods
    ✓ total_products
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
import base64
from datetime import datetime
import json
import io
import os
import re
import tempfile
from typing import Any, List, Optional

# External imports.
import pandas as pd
import pdfplumber
from PIL import Image
import requests

# Internal imports.
from cannlytics import firebase
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
)


def save_image_data(image_data, image_file='image.png'):
    """Save image data to a file."""
    image_bytes = base64.b64decode(image_data)
    image_io = io.BytesIO(image_bytes)
    image = Image.open(image_io)
    image.save(image_file)


def upload_image_data(storage_ref, image_file):
    """Upload image data to Firebase Storage."""
    firebase.initialize_firebase()
    firebase.upload_file(storage_ref, image_file)


def get_rows_between_values(
        original_list,
        start: Optional[str] = '',
        stop: Optional[str] = '',
    ):
    """Get rows between two values."""
    start_index = None
    end_index = None
    for index, line in enumerate(original_list):
        if line.startswith(start) and start_index is None:
            start_index = index + 1
        elif line.startswith(stop) and start_index is not None:
            end_index = index
            break
    if start_index is not None and end_index is not None:
        return original_list[start_index:end_index]
    elif start_index is not None:
        return original_list[start_index:]
    elif end_index is not None:
        return original_list[:end_index]
    else:
        return []


def split_elements(elements: list, split_words: List[str]):
    """Split elements in a list by a list of words, extending the list."""
    cells = []
    for element in elements:
        was_split = False
        temp_cells = []
        for word_index, split_word in enumerate(split_words):
            splits = element.split(split_word)
            if len(splits) > 1:  # if the element was split
                was_split = True
                for split_index, split in enumerate(splits):
                    # if it's not the first split, add split_word back
                    if split_index != 0:
                        split = split_word + split
                    temp_cells.append(split.strip())
        if was_split:  # if the element was split by any split word
            cells.extend(temp_cells)
        else:
            cells.append(element.strip())
        # remove empty strings
        cells = [i for i in cells if i]
    return cells


# It is assumed that the lab has the following details.
ACS_LABS = {
    'coa_algorithm': 'acs.py',
    'coa_algorithm_entry_point': 'parse_acs_coa',
    'lims': 'ACS Labs',
    'url': 'https://portal.acslabcannabis.com',
    'lab': 'ACS Labs',
    'lab_license_number': 'CMTL-0003',
    'lab_image_url': 'https://global-uploads.webflow.com/630470e960f8722190672cb4/6305a2e849811b34bf18777d_Desktop%20Logo.svg',
    'lab_address': '721 Cortaro Dr, Sun City Center, FL 33573',
    'lab_street': '721 Cortaro Dr',
    'lab_city': 'Sun City Center',
    'lab_county': 'Hillsborough County',
    'lab_state': 'FL',
    'lab_zipcode': '33573',
    'lab_phone': '813-634-4529',
    'lab_email': 'info@acslabcannabis.com',
    'lab_website': 'https://www.acslabcannabis.com/',
    'lab_latitude': 27.713506,
    'lab_longitude': -82.371029,
}

# It is assumed that the COA has the following details.
ACS_LABS_COA = {
    'analyses': {
        'Potency': 'cannabinoids',
        'Terpenes': 'terpenes',
        'Pesticides': 'pesticides',
        'Heavy Metals': 'heavy_metals',
        'Pathogenic': 'microbes',
        'Microbiology (qPCR)': 'microbes',
        'Microbiology Petrifilm': 'microbes',
        'Mycotoxins': 'mycotoxins',
        'Residual Solvents': 'residuals_solvents',
        'Filth and Foreign': 'foreign_matter',
        'Total Contaminant Load': 'foreign_matter',
        'Water Activity': 'water_activity',
        'Moisture': 'moisture',
    },
    'fields': {
        'Batch Date': 'date_packaged',
        'Completion Date': 'date_tested',
        'Cultivation Facility': 'producer',
        'Cultivars': 'strain_name',
        'Initial Gross Weight': 'sample_weight',
        'Lab Batch Date': 'date_received',
        'Cultivation Date': 'date_harvested',
        # FIXME: This is getting "Cultivation Date" mixed in.
        'Lot ID': 'batch_number',
        'Net Weight per Unit': 'product_size',
        'Number of Units': 'units_per_package',
        'Order #': 'lab_id',
        'Order Date': 'date_received',
        'Production Date': 'date_harvested',
        'Production Facility': 'distributor',
        'Sample #': 'id',
        'Sampling Date': 'date_collected',
        # 'Sampling Method': 'method_sampling',
        'Seed to Sale #': 'traceability_id',
        'Total Number of Final Products': 'total_products',
        'FL License #': 'lab_license_number',
        'Test Reg State': 'producer_state',
    },
}


def parse_acs_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        coa_parameters: Optional[dict] = ACS_LABS_COA,
        session: Optional[Any] = None,
        headers: Optional[dict] = DEFAULT_HEADERS,
        **kwargs,
    ) -> dict:
    """Parse a ACS Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """

    # Get the lab's parameters.
    obs = {}
    analyses, methods, results = [], [], []
    lab_analyses = coa_parameters['analyses']
    lab_fields = coa_parameters['fields']

    # If the `doc` is a URL, then download the PDF to the `temp_path`.
    # Then use the path of the downloaded PDF as the doc.
    if isinstance(doc, str):
        if doc.startswith('https'):
            if temp_path is None: temp_path = tempfile.gettempdir()
            if not os.path.exists(temp_path): os.makedirs(temp_path)
            try:
                filename = doc.split('/')[-1].split('?')[0] + '.pdf'
            except:
                filename = 'coa.pdf'
            coa_pdf = os.path.join(temp_path, filename)
            if session is not None:
                response = session.get(doc)
            else:
                response = requests.get(doc, headers=headers)
            with open(coa_pdf, 'wb') as pdf:
                pdf.write(response.content)
            report = pdfplumber.open(coa_pdf)
            obs['coa_pdf'] = filename
        else:
            report = pdfplumber.open(doc)
            obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the front page.
    page = report.pages[0]
    page_text = page.extract_text().replace(r'\u0000', '')
    lines = page_text.split('\n')
    left = page.within_bbox((0, 0, page.width * 0.5, page.height))
    right = page.within_bbox((page.width * 0.5, 0, page.width, page.height))
    rows = left.extract_text().split('\n') + right.extract_text().split('\n')

    # Get the lab results URL from the QR code.
    coa_url = parser.find_pdf_qr_code_url(page)
    if coa_url is None and doc.startswith('https'):
        coa_url = doc
    obs['lab_results_url'] = coa_url

    # Format the `coa_urls`.
    if coa_url is not None:
        filename = coa_url.split('/')[-1].split('?')[0] + '.pdf'
        obs['coa_urls'] = json.dumps([{'url': coa_url, 'filename': filename}])

    # Get the product name.
    obs['product_name'] = lines[0]

    # Get the product type.
    top_corner = page.within_bbox((page.width * 0.25, 0, page.width, page.height * 0.25))
    top_lines = top_corner.extract_text().replace('\x00', 'fi').split('\n')
    top_lines = get_rows_between_values(
        top_lines,
        start='Sample Matrix',
        stop='Certificate of Analysis'
    )
    obs['product_type'] = ' '.join(top_lines)

    # Get sample detail fields.    
    names = list(lab_fields.keys())
    for name, key in lab_fields.items():
        if name.endswith('Date'):
            values = re.findall(rf"{name}:\s+([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})", page_text)
        else:
            values = re.findall(rf"{name}:\s+(.*)", page_text)
            if not values:
                values = re.findall(rf"{name}\s+(.*)", page_text)
                if not values:
                    values = re.findall(rf"{name}:+(.*)", page_text)
        if values:
            for n in names:
                if n != name and n in values[0]:
                    values = values[0].split(n)
            obs[key] = values[0]

    # TODO: Augment producer / distributor data.
    # - producer_address
    # - producer_street
    # - producer_city
    # - producer_state
    # - producer_zipcode
    # - producer_license_number (augment)

    # Get the analyses and statuses.
    tests = 'Potency' + page_text.split('Potency')[1].split('Product Image')[0]
    tests = tests.replace('Not Tested', 'NT')
    for k, v in lab_analyses.items():
        tests = tests.replace('\x00', 'fi').replace(k, v)
    tests = [x.split(' ') for x in tests.split('\n') if x]

    # Determine status for each analysis.
    overall_status = 'Pass'
    for index, sublist in enumerate(tests):
        if index % 2 == 0:
            analyses.extend(sublist)
        else:
            test_types = analyses[-len(sublist):]
            for k, test_types in enumerate(test_types):
                status = sublist[k].replace('Passed', 'Pass').replace('Failed', 'Fail')
                obs[f'{test_types}_status'] = status
                if 'fail' in status.lower():
                    overall_status = 'Fail'
    obs['status'] = overall_status
    analyses = list(set(analyses))

    # Get total cannabinoids.
    crop = page.within_bbox((0.5 * page.width, 0.33 * page.height, page.width, page.height * 0.8))
    cells = crop.extract_text().split('\n')
    for i, cell in enumerate(cells):

        # Get total THC and CBD.
        if cell.startswith('Total THC') or cell.startswith('Total Active THC'):
            line = cells[i + 1]
            line = line.replace('Not Detected', 'ND') \
                .replace('None Detected', 'ND') \
                .replace('-', 'ND')
            values = line.split(' ')
            obs['total_thc'] = convert_to_numeric(values[0], strip=True)
            obs['total_cbd'] = convert_to_numeric(values[-2], strip=True)
        
        # Get total cannabinoids.
        if cell.startswith('Other Cannabinoids'):
            line = cells[i + 1]
            line = line.replace('Not Detected', 'ND') \
                .replace('None Detected', 'ND') \
                .replace('-', 'ND')
            values = line.split(' ')
            obs['total_cannabinoids'] = convert_to_numeric(values[-2], strip=True)

        # Get total terpenes.
        if cell.startswith('Total Terpenes'):
            value = convert_to_numeric(cell.split(' ')[-1], strip=True)
            obs['total_terpenes'] = value
            break

    # Get cannabinoids.
    crop = page.within_bbox((0, 0.4 * page.height, page.width * 0.5, page.height * 0.8))
    cells = crop.extract_text().split('\n')
    if 'Potency' in page_text:
        stop = 'Sample Prepared By' if 'Sample Prepared By' in page_text else 'Total'
        elements = get_rows_between_values(
            rows,
            start='Analyte',
            stop=stop,
        )
        for line in elements[1:]:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'cannabinoids',
                'key': key,
                'lod': convert_to_numeric(values[1]),
                'loq': convert_to_numeric(values[2]),
                'name': name,
                'units': 'percent',
                'value': convert_to_numeric(values[-1]),
                'mg_g': convert_to_numeric(values[-2]),
            })

    # Get heavy metals (flower).
    if 'Arsenic' in page.extract_text():
        elements = get_rows_between_values(
            cells,
            start='Analyte LOD',
            stop='Prep. By',
        )
        elements = split_elements(elements, ['Lead', 'Mercury'])
        for line in elements[1:]:
            first_value = find_first_value(line, [' \d+', 'ND', '<', ' .'])
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'heavy_metals',
                'key': key,
                'lod': convert_to_numeric(values[1]),
                'loq': convert_to_numeric(values[2]),
                'limit': convert_to_numeric(values[3]),
                'name': name,
                'units': 'ppb',
                'value': convert_to_numeric(values[-1]),
            })

    # Get terpene summary in case there are no terpene results later.
    terpenes_collected = []
    if 'Patient COA' in page_text:
        crop = page.within_bbox((page.width * 0.5, 0.4 * page.height, page.width, page.height * 0.8))
        cells = crop.extract_text().split('\n')
        elements = get_rows_between_values(
            cells,
            start='Analyte',
            stop='Total Terpenes',
        )
        for line in elements:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'units': 'percent',
                'value': convert_to_numeric(values[-1], strip=True),
                'mg_g': convert_to_numeric(values[0], strip=True),
            })
            terpenes_collected.append(key)

    # Get results.
    for page in report.pages[1:]:
        
        # Get page rows from the double column layout.
        page_text = page.extract_text().replace(r'\u0000', '')
        left = page.within_bbox((0, 0, page.width * 0.5, page.height))
        right = page.within_bbox((page.width * 0.5, 0, page.width, page.height))
        rows = left.extract_text().replace(r'\u0000', '').split('\n')
        rows += right.extract_text().replace(r'\u0000', '').split('\n')

        # Handle wide first column for mycotoxins.
        if 'Mycotoxins' in page_text and 'Prep. By' in page_text:
            left = page.within_bbox((0, 0, page.width * 0.5725, page.height))
            right = page.within_bbox((page.width * 0.5725, 0, page.width, page.height))
            rows = left.extract_text().split('\n') + right.extract_text().split('\n')

        # Get residual solvents (concentrates).
        # FIXME: Test on recent COAs.
        if 'Residual Solvents' in page_text:
            q3 = page.within_bbox((page.width * .5, 0, page.width * .72, page.height))
            q4 = page.within_bbox((page.width * .71, 0, page.width, page.height))
            texts = '\n'.join([q3.extract_text(), q4.extract_text()])
            cells = texts.split('\n')
            elements = get_rows_between_values(
                cells,
                start='Analyte',
                stop='Lab Batch #',
            )
            set1 = get_rows_between_values(
                elements,
                stop='Sample Prepared By',
            )
            set2 = get_rows_between_values(
                elements,
                start='Analyte (1:n)',
                stop='Sample Analyzed By',
            )
            table = [x for x in set1 + set2 if len(x.split(' ')) > 1]
            for line in table:
                if line.startswith('1,'):
                    line = line.replace('- ', '-Dichloroethane ')
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'residual_solvents',
                    'key': key,
                    'name': name,
                    'units': 'ppm',
                    'loq': convert_to_numeric(values[-3]),
                    'limit': convert_to_numeric(values[-2]),
                    'value': convert_to_numeric(values[-1]),
                })

        # Get microbes.
        if 'Pathogenic' in page_text:
            first_stop = 'Reviewed By' if 'Reviewed By' in page_text else 'Batch Reviewed By'
            stop = 'Prep. By' if 'Prep. By' in page_text else 'Sample Prepared By'
            elements = get_rows_between_values(
                get_rows_between_values(rows, start='Pathogenic', stop=first_stop),
                start='Analyte',
                stop=stop,
            )
            elements = [x.replace('\x00', 'fl') for x in elements if len(x.split(' ')) > 1]
            elements = split_elements(elements, ['Aspergillus', 'Salmonella', 'STEC'])
            elements = [x.replace('Absence in 1g', 'ND') \
                .replace('Absence in 1 g', 'ND') \
                .replace('Absence', 'ND') \
                .replace('in 1 g', 'ND') for x in elements]
            for line in elements[1:]:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) > 2:
                    continue
                results.append({
                    'analysis': 'microbes',
                    'key': key,
                    'name': name,
                    'units': 'cfu/g',
                    'value': convert_to_numeric(values[-1]),
                    'limit': convert_to_numeric(values[0]),
                })

        # Get moisture content (flower).
        if 'Moisture' in page_text:
            for row in rows:
                if row.startswith('Moisture 15'):
                    first_value = find_first_value(row)
                    name = row[:first_value].strip()
                    key = parser.analytes.get(snake_case(name), snake_case(name))
                    values = row[first_value:].strip().split(' ')
                    results.append({
                        'analysis': 'moisture',
                        'key': key,
                        'name': name,
                        'units': 'percent',
                        'value': convert_to_numeric(values[-1]),
                        'limit': convert_to_numeric(values[0]),
                    })
        
        # Get terpenes.
        if 'Terpenes' in page_text:
            elements = []
            if 'Sample Prepared By' in page_text:
                elements = get_rows_between_values(
                    rows,
                    start='Analyte Dilution',
                    stop='Sample Prepared By',
                )
            elif 'Prep. By' in page_text:
                set1 = get_rows_between_values(
                    rows,
                    start='Analyte',
                    stop='Prep. By',
                )
                set2 = get_rows_between_values(
                    get_rows_between_values(rows, start='Analyte'),
                    start='Analyte',
                    stop='Analyzed By',
                )
                elements = [x for x in set1 + set2 if len(x.split(' ')) > 1]
            for line in elements[1:]:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                if key in terpenes_collected: # Skip any terpenes collected in the summary.
                    continue
                values = line[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'terpenes',
                    'key': key,
                    'lod': convert_to_numeric(values[1]),
                    'name': name,
                    'units': 'percent',
                    'value': convert_to_numeric(values[-1]),
                })

        # Get mycotoxins.
        if 'Mycotoxins' in page_text:
            stop = 'Prep. By' if 'Prep. By' in page_text else 'Sample Prepared By'
            elements = get_rows_between_values(
                rows,
                start='Mycotoxins',
                stop='Batch Reviewed',
            )
            elements = get_rows_between_values(
                elements,
                start='Analyte',
                stop=stop,
            )
            elements = [x.replace('\x00', 'fl') for x in elements]
            cells = split_elements(elements, ['Aflatoxin', 'Ochratoxin'])
            for line in cells[1:]:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) > 4:
                    continue
                results.append({
                    'analysis': 'mycotoxins',
                    'key': key,
                    'lod': convert_to_numeric(values[1]),
                    'name': name,
                    'units': 'ppb',
                    'value': convert_to_numeric(values[-1]),
                    'limit': convert_to_numeric(values[-2]),
                })

        # Get heavy metals.
        if 'Arsenic' in page_text:
            stop = 'Prep. By' if 'Prep. By' in page_text else 'Sample Prepared By'
            elements = get_rows_between_values(
                rows,
                start='Heavy Metals',
                stop='Batch Reviewed',
            )
            elements = get_rows_between_values(
                elements,
                start='Analyte',
                stop=stop,
            )
            cells = split_elements(elements, ['Lead', 'Mercury'])
            for line in cells[1:]:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'heavy_metals',
                    'key': key,
                    'lod': convert_to_numeric(values[0]),
                    'name': name,
                    'units': 'ppb',
                    'value': convert_to_numeric(values[-1]),
                    'limit': convert_to_numeric(values[1]),
                })

        # Get pesticides.
        if 'Pesticides' in page_text:
            if 'Sample Prepared By' in page_text:
                q1 = page.within_bbox((0, 0, page.width * 0.27, page.height))
                q2 = page.within_bbox((page.width * 0.27, 0, page.width * 0.5, page.height))
                texts = '\n'.join([q1.extract_text(), q2.extract_text()])
                texts = texts.replace('\x00', 'fl')
                cells = texts.split('\n')
                elements = get_rows_between_values(
                    cells,
                    start='Analyte',
                    stop='Batch Reviewed By',
                )
                set1 = get_rows_between_values(
                    elements,
                    stop='Sample Prepared By',
                )
                set2 = get_rows_between_values(
                    elements,
                    start='Analyte',
                    stop='Sample Analyzed By',
                )
                table = [x for x in set1 + set2 if len(x.split(' ')) > 1]
            else:
                set1 = get_rows_between_values(
                    rows,
                    start='Analyte',
                    stop='Prep. By',
                )
                set2 = get_rows_between_values(
                    get_rows_between_values(rows, start='Prep. By', stop='Lab Batch #'),
                    start='Analyte',
                    stop='Analyzed By',
                )
                elements = [x.replace('\x00', 'fl') for x in set1 + set2 if len(x.split(' ')) > 1]
                table = [x for x in elements if '(ppb)' not in x]
            for line in table:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) < 3:
                    continue
                results.append({
                    'analysis': 'pesticides',
                    'key': key,
                    'name': name,
                    'units': 'ppb',
                    'loq': convert_to_numeric(values[1]),
                    'limit': convert_to_numeric(values[2]),
                    'value': convert_to_numeric(values[-1]),
                })

        # Get foreign matter.
        if 'Filth and Foreign Material' in page_text:
            stop = 'Prep. By' if 'Prep. By' in page_text else 'Sample Prepared By'
            elements = get_rows_between_values(
                rows,
                start='Filth and Foreign Material',
                stop='Batch Reviewed',
            )
            elements = get_rows_between_values(
                elements,
                start='Analyte',
                stop=stop,
            )
            split_words = ['Weight']
            cells = split_elements(elements, split_words)
            for line in cells[1:]:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'foreign_matter',
                    'key': key,
                    'name': name,
                    'units': 'percent',
                    'value': convert_to_numeric(values[-1]),
                    'limit': convert_to_numeric(values[0]),
                })

        # Get water activity.
        if 'Water Activity' in page_text:
            for row in rows:
                if row.startswith('Water Activity 0.65'):
                    first_value = find_first_value(row)
                    name = row[:first_value].strip()
                    key = parser.analytes.get(snake_case(name), snake_case(name))
                    values = row[first_value:].strip().split(' ')
                    results.append({
                        'analysis': 'water_activity',
                        'key': key,
                        'name': name,
                        'units': 'aw',
                        'value': convert_to_numeric(values[-1]),
                        'limit': convert_to_numeric(values[0]),
                    })

        # Get total yeast and mold.
        if 'Total Yeast and Mold' in page_text:
            for row in rows:
                if row.startswith('Total Yeast/Mold'):
                    first_value = find_first_value(row)
                    name = row[:first_value].strip()
                    key = parser.analytes.get(snake_case(name), snake_case(name))
                    values = row[first_value:].strip().split(' ')
                    status = values[-1].replace('Passed', 'Pass').replace('Failed', 'Fail')
                    result = {
                        'analysis': 'microbe',
                        'key': key,
                        'name': name,
                        'units': 'CFU/g',
                        'value': convert_to_numeric(status),
                        'status': status,
                        'limit': convert_to_numeric(values[0]),
                    }
                    if len(values) == 3:
                        result['value'] = convert_to_numeric(values[-2])
                    results.append(result)

    # Optional: Get the image data.

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
    obs = {**ACS_LABS, **obs}
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['methods'] = json.dumps(methods)
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(obs['results'])
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


# === Tests ===
if __name__ == '__main__':

    # Initialize CoADoc.
    from cannlytics.data.coas import CoADoc
    from time import sleep
    parser = CoADoc()

    # [✓] TEST: Identify LIMS from a COA URL.
    url = 'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFQzc0OS0wMTA1MjMtU0dMQzEyLVIzNS0wMjIxMjAyMw=='
    lims = parser.identify_lims(url, lims={'ACS Labs': ACS_LABS})
    assert lims == 'ACS Labs'
    print('Identified LIMS:', lims)

    # [✓] TEST: Identify LIMS from a COA PDF.
    parser = CoADoc()
    doc = '../../../../tests/assets/coas/acs/AAEC749-010523-SGLC12-R35-02212023-COA_EN.pdf'
    lims = parser.identify_lims(doc, lims={'ACS Labs': ACS_LABS})
    assert lims == 'ACS Labs'
    print('Identified LIMS:', lims)

    # [✓] TEST: Parse partial COA.
    doc = '../../../../tests/assets/coas/acs/AAEC749-010523-SGLC12-R35-02212023-COA_EN.pdf'
    data = parse_acs_coa(parser, doc)
    assert data is not None
    print('Parsed:', data)

    # [✓] TEST: Parse full panel COA for a concentrate.
    doc = '../../../../tests/assets/coas/acs/27675_0002407047.pdf'
    data = parse_acs_coa(parser, doc)
    assert data is not None
    print('Parsed:', data)

    # [✓] TEST: Parse a full panel COA for a flower.
    doc = '../../../../tests/assets/coas/acs/49448_0004136268.pdf'
    data = parse_acs_coa(parser, doc)
    assert data is not None
    print('Parsed:', data)

    # [✓] TEST: Parse partial COA from a URL.
    urls = [
        'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEVjIxMC0xMDI1MjItREJGSy1SMzUtMTIxMTIwMjI=',
        'https://www.trulieve.com/files/lab-results/18362_0003059411.pdf',
    ]
    for url in urls:
        data = parse_acs_coa(parser, url)
        assert data is not None
        print('Parsed:', data)
        sleep(3)

    # [✓] TEST: Parse a full panel COA from a URL.
    urls = [
        'https://www.trulieve.com/files/lab-results/27675_0002407047.pdf',
    ]
    for url in urls:
        data = parse_acs_coa(parser, url)
        assert data is not None
        print('Parsed:', data)
        sleep(3)

"""
# EXAMPLE: Parse a folder of ACS labs COAs.

from datetime import datetime
import os
import pandas as pd
from cannlytics.data.coas import CoADoc

# Initialize CoADoc.
parser = CoADoc()

# Specify where your ACS Labs COAs live.
all_data = []
data_dir = 'D://data/florida/lab_results/.datasets/pdfs/acs'
coa_pdfs = os.listdir(data_dir)
for coa_pdf in coa_pdfs:
    filename = os.path.join(data_dir, coa_pdf)
    try:
        data = parser.parse(filename)
        all_data.extend(data)
        print('Parsed:', filename)
    except:
        print('Failed to parse:', filename)

# Save the data.
date = datetime.now().isoformat()[:19].replace(':', '-')
outfile = f'D://data/florida/lab_results/.datasets/acs-lab-results-{date}.xlsx'
df = pd.DataFrame(all_data)
df.replace(r'\\u0000', '', regex=True, inplace=True)
parser.save(df, outfile)
"""
