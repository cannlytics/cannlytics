"""
Parse COAs | Keystone State Testing
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/26/2024
Updated: 6/27/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Keystone State Testing COA PDFs.
"""
# Standard imports.
from datetime import datetime
import json
import re
from typing import Any, List, Optional

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics import __version__
from cannlytics.data.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
)

# It is assumed that the lab has the following details.
KEYSTONE = {
    'coa_algorithm': 'keystone.py',
    'coa_algorithm_entry_point': 'parse_keystone_coa',
    'lims': 'Keystone State Testing',
}
KEYSTONE_COA = {
    'fields': {
        'Date Collected': 'date_collected',
        'Date Received': 'date_received',
        'Date Analyzed': 'date_tested',
        'Date Released': 'date_released',
        'Report #': 'lab_id',
        'Order #': 'project_id',
        'Category/Type': 'product_type',
        'Regulator Sample ID': 'sample_id',
        'Regulator Source Package ID': 'source_id',
        'Regulator Batch ID': 'batch_number',
        'Size': 'batch_size',
    }
}


def extract_lines(
        lines: List[str],
        start_value: Optional[str] = None,
        end_value: Optional[str] = None,
    ) -> List[str]:
    """Extract lines from a list starting from a specific value and optionally ending at another value.
    
    Args:
        lines (List[str]): The list of lines to extract from.
        start_value (Optional[str]): The line to start extraction from. If None, starts from the beginning.
        end_value (Optional[str]): The line to end extraction at. If None, extracts until the end of the list.
    
    Returns:
        List[str]: The extracted lines.
    """
    start_index, end_index = 0, len(lines)
    if start_value:
        for i, line in enumerate(lines):
            if line.startswith(start_value):
                start_index = i + 1
                break
    if end_value:
        for i in range(start_index, len(lines)):
            if lines[i].startswith(end_value):
                end_index = i
                break
    return lines[start_index:end_index]


def remove_leading_numbers(lines: List[str]) -> List[str]:
    """Remove leading numbers from each line in the list.
    Args:
        lines (List[str]): The list of lines to process.
    Returns:
        List[str]: The list of lines with leading numbers removed.
    """
    return [re.sub(r'^\d+\s*', '', line) for line in lines]


def calculate_total_terpenes(results):
    """Calculate total terpenes from a list of results."""
    total = 0
    for result in results:
        if result.get('analysis') == 'terpenes':
            value = convert_to_numeric(str(result.get('value')), strip=True)
            try:
                total += value
            except:
                pass
    return total


def get_keystone_terpenes(text, compounds, results, analytes):
    lines = text.split('\n')
    rows = extract_lines(lines, '(%)', 'This product')
    rows = extract_lines(rows, None, 'Test Comment')
    rows = remove_leading_numbers(rows)
    for line in rows:
        first_value = find_first_value(line)
        name = line[:first_value].strip()
        if name == 'Results based on dry weight':
            continue
        elif name.startswith('Terpenes') or name.startswith('Compound') or name.startswith('(%)'):
            continue
        key = analytes.get(snake_case(name), snake_case(name))
        if key in compounds:
            continue
        values = line[first_value:].strip().split(' ')
        if len(values) == 1:
            loq = None
            value = convert_to_numeric(values[0])
        elif len(values) == 2:
            loq = convert_to_numeric(values[0])
            value = convert_to_numeric(values[1])
        else:
            loq = convert_to_numeric(values[1])
            value = convert_to_numeric(values[2])
        results.append({
            'analysis': 'terpenes',
            'key': key,
            'name': name,
            'loq': loq,
            'value': value,
        })
    return results


def parse_keystone_coa(
        parser,
        doc: Any,
        coa_parameters: dict = KEYSTONE_COA,
        **kwargs,
    ) -> dict:
    """Parse a Keystone State Testing COA PDF.
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

    # Get lab details (bottom left corner).
    front_page = report.pages[0]
    crop = front_page.within_bbox((0, front_page.height * 0.75, front_page.width * 0.5, front_page.height))
    lines = crop.extract_text().split('\n')
    lines = extract_lines(lines, 'If sampled', 'Page')
    if 'Keystone State Testing' not in lines[0]:
        lines = lines[1:]
    parts = lines[2].split(',')
    obs['lab'] = lines[0]
    obs['lab_street'] = lines[1]
    obs['lab_city'] = parts[0]
    obs['lab_state'] = parts[1].split(' ')[1]
    obs['lab_zipcode'] = parts[1].split(' ')[2]
    obs['lab_phone'] = lines[3]
    obs['lab_email'] = lines[4]
    obs['lab_website'] = lines[5]
    if 'License #' in lines[-2] or 'Permit #' in lines[-2]:
        obs['lab_license_number'] = lines[-2].split(':')[-1].strip()
    elif 'License #' in lines[-1] or 'Permit #' in lines[-1]:
        obs['lab_license_number'] = lines[-1].split(':')[-1].strip()

    # Get producer details (top left corner).
    crop = front_page.within_bbox((0, 0, front_page.width * 0.5, front_page.height * 0.15))
    lines = crop.extract_text().split('\n')
    obs['producer'] = lines[0]
    obs['producer_address'] = lines[1]
    if 'License #' in lines[-1]:
        obs['producer_license_number'] = lines[-1].split(':')[-1].strip()

    # Get sample details.
    # FIXME: Get IDs with long lines.
    rect = front_page.rects[0]
    crop = front_page.within_bbox((0, front_page.height * 0.15, front_page.width * 0.4, rect['top']))
    lines = crop.extract_text().split('\n')
    for i, line in enumerate(lines):
        if 'Report #' in line:
            obs['product_name'] = lines[i + 1]
            if 'Sample #' not in lines[i + 2]:
                obs['product_name'] += ' ' + lines[i + 2]
                values = lines[i + 3].split(', ')
            else:
                values = lines [i + 2].split(', ')
            obs['sample_number'] = values[0].split(':')[-1].strip()
            obs['sample_weight'] = values[1].split(':')[-1].strip()
        for field, key in coa_parameters['fields'].items():
            if field in line:
                obs[key] = line.split(':', maxsplit=1)[-1].strip()
    
    # FIXME: Get lab results URL.
    # Note: This currently causes the interpreter to crash.
    # coa_url = parser.find_pdf_qr_code_url(front_page)
    # obs['lab_results_url'] = coa_url
    
    # TODO: Get analyses.

    # TODO: Get methods.

    # Get total cannabinoids.
    crop = front_page.within_bbox((rect['x0'], rect['top'], rect['x1'], rect['bottom']))
    crop_text = crop.extract_text()
    lines = crop_text.split('\n')
    totals = ['Total Cannabinoids', 'Total THC', 'Total CBD']
    for line in lines:
        for total in totals:
            if total in line:
                value = line.split(f'{total}:')[-1].strip().split(' ')[0]
                obs[snake_case(total)] = convert_to_numeric(value)

    # Determine if it is an edible COA.
    edible = False
    if 'mg/svg' in crop_text:
        edible = True

    # Get cannabinoid results.
    results = []
    compounds = []
    if edible:
        rows = extract_lines(lines, '(mg/svg', 'Test Comment')
    else:
        rows = extract_lines(lines, '(%)', 'Test Comment')
    for row in rows:
        values = row.split(' ')
        if len(values) < 3:
            continue
        key = parser.analytes.get(snake_case(values[0]), snake_case(values[0]))
        compounds.append(key)
        if edible:
            results.append({
                'analysis': 'cannabinoids',
                'key': key,
                'name': values[0],
                'loq': convert_to_numeric(values[-3]),
                'value': convert_to_numeric(values[-1]),
                'mg_per_serving': convert_to_numeric(values[-2]),
                'mg_g': convert_to_numeric(values[-1]),
            })
        else:
            results.append({
                'analysis': 'cannabinoids',
                'key': key,
                'name': values[0],
                'loq': convert_to_numeric(values[-3]),
                'value': convert_to_numeric(values[-2]),
                'mg_g': convert_to_numeric(values[-1]),
            })

    # Get terpenes.
    terpenes = 0
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Terpenes' in text:
            # Note: If a page number is skipped between terpenes,
            # then make sure to get results from that page.
            if terpenes and terpenes != page.page_number - 1:
                page_text = report.pages[terpenes].extract_text()
                results = get_keystone_terpenes(page_text, compounds, results, parser.analytes)
            terpenes = page.page_number
            results = get_keystone_terpenes(text, compounds, results, parser.analytes)

    # Calculate total terpenes.
    if terpenes:
        obs['total_terpenes'] = calculate_total_terpenes(results)

    # TODO: Get remaining tests.
    # - heavy_metals
    # - pesticides
    # - microbes
    # - mycotoxins
    # - residual_solvents
    # - water_activity
    # - moisture_content
    # - foreign_matter
    # - etc?

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
    obs = {**KEYSTONE, **obs}
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    # obs['analyses'] = json.dumps(list(set(analyses)))
    # obs['methods'] = json.dumps(methods)
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
# Tested: 2024-06-27 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # TODO: [ ] TEST: Identify LIMS.


    # [✓] TEST: Parse a COA PDF.
    docs = [
        r'D://data/new-york\\my-coa\\pdfs\\MFNY Concentrate - Cheetah LFFCP1-001.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Flower - Apple Fritter QTRAF1.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Flower - Blueberry Muffin QTRBBM2.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Pre-Roll - Blueberry Muffin x Blueberry Muffin Resin PRRBBM2.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Live Rosin - Gazzurple LRGZP2.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Pre-Roll - Blueberry Muffin Flower_ x Strawpaya Resin Infused PRR-BBMSP1.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Disposable Vape - Poddy Mouth LRDV-PM-1.pdf',
        r'D://data/new-york\my-coa\pdfs\MFNY Gummies - Blueberry BCLRG-001.pdf',
    ]
    for doc in docs:
        parser = CoADoc()
        data = parse_keystone_coa(parser, doc)
        assert data is not None
