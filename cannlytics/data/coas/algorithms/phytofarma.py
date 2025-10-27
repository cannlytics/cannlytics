"""
Parse COAs | Phyto-Farma Labs
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
PHYTO_FARMA = {
    'coa_algorithm': 'keystone.py',
    'coa_algorithm_entry_point': 'parse_keystone_coa',
    'lims': 'Keystone State Testing',
    # TODO: Get lab details from the COA.
    'lab': 'Phyto-Farma Labs',
    'lab_street': '49 John Hicks Drive',
    'lab_city': 'Warwick',
    'lab_state': 'NY',
    'lab_zipcode': '10990',
    'lab_license_number': 'OCM-CPL-2022-00004',
    'lab_phone': '845-988-0937',
}
PHYTO_FARMA_COA = {
    'fields': {
        'Client Name': 'producer',
        'Address': 'producer_address',
        'License Number': 'producer_license_number',
        'Sample Description': 'product_name',
        'Lot Number': 'batch_number',
        'Lot #': 'batch_number',
        'Regulatory Category': 'classification',
        'Sample Matrix': 'sample_matrix',
        'Delivery Method': 'product_category',
        'Sample Type': 'product_type',
        'Sample Subtype': 'product_subtype',
        'Sampling Site': 'producer_address',
        'Sampling Date and Time': 'date_sampled',
        'Sample Collected': 'date_sampled',
        'Received': 'date_received',
        'Sample ID': 'lab_id',
        'Certificate': 'coa_id',
        'Lot Size': 'batch_size',
        'Amount Received': 'sample_size',
        'Published': 'date_tested',
        # 'Sampling Location': 'producer_address',
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


def parse_phyto_farma_coa(
        parser,
        doc: Any,
        coa_parameters: dict = PHYTO_FARMA_COA,
        **kwargs,
    ) -> dict:
    """Parse a Phyto-Farma Labs COA PDF.
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

    # Parse historic COAs.
    front_page = report.pages[0]
    if 'Phyto-farma Labs' in front_page.extract_text():
        return parse_historic_phyto_farma_coa(
            parser,
            doc,
            coa_parameters=coa_parameters,
            **kwargs,
        )
    
    # TODO: Get lab details.

    # Get producer details.
    crop = front_page.within_bbox((0, 0, front_page.width * 0.6, front_page.height * 0.15))
    lines = crop.extract_text().split('\n')
    obs['producer'] = lines[0]
    for i, line in enumerate(lines):
        for field, key in coa_parameters['fields'].items():
            if field in line:
                obs[key] = line.split(':', maxsplit=1)[-1].strip()
        
        # Get long license numbers and addresses.
        if 'License Number' in line:
            if ':' not in lines[i + 1]:
                obs['producer_license_number'] += lines[i + 1]
        elif 'Address' in line:
            if ':' not in lines[i + 1]:
                obs['producer_address'] += lines[i + 1]

    # Get the product name.
    crop = front_page.within_bbox((0, front_page.height * 0.15, front_page.width * 0.6, front_page.height * 0.33))
    lines = crop.extract_text().split('\n')
    obs['product_name'] = lines[0]
    if ':' not in lines[1]:
        obs['product_name'] += lines[1]

    # Get sample details.
    # Note: There are 2 columns.
    crop = front_page.within_bbox((0, front_page.height * 0.15, front_page.width * 0.33, front_page.height * 0.33))
    lines = crop.extract_text().split('\n')
    crop = front_page.within_bbox((front_page.width * 0.33, front_page.height * 0.15, front_page.width * 0.66, front_page.height * 0.33))
    lines += crop.extract_text().split('\n')
    for i, line in enumerate(lines):
        for field, key in coa_parameters['fields'].items():
            if line.startswith(field):
                obs[key] = line.split(':', maxsplit=1)[-1].strip()

    # Optional: Get lab results URL.
    coa_url = parser.find_pdf_qr_code_url(front_page)
    obs['lab_results_url'] = coa_url

    # TODO: Get serving_size.

    # TODO: Get analyses.

    # TODO: Get methods.

    # Get cannabinoids.
    results = []
    page = report.pages[1]
    text = page.extract_text()
    lines = text.split('\n')
    rows = extract_lines(lines, 'Analyte', '* Analyte')
    for line in rows:
        first_value = find_first_value(line)
        name = line[:first_value].strip()
        key = parser.analytes.get(snake_case(name), snake_case(name))
        values = line[first_value:].strip().split(' ')

        # Handle totals.
        if key == 'total_tetrahydrocannabinol_thc':
            obs['total_thc'] = convert_to_numeric(values[0])
            continue
        elif key == 'total_cannabidiol_cbd':
            obs['total_cbd'] = convert_to_numeric(values[0])
            continue
        elif key == 'total_cannabinoids':
            obs['total_cannabinoids'] = convert_to_numeric(values[0])
            continue
        elif key.startswith('total_active') or key.startswith('cannabinoid_totals'):
            continue
        
        # Handle normal rows.
        results.append({
            'analysis': 'cannabinoids',
            'key': key,
            'name': name,
            'loq': convert_to_numeric(values[0]),
            'value': convert_to_numeric(values[1]),
            'mg_per_serving': convert_to_numeric(values[2]),
        })

    # Get terpenes.
    page = report.pages[2]
    text = page.extract_text()
    if 'Terpenes' in text:

        # Get total terpenes.
        # Note: Uses the location of "Total Terpenes" to crop the page.
        y_position = page.height * 0.8
        words = page.extract_words()
        for i, word in enumerate(words):
            if word['text'] == 'Total' and words[i + 1]['text'] == 'Terpenes':
                y_position = word['top']
                obs['total_terpenes'] = convert_to_numeric(words[i + 2]['text'])
                break

        # Get the page in two halves.
        crop = page.within_bbox((0, 0, page.width * 0.5, y_position))
        lines = crop.extract_text().split('\n')
        rows = extract_lines(lines, 'Analyte', 'Analyzed')
        crop = page.within_bbox((page.width * 0.5, 0, page.width, y_position))
        lines = crop.extract_text().split('\n')
        rows += extract_lines(lines, 'Analyte', 'Analyzed')
        for line in rows:
            if line.startswith('Terpene Totals') or line.startswith('Pass'):
                continue
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'loq': convert_to_numeric(values[0]),
                'value': convert_to_numeric(values[1]),
            })

    # TODO: Get remaining tests.
    # - heavy_metals
    # - pesticides
    # - microbes
    # - mycotoxins
    # - residual_solvents

    # Finish data collection with a freshly minted sample ID.
    obs = {**PHYTO_FARMA, **obs}
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


def parse_historic_phyto_farma_coa(
        parser,
        doc: Any,
        coa_parameters: dict = PHYTO_FARMA_COA,
        **kwargs,
    ) -> dict:
    """Parse a Phyto-Farma Labs COA PDF.
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

    # TODO: Handle the format of older COAs.
    front_page = report.pages[0]

    # TODO: Get lab details.

    # Get sample details.
    crop = front_page.within_bbox((0, front_page.height * 0.15, front_page.width * 0.5, front_page.height * 0.75))
    lines = crop.extract_text().split('\n')
    for i, line in enumerate(lines):
        for field, key in coa_parameters['fields'].items():
            if field in line:
                obs[key] = line.split(':', maxsplit=1)[-1].strip()
        
        # Get long license numbers and addresses.
        if 'License Number' in line:
            if ':' not in lines[i + 1]:
                obs['producer_license_number'] += lines[i + 1]
        elif 'Address' in line:
            if ':' not in lines[i + 1]:
                obs['producer_address'] += lines[i + 1]
    
    # Optional: Get lab results URL.
    # coa_url = parser.find_pdf_qr_code_url(front_page)
    # obs['lab_results_url'] = coa_url
    
    # TODO: Get analyses.

    # TODO: Get methods.

    # Get the date tested.
    analysis_page = report.pages[1]
    lines = analysis_page.extract_text().split('\n')
    for line in lines:
        if 'Date analyzed' in line:
            obs['date_tested'] = line.split(':', maxsplit=1)[-1].strip().split(' ')[0]
            break

    # Get the cannabinoid results.
    results = []
    cannabinoids = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Cannabinoids Profile' in text or 'Cannabinoid Profile' in text:
            cannabinoids = True
            break
    if not cannabinoids:
        page = report.pages[1]
        text = page.extract_text()
    lines = text.split('\n')
    if 'Homogeneity' in text:
        rows = extract_lines(lines, 'Analyte', '*Pass')
        for i, line in enumerate(rows):

            # Handle lines with long analyte names.
            line = line.replace('†', '').replace('*', '')
            if line.startswith('Overall Status'):
                obs['status'] = line.split('Overall Status')[-1].strip()
                continue
            elif line.startswith('Total Cannabidiol (CBD)'):
                value = line.split('Total Cannabidiol (CBD)')[-1].strip().split(' ')[0]
                obs['total_cbd'] = convert_to_numeric(value)
                continue
            elif line.startswith('Total Tetrahydrocannabinol'):
                value = rows[i + 1].split(' ')[0]
                obs['total_thc'] = convert_to_numeric(value)
                continue
            elif line.startswith('Tetrahydrocannabinolic acid'):
                values = rows[i + 1].split(' ')
                results.append({
                    'analysis': 'cannabinoids',
                    'key': 'thca',
                    'name': 'Tetrahydrocannabinolic acid',
                    'loq': convert_to_numeric(values[-1]),
                    'value': convert_to_numeric(values[0]),
                    'mg_per_serving': convert_to_numeric(values[1]),
                })
                continue
            elif 'serving' in line:
                continue

            # Handle normal rows.
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                if isinstance(convert_to_numeric(name), (int, float)):
                    continue
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) == 1:
                    continue
                results.append({
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': name,
                    'loq': convert_to_numeric(values[-1]),
                    'value': convert_to_numeric(values[0]),
                    'mg_per_serving': convert_to_numeric(values[1]),
                    # TODO: Get std. deviation
                })

    # Older COAs.
    else:
        rows = extract_lines(lines, 'Analyte', 'Analyzed')
        rows = extract_lines(rows, None, 'Analysis')
        for line in rows:
            line = line.replace('†', '').replace('*', '')
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            if name == 'Total Tetrahydrocannabinol (THC)':
                obs['total_thc'] = convert_to_numeric(values[0])
                continue
            elif name == 'Total Cannabidiol (CBD)':
                obs['total_cbd'] = convert_to_numeric(values[0])
                continue
            elif name == 'Total Cannabinoids':
                obs['total_cannabinoids'] = convert_to_numeric(values[0])
                continue
            results.append({
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'loq': convert_to_numeric(values[1]),
                'value': convert_to_numeric(values[0]),
                'mg_per_serving': convert_to_numeric(values[-1]),
            })

    # Get the first page of terpene results.
    terpenes = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Terpenes' in text:
            terpenes = True
            break
    if terpenes:
        lines = text.split('\n')
        rows = extract_lines(lines, 'Analyte', 'Analyzed')
        rows = extract_lines(rows, None, 'This is')
        for line in rows:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            if len(values) == 1:
                continue
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'loq': convert_to_numeric(values[-1]),
                'value': convert_to_numeric(values[0]),
            })

        # Get the second page of terpene results.
        next_page = report.pages[page.page_number]
        text = next_page.extract_text()
        lines = text.split('\n')
        rows = extract_lines(lines, 'Phone', 'Analyzed')
        rows = extract_lines(rows, None, 'Analysis')
        for line in rows:
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            if len(values) == 1:
                continue
            if name == 'TOTAL':
                obs['total_terpenes'] = convert_to_numeric(values[0])
                continue
            results.append({
                'analysis': 'terpenes',
                'key': key,
                'name': name,
                'loq': convert_to_numeric(values[-1]),
                'value': convert_to_numeric(values[0]),
            })

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

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs = {**PHYTO_FARMA, **obs}
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

    # [✓] TEST: Parse current COA PDFs.
    docs = [
        'D://data/new-york\\hudson-cannabis\\pdfs\\1JljGOuXHr885wC1b4Dn1RXUozahwukPu.pdf',
        'D://data/new-york\\my-coa\\pdfs\\Blueberry Muffin x Blueberry Muffin Resin PRRBBM04.pdf',
        'D://data/new-york\\my-coa\\pdfs\\Honey Banana 510.pdf',
        'D://data/new-york\\my-coa\\pdfs\\Gelato 41 Vape Pen 510RESG41D1.pdf',
        'D://data/new-york\\my-coa\\pdfs\\Tropicana Cookies Disposable.pdf',
        'D://data/new-york\\my-coa\\pdfs\\Blueberry Oishii Gummy.pdf'
    ]
    parser = CoADoc()
    for doc in docs:
        data = parse_phyto_farma_coa(parser, doc)
        assert data is not None

    # [✓] TEST: Parse historic COA PDFs.
    docs = [
        r'D://data/new-york\jetty-extracts\pdfs\Double Frosted_JLR-DF0001 - COA - 75.09% - 2492.1.pdf',
        r'D://data/new-york\jetty-extracts\pdfs\Napa Sunrise_JLR-NS0001 - COA - 77.66% - 2491.1.pdf',
        r'D:/data/new-york/hudson-cannabis/pdfs/1Af7-SrPSWXOe8L-aHRvSU_V73LlK9oAU.pdf',
        r'D://data/new-york\hudson-cannabis\pdfs\1eIXD7mdyeaQeSgIQYUMKjX5A5v4qgzAa.pdf',
    ]
    parser = CoADoc()
    for doc in docs:
        data = parse_phyto_farma_coa(parser, doc)
        assert data is not None
