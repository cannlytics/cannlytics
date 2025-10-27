"""
Parse Custom Confident Cannabis COAs
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/2/2024
Updated: 3/5/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Tested Labs:

    - Encore Labs
    - SQRD Lab

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
    x distributor_street
    x distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ producer
    ✓ producer_license_number
    ✓ producer_address
    x producer_street
    x producer_city
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
    x lab_latitude
    x lab_longitude

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
    snake_case,
)
from cannlytics.utils.constants import ANALYTES
import pdfplumber
from selenium.webdriver.common.by import By
import zipcodes


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


def parse_cc_custom_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        verbose: Optional[bool] = False,
        pause: Optional[float] = 10,
        headless: Optional[bool] = True,
        persist: Optional[bool] = False,
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
            if parser.driver is None:
                parser.driver = initialize_selenium(
                    download_dir=download_dir,
                    headless=headless,
                )
            parser.driver.get(doc)
            sleep(pause)
            button = parser.driver.find_element(by=By.TAG_NAME, value='button')
            button.click()
            sleep(pause)
            if not persist:
                parser.quit()
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
        
    # Get lab details.
    obs['lims'] = 'Confident Cannabis'
    front_page = report.pages[0]
    top = front_page.within_bbox((0, 0, front_page.width, front_page.height * 0.25))
    top_lines = top.extract_text_lines(layout=True, strip=False, return_chars=True)
    for line in top_lines:
        parts = line['text'].replace('  ', '\n').split('\n')
        parts = [x.strip() for x in parts if x]
        for i, part in enumerate(parts):
            if '(' in part:
                obs['lab'] = parts[i - 1]
                obs['lab_phone'] = part
            elif 'http' in part:
                obs['lab_street'] = part.split('http')[0].strip()
                obs['lab_website'] = 'http' + part.split('http')[-1].split('.com')[0].replace('\x00', 'f') + '.com'
            elif 'Lic#' in part:
                address = part.split('Lic#')[0].strip()
                obs['lab_license_number'] = part.split('Lic#')[-1].strip()
                obs['lab_city'] = address.split(',')[0].strip()
                obs['lab_state'] = address.split(',')[1].strip().split(' ')[0]
                obs['lab_zipcode'] = address.split(',')[1].strip().split(' ')[1]
                obs['lab_address'] = ', '.join((obs['lab_street'], address))
                try:
                    matches = zipcodes.matching(obs['lab_zipcode'])
                    if matches:
                        obs['lab_county'] = matches[0]['county'].replace(' County', '')
                except:
                    pass
            elif part.startswith('1 of '):
                break

    # Crop the producer and distributor areas.
    # Finds the location of the words "Producer" and "Distributor".
    # The distributor area is the space starting at the word "Distributor" and ending at the word "Producer".
    # The producer area starts at the word "Producer" and ends at the end of the page.
    # The areas go down to the 2nd line. If the line can't be found,
    # then goes down to just above the y-coordinate of the word "Summary".
    front_page = report.pages[0]
    top = front_page.within_bbox((0, 0, front_page.width, front_page.height * 0.25))
    words = top.extract_words()
    producer_coords = None
    distributor_coords = None
    collected_coords = None
    for word in words:
        if word['text'] == "Producer":
            producer_coords = (word['x0'], word['top'], word['x1'], word['bottom'])
        elif word['text'] == "Distributor":
            distributor_coords = (word['x0'], word['top'], word['x1'], word['bottom'])
        elif word['text'] == "Collected:":
            collected_coords = (word['x0'], word['top'], word['x1'], word['bottom'])
        if producer_coords and distributor_coords and collected_coords:
            break
    bottom_boundary = top.height
    try:
        border_line = top.lines[-1]
        bottom_boundary = min(border_line['top'], border_line['bottom'])
    except:
        for word in words:
            if word['text'] == "Summary":
                bottom_boundary = max(word['top'], word['bottom']) - 5
                break

    # Get the lines of the metadata.
    if collected_coords:
        collected_bbox = (
            collected_coords[0] - 5, collected_coords[1] - 15, # x0, y0
            distributor_coords[0] - 5, bottom_boundary # x1, y1
        )
        collected_section = top.within_bbox(collected_bbox)
        if collected_section:
            collected_text = collected_section.extract_text()

        id_bbox = (
            0, 0, # x0, y0
            collected_coords[0] - 5, bottom_boundary # x1, y1
        )
        id_section = top.within_bbox(id_bbox)
        if id_section:
            id_text = id_section.extract_text()

    # Compile the top text lines.
    top_text = '\n'.join((id_text, collected_text))
    top_lines = top_text.split('\n')

    # Get the COA metadata.
    for line in top_lines:
        # Get the Metrc IDs.
        if 'METRC Batch' in line or 'Source Package ID:' in line:
            value = line.split(':')[-1].strip()
            obs['metrc_source_id'] = value
        elif 'UID:' in line:
            value = line.split('UID:')[1].strip().split(' ')[0]
            obs['metrc_source_id'] = value
        elif 'METRC Sample' in line:
            value = line.split(':')[-1].strip().split(' ')[0]
            obs['metrc_sample_label'] = value
        elif len(line) == 24 and line.startswith('1A'):
            obs['metrc_source_id'] = line

        # Get the batch number.
        if 'Batch#:' in line or 'Batch Number:' in line:
            value = line.split('Batch#:')[1].strip()
            value = value.split('Batch Number:')[-1].strip()
            obs['batch_number'] = value

        # Get the Lab IDs.
        if 'Sample ID:' in line or 'LIMS ID:' in line:
            value = line.split('Sample ID:')[-1]
            value = value.split('LIMS ID:')[-1]
            obs['lab_id'] = value.strip()
            print(value)

        # Get the amounts.
        if 'Sample Size:' in line:
            value = line.split('Sample Size:')[-1].strip()
            obs['sample_size'] = value
        if ('Batch:' in line or 'Batch Size:' in line) and 'METRC' not in line:
            value = line.split('Batch:')[-1].strip()
            value = value.split('Batch Size:')[-1].strip()
            obs['batch_size'] = value

        # Get the dates.
        if 'Completed:' in line or 'Reported:' in line:
            value = line.split('Completed:')[-1]
            value = value.split('Reported:')[-1]
            value = value.strip().split(' ')[0]
            obs['date_tested'] = value
        elif 'Received:' in line:
            value = line.split('Received:')[-1].strip().split(' ')[0]
            obs['date_received'] = value
        elif 'Collected:' in line:
            value = line.split('Collected:')[-1].strip().split(' ')[0]
            obs['date_collected'] = value

        # Get the classifications.
        if 'Strain:' in line:
            value = line.split('Strain:')[-1].strip()
            obs['strain_name'] = value
        if 'Matrix:' in line:
            value = line.split('Matrix:')[-1].strip()
            obs['product_type'] = value
        elif 'Type:' in line:
            value = line.split('Type:')[-1].strip()
            obs['product_subtype'] = value

    # Get the product name.
    obs['product_name'] = lines[5].strip()

    # Get the producer details.
    if producer_coords:
        producer_bbox = (
            producer_coords[0] - 5, producer_coords[1], # x0, y0
            top.width, bottom_boundary # x1, y1
        )
        producer_section = top.within_bbox(producer_bbox)
        if producer_section:
            producer_text = producer_section.extract_text()
            obs['producer'] = producer_text.split('Producer')[-1].split('Lic. #')[0].replace('\n', ' ').strip()
            obs['producer_license_number'] = producer_text.split('Lic. #')[-1].replace('\n', ' ').split(' ')[1]
            address = producer_text.split(obs['producer_license_number'])[-1].strip()
            address = address.replace('\n', ' ').replace('  ', ' ')
            obs['producer_address'] = address
            obs['producer_state'] = address.split(' ')[-2]
            obs['producer_zipcode'] = address.split(' ')[-1]
            # TODO: Find a way to identify the street and city.
            # obs['producer_street'] = address.split(',')[0].strip()
            # obs['producer_city'] = address.split(',')[1].strip().split(' ')[0]

    # Get the distributor details.
    if distributor_coords:
        distributor_bbox = (
            distributor_coords[0] - 5, distributor_coords[1], # x0, y0
            producer_coords[0], bottom_boundary # x1, y1
        )
        distributor_section = top.within_bbox(distributor_bbox)
        if distributor_section:
            distributor_text = distributor_section.extract_text()
            obs['distributor'] = distributor_text.split('Distributor')[-1].split('Lic. #')[0].replace('\n', ' ').strip()
            obs['distributor_license_number'] = distributor_text.split('Lic. #')[-1].replace('\n', ' ').split(' ')[1]
            address = distributor_text.split(obs['distributor_license_number'])[-1].strip()
            address = address.replace('\n', ' ').replace('  ', ' ')
            obs['distributor_address'] = address
            obs['distributor_state'] = address.split(' ')[-2]
            obs['distributor_zipcode'] = address.split(' ')[-1]
            # TODO: Find a way to identify the street and city.

    # Get analyses, methods, and results.
    analyses, methods, results = [], [], []

    # Get cannabinoids.
    # FIXME: Generalize to multiple labs.
    sublist = list_between_values(unique_lines, 'Total THC', 'Total THC =')
    if sublist:
        # FIXME: Get the cannabinoids method.
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
                break

        # sublist = list_between_values(sublist, 'mg/g', 'Total THC =')
        analyses.append('cannabinoids')
        for line in sublist:
            if 'Analyte' in line or 'serving(s) per container' in line or 'Testing performed' in line:
                continue
            elif 'mg/g' in line:
                # FIXME: Get the column order.
                continue

            if 'Total THC' in line:
                value = line.split('Total THC')[1].strip().split(' ')[0]
                obs['total_thc'] = convert_to_numeric(value)
            elif 'Total CBD' in line:
                value = line.split('Total CBD')[1].strip().split(' ')[0]
                obs['total_cbd'] = convert_to_numeric(value)
            elif 'Total Cannabinoids' in line:
                value = line.split('Total Cannabinoids')[1].strip().split(' ')[0]
                obs['total_cannabinoids'] = convert_to_numeric(value)
            elif 'Total' in line:
                value = line.split('Total')[1].strip().split(' ')[0]
                obs['total_cannabinoids'] = convert_to_numeric(value)
            elif 'Sum of Cannabinoids' in line:
                value = line.split('Sum of Cannabinoids')[1].strip().split(' ')[0]
                obs['sum_of_cannabinoids'] = convert_to_numeric(value)
            else:
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                try:
                    # FIXME: Need to get the order of the columns!
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
    sublist = list_between_values(unique_lines[50:], 'Heavy Metals', 'without')
    if not sublist:
        sublist = list_between_values(unique_lines[50:], 'Heavy Metals', 'Test performed')
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
                        'limit': convert_to_numeric(values[2]),
                        'value': convert_to_numeric(values[3]),
                        'status': values[4],
                        'units': 'μg/g',
                    })
                except:
                    pass

    # Get microbe results.
    sublist = list_between_values(unique_lines[50:], 'Microbial', 'Date Tested')
    if not sublist:
        sublist = list_between_values(unique_lines[50:], 'Microbial', 'ND = Not Detected')
    if sublist:
        analyses.append('microbes')
        for line in sublist:
            if 'Method:' in line:
                methods.append(line.split('Method:')[1].strip())
            elif 'Analyte' in line or 'Testing performed' in line:
                continue
            else:
                line = line.replace('Not Detected in 1g', 'ND')
                line = line.replace('Not Detected', 'ND')
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = snake_case(name)
                key = ANALYTES.get(key, key)
                values = [x.strip() for x in line[first_value:].split(' ') if x]
                results.append({
                    'analysis': 'microbes',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(values[-2]),
                    'status': values[-1],
                    'units': 'cfu/g',
                })
                print(results[-1])

    # Get mycotoxin results.
    # FIXME: Generalize to multiple labs.
    sublist = list_between_values(lines[50:], 'Mycotoxins', 'Date Tested')
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
    # FIXME: Generalize to multiple labs.
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
    # FIXME: Generalize to multiple labs.
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
    # FIXME: Generalize to multiple labs.
    sublist = list_between_values(unique_lines[50:], 'Terpenes', 'Primary Aromas')
    if sublist:
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
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['coa_algorithm'] = 'parse_cc_custom_coa'
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
# Tested: 2024-03-04 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # # [✓] Test parsing a URL.
    # parser = CoADoc()
    # doc = 'https://orders.confidentcannabis.com/report/public/sample/6ea7ee5b-8443-4c8f-b87c-ab17eba6cad1'
    # data = parse_cc_custom_coa(parser, doc, pause=4, headless=False)
    # assert data is not None

    # # [✓] Test parsing full-panel flower COA.
    # parser = CoADoc()
    # doc = r'D:/data/california/lab_results/.datasets/flower-company/pdfs/710-labs-badder-cardan.pdf'
    # data = parse_cc_custom_coa(parser, doc)
    # assert data is not None

    # # [✓] Test parsing full-panel concentrate COA.
    # parser = CoADoc()
    # doc = r'D:/data/california/lab_results/pdfs/flower-company/bbd406b8a6f3f0683006bc2d366c75d9f400a4794513db10ca2e2c0b618fe62f.pdf'
    # data = parse_cc_custom_coa(parser, doc)
    # assert data is not None

    # # [✓] Test parsing a COA with multi-line producer names.
    # parser = CoADoc()
    # doc = r'D:/data/california/lab_results/pdfs/flower-company\deef169934c829c782b2da8eaad34f95e3785c9bfdd66b1692b471c94e9bdf74.pdf'
    # data = parse_cc_custom_coa(parser, doc)
    # assert data is not None

    # FIXME: Parse a SQRD Lab COA
    # - Make lab details dynamic.

    # D:/data/california/lab_results/pdfs/flower-company\84bf23ab73cf896e24aeb1f8ff28f4e5a128dac6378e6e395be1b760ea32129d.pdf
    # D:/data/california/lab_results/pdfs/flower-company\4b019adf6a4ff69bf462b48ef909f1f9d416c6c7de0c15cdcfc719f42cb7ff46.pdf
    # D:/data/california/lab_results/pdfs/flower-company\5519cada071fb83bdc63cbfaa25b66742b837e6e0fc39335a05be5368fad90ec.pdf
    # D:/data/california/lab_results/pdfs/flower-company\e534195f57fcfd03528c1e54afcfd5b12e5d2fb3e6db5d1086b58f9436732c21.pdf
    doc = r'D:/data/california/lab_results/pdfs/flower-company/3beafe9ef2e762d6cbc97857733cf6d7e55835dad8aad59a2e5e60701bb798c4.pdf'
    parser = CoADoc()
    data = parse_cc_custom_coa(parser, doc)
    assert data is not None
