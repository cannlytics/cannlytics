"""
Parse Encore Labs COAs
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/2/2024
Updated: 3/3/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Data points:

    ✓ analyses
    ✓ methods
    ✓ results
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    ✓ total_terpenes
    ✓ batch_number
    ✓ metrc_batch_label
    ✓ metrc_sample_label
    ✓ lab_id
    ✓ strain_name
    ✓ strain_type
    ✓ product_name
    ✓ product_category
    ✓ product_type
    x date_produced
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    ✓ sample_size
    ✓ batch_size
    ✓ distributor
    ✓ distributor_license_number
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ producer
    ✓ producer_license_number
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ lab
    ✓ lab_license_number
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_county
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    ✓ lab_email
    ✓ lab_website
    ✓ lab_latitude
    ✓ lab_longitude

"""
# Standard imports:
from collections import OrderedDict
from datetime import datetime
import json
import os
import re
import tempfile
from time import sleep
from typing import Any, Optional

# External imports:
from cannlytics import __version__
from cannlytics.data import (
    create_hash,
    create_sample_id,
    find_first_value,
)
from cannlytics.data.web import initialize_selenium
from cannlytics.utils import (
    convert_to_numeric,
    download_file_from_url,
    snake_case,
)
from cannlytics.utils.constants import ANALYTES
import pdfplumber
from selenium.webdriver.common.by import By


# It is assumed that the lab has the following details.
ENCORE_LABS = {
    'coa_algorithm_version': 'encore.py',
    'coa_algorithm_entry_point': 'parse_encore_coa',
    'lims': 'Confident Cannabis',
    'lab': 'Encore Labs',
    'lab_address': '75 N Vinedo Ave., Pasadena, CA 91107',
    'lab_street': '75 N Vinedo Ave.',
    'lab_city': 'Pasadena',
    'lab_county': 'Los Angeles',
    'lab_state': 'CA',
    'lab_zipcode': '91107',
    'lab_license_number': 'C8-0000086-LIC',
    'lab_phone': '(626) 696-3086',
    'lab_website': 'https://encore-labs.com',
    'lab_latitude': 34.147450,
    'lab_longitude': -118.096160,
}


def list_between_values(lst, start_value, end_value):
    """
    Returns a sublist of lst that starts with the element after the first occurrence of start_value
    and ends with the element before the first occurrence of end_value. 
    This version also finds elements that start with the start_value or end_value.
    """
    start_index = None
    end_index = None
    for i, item in enumerate(lst):
        if item.startswith(start_value):
            start_index = i + 1
            break
    if start_index is not None:
        for i, item in enumerate(lst[start_index:], start=start_index):
            if item.startswith(end_value):
                end_index = i
                break
    if start_index is not None and end_index is not None and start_index < end_index:
        return lst[start_index:end_index]
    else:
        return []


def parse_encore_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        verbose: Optional[bool] = False,
        pause: Optional[float] = 3.33,
        headless: Optional[bool] = True,
        **kwargs,
    ) -> dict:
    """Parse an Encore Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Download the PDF if it's a URL.
    obs = {}
    if isinstance(doc, str):
        if doc.startswith('http'):
            if temp_path is None:
                download_dir = tempfile.mkdtemp()
            doc = doc.replace('/sample/', '/pdf/')
            driver = initialize_selenium(download_dir=download_dir, headless=headless)
            driver.get(doc)
            sleep(pause)
            button = driver.find_element(by=By.TAG_NAME, value='button')
            button.click()
            sleep(pause)
            driver.quit()
            pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
            if pdf_files:
                coa_pdf = os.path.join(download_dir, pdf_files[0])
                report = pdfplumber.open(coa_pdf)
            else:
                raise ValueError('No PDFs were found. Try increasing `pause`.')
        else:
            report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Read the lines of the PDF.
    text = ''
    for page in report.pages:
        text += page.extract_text()
    lines = text.split('\n')
    unique_lines = list(OrderedDict.fromkeys(lines))

    # Get the COA metadata.
    for line in unique_lines:
        if 'metrc batch' in line.lower():
            obs['metrc_batch_label'] = line.split(':')[-1].strip()
        elif 'metrc sample' in line.lower():
            obs['metrc_sample_label'] = line.split(':')[-1].strip().split(' ')[0]
        if 'Completed:' in line:
            obs['date_tested'] = line.split('Completed:')[1].strip().split(' ')[0]
        elif 'Received:' in line:
            obs['date_received'] = line.split('Received:')[1].strip().split(' ')[0]
        elif 'Collected:' in line:
            obs['date_collected'] = line.split('Collected:')[1].strip().split(' ')[0]
        if 'Matrix:' in line:
            obs['product_category'] = line.split(':')[1].strip().split('Completed')[0].strip()
        if 'Batch#:' in line:
            obs['batch_number'] = line.split('Batch#:')[1].strip().split(' ')[0]
        if 'Sample Size:' in line:
            value = line.split('Sample Size:')[1].strip().split(' ')[0]
            obs['sample_size'] = convert_to_numeric(value.replace(',', ''))
        if 'Batch:' in line and 'METRC' not in line:
            value = line.split('Batch:')[1].strip().split(' ')[0]
            obs['batch_size'] = convert_to_numeric(value.replace(',', ''))

        if 'Strain:' in line:
            obs['strain_name'] = line.split('Strain:')[1].split('Received:')[0].strip()
        if 'Sample ID:' in line:
            obs['lab_id'] = line.split('Sample ID:')[1].split('Collected:')[0].strip()
        if 'Matrix:' in line:
            obs['product_type'] = line.split('Matrix:')[1].split('Completed:')[0].strip()
        elif 'Type:' in line:
            obs['product_subtype'] = line.split('Type:')[1].split('Sample Size::')[0].strip()

    # Get the product name.
    obs['product_name'] = lines[5].strip()

    # Get the producer details.
    front_page = report.pages[0]
    area = (
        page.width * 0.8,
        page.height * 0.1,
        page.width * 1,
        page.height * 0.25,
    )
    crop = front_page.within_bbox(area)
    details = crop.extract_text()
    producer_lines = details.split('\n')
    obs['producer'] = producer_lines[1]
    obs['producer_license_number'] = producer_lines[2].split('#')[-1].strip()
    obs['producer_street'] = producer_lines[3]
    obs['producer_city'] = producer_lines[4].split(',')[0].strip()
    obs['producer_state'] = producer_lines[4].split(',')[1].strip().split(' ')[0]
    obs['producer_zipcode'] = producer_lines[4].split(' ')[-1].strip()

    # Get the distributor details.
    area = (
        page.width * 0.65,
        page.height * 0.1,
        page.width * 0.8,
        page.height * 0.25,
    )
    crop = front_page.within_bbox(area)
    details = crop.extract_text()
    producer_lines = details.split('\n')
    obs['distributor'] = producer_lines[1]
    obs['distributor_license_number'] = producer_lines[2].split('#')[-1].strip()
    obs['distributor_street'] = producer_lines[3]
    obs['distributor_city'] = producer_lines[4].split(',')[0].strip()
    obs['distributor_state'] = producer_lines[4].split(',')[1].strip().split(' ')[0]
    obs['distributor_zipcode'] = producer_lines[4].split(' ')[-1].strip()

    # Get analyses, methods, and results.
    analyses, methods, results = [], [], []

    # Get cannabinoids.
    sublist = list_between_values(unique_lines, 'Cannabinoids', 'Cannabinoids = ')
    if sublist:
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
                break
        sublist = list_between_values(sublist, 'mg/g', 'Total THC =')
        analyses.append('cannabinoids')
        for line in sublist:
            if 'Total THC' in line:
                value = line.split('Total THC')[1].strip().split(' ')[0]
                obs['total_thc'] = convert_to_numeric(value)
            elif 'Total CBD' in line:
                value = line.split('Total CBD')[1].strip().split(' ')[0]
                obs['total_cbd'] = convert_to_numeric(value)
            elif 'Total Cannabinoids' in line:
                value = line.split('Total Cannabinoids')[1].strip().split(' ')[0]
                obs['total_cannabinoids'] = convert_to_numeric(value)
            elif 'Sum of Cannabinoids' in line:
                value = line.split('Sum of Cannabinoids')[1].strip().split(' ')[0]
                obs['total_cannabinoids'] = convert_to_numeric(value)
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                try:
                    results.append({
                        'analysis': 'cannabinoids',
                        'key': key,
                        'name': name,
                        'lod': convert_to_numeric(values[0]),
                        'loq': convert_to_numeric(values[1]),
                        'value': convert_to_numeric(values[2]),
                        'mg_g': convert_to_numeric(values[3]),
                        'units': 'percent',
                    })
                except:
                    pass

    # Get heavy metals.
    sublist = list_between_values(unique_lines[-25:], 'Heavy Metals', 'without')
    if sublist:
        analyses.append('heavy_metals')
        for line in sublist:
            if 'μg/g' in line:
                continue
            elif 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                try:
                    results.append({
                        'analysis': 'heavy_metals',
                        'key': key,
                        'name': name,
                        'lod': convert_to_numeric(values[0]),
                        'loq': convert_to_numeric(values[1]),
                        'limit': convert_to_numeric(values[3]),
                        'value': convert_to_numeric(values[2]),
                        'status': values[4],
                        'units': 'μg/g',
                    })
                except:
                    pass

    # Get microbe results.
    sublist = list_between_values(unique_lines[-100:], 'Microbial Impurities', 'Date Tested')
    if sublist:
        analyses.append('microbes')
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Analytes' in line:
                continue
            else:
                line = line.replace('Not Detected in 1g', 'ND')
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                try:
                    results.append({
                        'analysis': 'microbes',
                        'key': key,
                        'name': name,
                        'value': convert_to_numeric(values[0]),
                        'status': values[1],
                        'units': 'cfu/g',
                    })
                except:
                    pass

    # Get mycotoxin results.
    sublist = list_between_values(lines[-100:], 'Mycotoxins', 'Date Tested')
    if sublist:
        analyses.append('mycotoxins')
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Analytes' in line or 'μg/kg' in line or 'Total' in line:
                continue
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                if len(values) == 4:
                    values.insert(2, 20)
                try:
                    results.append({
                        'analysis': 'mycotoxins',
                        'key': key,
                        'name': name,
                        'lod': convert_to_numeric(values[0]),
                        'loq': convert_to_numeric(values[1]),
                        'limit': convert_to_numeric(values[2]),
                        'value': convert_to_numeric(values[3]),
                        'status': values[4],
                        'units': 'μg/kg',
                    })
                except:
                    pass

    # Get pesticide results.
    sublist = list_between_values(lines[50:], 'Pesticides', 'Date Tested')
    if sublist:
        analyses.append('pesticides')
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Analytes' in line or 'μg/g' in line or 'Total' in line:
                continue
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                column_one = values[:5]
                results.append({
                    'analysis': 'pesticides',
                    'key': key,
                    'name': name,
                    'lod': convert_to_numeric(column_one[0]),
                    'loq': convert_to_numeric(column_one[1]),
                    'limit': convert_to_numeric(column_one[2]),
                    'value': convert_to_numeric(column_one[3]),
                    'status': column_one[4],
                    'units': 'μg/g',
                })
                if len(values) > 5:
                    column_two = values[5:]
                    if len(column_two) > 6:
                        name = ' '.join([column_two[0]] + [column_two[1]])
                        column_two = [name] + column_two[2:]
                    name = column_two.pop(0).strip()
                    key = snake_case(name)
                    key = ANALYTES.get(key, key)
                    results.append({
                        'analysis': 'pesticides',
                        'key': key,
                        'name': name,
                        'lod': convert_to_numeric(column_two[0]),
                        'loq': convert_to_numeric(column_two[1]),
                        'limit': convert_to_numeric(column_two[2]),
                        'value': convert_to_numeric(column_two[3]),
                        'status': column_two[4],
                        'units': 'μg/g',
                    })

    # Get residual solvent results.
    sublist = list_between_values(lines[50:], 'Residual Solvents', 'Date Tested')
    if sublist:
        analyses.append('residual_solvents')
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Analytes' in line or 'μg/g' in line:
                continue
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                results.append({
                    'analysis': 'residual_solvents',
                    'key': key,
                    'name': name,
                    'lod': convert_to_numeric(values[0]),
                    'loq': convert_to_numeric(values[1]),
                    'limit': convert_to_numeric(values[2]),
                    'value': convert_to_numeric(values[3]),
                    'status': values[4],
                    'units': 'μg/g',
                })

    # Get terpenes.
    sublist = list_between_values(unique_lines, 'Terpenes', 'Primary Aromas')
    if sublist:
        sublist = list_between_values(sublist, 'Terpenes', 'LOQ =')
        analyses.append('terpenes')
        for line in sublist:
            if 'LOQ =' in line or 'Date Tested' in line:
                continue
            elif 'Method' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Total' in line:
                value = line.split('Total')[1].strip().split(' ')[0]
                obs['total_terpenes'] = convert_to_numeric(value)

            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                try:
                    results.append({
                        'analysis': 'terpenes',
                        'key': key,
                        'name': name,
                        'lod': convert_to_numeric(values[0]),
                        'loq': convert_to_numeric(values[1]),
                        'value': convert_to_numeric(values[2]),
                        'mg_g': convert_to_numeric(values[3]),
                        'units': 'percent',
                    })
                except:
                    pass

    # Get moisture content and water activity.
    for line in unique_lines:
        if 'Moisture' in line:
            match = re.compile(r"\b\d+\.?\d*%").search(line)
            if match:
                percentage_value = float(match.group()[:-1])
                obs['moisture_content'] = percentage_value
        elif 'Water Activity' in line:
            match = re.compile(r"\b\d+\.\d+\s*aw").search(line)
            if match:
                aw_value = float(match.group().strip(' aw'))
                obs['water_activity'] = aw_value
            break

    # Close the PDF.
    report.close()

    # Finish data collection with a freshly minted sample ID.
    obs = {**ENCORE_LABS, **obs}
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

    # FIXME: Test parsing a URL.
    parser = CoADoc()
    doc = 'https://orders.confidentcannabis.com/report/public/sample/6ea7ee5b-8443-4c8f-b87c-ab17eba6cad1'
    data = parse_encore_coa(parser, doc)
    assert data is not None

    # Test parsing full-panel flower COA.
    doc = r'D:/data/california/lab_results/.datasets/flower-company/pdfs/710-labs-badder-cardan.pdf'
    data = parse_encore_coa(parser, doc)
    assert data is not None

    # Test parsing full-panel concentrate COA.
    doc = r'D:/data/california/lab_results/pdfs/flower-company/bbd406b8a6f3f0683006bc2d366c75d9f400a4794513db10ca2e2c0b618fe62f.pdf'
    data = parse_encore_coa(parser, doc)
    assert data is not None
