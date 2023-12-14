"""
CoADoc | Parse Northeast Laboratories COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 12/11/2023
Updated: 12/12/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Extract data from NE Labs COAs and merge the COA data with product
    data from the Connecticut Medical Marijuana Brand Registry.

Data Points:

    ✓ id
    ✓ lab_id
    ✓ product_id
    ✓ product_name
    ✓ product_type
    ✓ brand
    ✓ image_url
    ✓ lab_results_url
    ✓ date_reported
    ✓ date_received
    ✓ date_tested
    ✓ total_terpenes
    ✓ cannabinoids_method
    ✓ total_cannabinoids
    ✓ sample_weight
    ✓ label_url
    ✓ lab
    ✓ lab_website
    ✓ lab_license_number
    ✓ lab_image_url
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    ✓ lab_county
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_latitude
    ✓ lab_longitude
    ✓ lab_phone
    ✓ producer
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_county
    ✓ producer_state
    ✓ producer_zipcode
    ✓ analyses
    ✓ reported_results
    ✓ results


"""
# Standard imports:
from datetime import datetime
import json
import os
from typing import Any, Optional

# External imports:
from cannlytics import __version__
from cannlytics.data.data import create_hash, create_sample_id
from cannlytics.utils import convert_to_numeric, snake_case
from cannlytics.utils.constants import ANALYTES
import pandas as pd
import pdfplumber


NE_LABS = {
    'coa_algorithm': 'ne_labs.py',
    'coa_algorithm_entry_point': 'parse_ne_labs_coa',
    'lims': 'Northeast Laboratories',
    'url': 'www.nelabsct.com',
    'lab': 'Northeast Laboratories',
    'lab_website': 'www.nelabsct.com',
    'lab_license_number': 'CTM0000001',
    'lab_image_url': 'https://www.nelabsct.com/images/Northeast-Laboratories.svg',
    'lab_address': '129 Mill Street, Berlin, CT 06037',
    'lab_street': '129 Mill Street',
    'lab_city': 'Berlin',
    'lab_county': 'Hartford',
    'lab_state': 'CT',
    'lab_zipcode': '06037',
    'lab_latitude': 41.626190,
    'lab_longitude': -72.748250,
    'lab_phone': '860-828-9787',
    # 'lab_email': '',
}


def parse_ne_labs_coa(
        parser,
        doc: Any,
        public_key: Optional[str] = 'product_id',
        verbose: Optional[bool] = False,
        **kwargs,
    ) -> dict:
    """Parse a Northeast Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # Initialize.
    obs = {}

    # Read the PDF.
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
    else:
        report = doc
    obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]

    # Extract producer details.
    page = report.pages[0]
    midpoint = page.width * 0.45
    left_half = (0, 0, midpoint, page.height)
    left_half_page = page.crop(left_half)
    left_text = left_half_page.extract_text()
    lines = left_text.split('\n')
    parts = lines[2].split(' ')
    obs['producer'] = lines[0]
    obs['producer_street'] = lines[1]
    obs['producer_city'] = ' '.join(parts[0:-2]).rstrip(',')
    obs['producer_state'] = parts[-2]
    obs['producer_zipcode'] = parts[-1]
    obs['producer_address'] = ', '.join([obs['producer_street'], obs['producer_city'], obs['producer_state'] + ' ' + obs['producer_zipcode']])

    # Extract dates and product details.
    right_half = (midpoint, 0, page.width, page.height)
    right_half_page = page.crop(right_half)
    right_text = right_half_page.extract_text()
    lines = right_text.split('\nResults')[0].split('\n')
    for line in lines:
        if 'Date Received' in line:
            obs['date_received'] = line.split(': ')[-1]
        if 'Report Date' in line:
            obs['date_tested'] = line.split(': ')[-1]
        if 'Report ID' in line:
            obs['lab_id'] = line.split(': ')[-1]
        
    # Get the product ID.
    top_half = page.crop((0, 0, page.width, page.height * 0.5))
    top_lines = top_half.extract_text().split('\n')
    for line in top_lines:
        if 'Product ID' in line:
            obs['product_id'] = line.split(': ')[-1]
            break

    # Get the tables.
    tables = []
    for page in report.pages:
        tables.extend(page.extract_tables())

    # Clean the tables.
    clean_tables = []
    for table in tables:
        clean_table = []
        for row in table:
            clean_table.append([cell for cell in row if cell])
        clean_tables.append(clean_table)

    # Get the results from the tables.
    analyses, results = [], []
    for table in clean_tables:
        table_name = table[0][0]

        # Hot-fix for cannabinoids:
        if table_name == 'C':
            table_name = 'Cannabinoids\nby HPLC'

        # Get the microbes.
        if table_name.startswith('Microbiology'):
            analyses.append('microbes')
            for cells in table[1:]:
                # cells = [cell for cell in row if cell]
                if 'Pass/Fail' in cells[0]:
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'microbes',
                    'key': key,
                    'name': cells[0],
                    'value': cells[1],
                    'limit': cells[2],
                    'method': cells[3],
                    'units': 'µg/kg',
                })

        # Get the cannabinoids, if not already collected.
        elif table_name.startswith('Cannabinoids') and 'cannabinoids' not in analyses:
            analyses.append('cannabinoids')
            if '\nby ' in table_name:
                obs['cannabinoids_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                # cells = [cell for cell in row if cell]
                if not cells or 'dry weight' in cells[0]:
                    continue
                if 'Total Cannabinoids' in cells[0]:
                    if len(cells) == 1:
                        obs['total_cannabinoids'] = convert_to_numeric(cells[0].split(':')[-1].strip())
                    else:
                        obs['total_cannabinoids'] = convert_to_numeric(cells[1].replace(' %', ''))
                    continue
                if 'Total THC' in cells[0]:
                    values = cells[0].split('\n')
                    obs['total_thc'] = convert_to_numeric(values[0].replace(' %', ''))
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'cannabinoids',
                    'key': key,
                    'name': cells[0],
                    'value': convert_to_numeric(cells[1]),
                    'units': 'percent',
                })

        # Get the terpenes.
        elif table_name.startswith('Terpenes'):
            analyses.append('terpenes')
            if '\nby ' in table_name:
                obs['terpenes_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                # cells = [cell for cell in row if cell]
                if not cells or 'dry weight' in cells[0]:
                    continue
                if 'Total Terpenes' in cells[0]:
                    values = cells[0].split('\n')
                    obs['total_terpenes'] = convert_to_numeric(values[0].replace(' %', '').replace('Total Terpenes: ', ''))
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'terpenes',
                    'key': key,
                    'name': cells[0],
                    'value': convert_to_numeric(cells[1]),
                    'units': 'percent',
                })

        # Get the pesticides.
        elif table_name.startswith('Pesticides'):
            analyses.append('pesticides')
            if '\nby ' in table_name:
                obs['pesticides_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                # cells = [cell for cell in row if cell]
                if 'Pass/Fail' in cells[0]:
                    continue
                # Handle two-column tables.
                if len(cells) == 4:
                    split_cells = [cells[:2], cells[2:]]
                    for split in split_cells:
                        key = ANALYTES.get(snake_case(split[0]), snake_case(split[0]))
                        results.append({
                            'analysis': 'pesticides',
                            'key': key,
                            'name': split[0],
                            'value': split[1],
                            'limit': None,
                            'units': None,
                        })
                else:
                    key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                    results.append({
                        'analysis': 'pesticides',
                        'key': key,
                        'name': cells[0],
                        'value': cells[1],
                        'limit': cells[2],
                        'units': None,
                    })

        # Get the heavy metals.
        elif table_name.startswith('Heavy Metals'):
            analyses.append('heavy_metals')
            if '\nby ' in table_name:
                obs['heavy_metals_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                # cells = [cell for cell in row if cell]
                if 'Pass/Fail' in cells[0]:
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'heavy_metals',
                    'key': key,
                    'name': cells[0],
                    'value': cells[1],
                    'limit': cells[2],
                    'units': '',
                })

        # Get the mycotoxins.
        elif table_name.startswith('Mycotoxins'):
            analyses.append('mycotoxins')
            if '\nby ' in table_name:
                obs['mycotoxins_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                if 'Pass/Fail' in cells[0]:
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'mycotoxins',
                    'key': key,
                    'name': cells[0],
                    'value': cells[1],
                    'limit': cells[2],
                    'units': 'µg/kg',
                })

        # Get the moisture content and water activity.
        elif table_name.startswith('Moisture'):
            for cells in table[1:]:
                if 'Content' in cells[0]:
                    obs['moisture_content'] = convert_to_numeric(cells[-1])
                elif 'Activity' in cells[0]:
                    obs['water_activity'] = convert_to_numeric(cells[-1])

        # Get the residual solvents results.
        elif 'Residual' in table_name:
            analyses.append('residual_solvents')
            if '\nby ' in table_name:
                obs['residual_solvents_method'] = table_name.split('\nby ')[-1]
            for cells in table[1:]:
                if 'Pass/Fail' in cells[0]:
                    continue
                key = ANALYTES.get(snake_case(cells[0]), snake_case(cells[0]))
                results.append({
                    'analysis': 'residual_solvents',
                    'key': key,
                    'name': cells[0],
                    'value': cells[1],
                    'units': 'percent',
                })
        # Get the sample weight.
        elif table_name.startswith('Density'):
            obs['sample_weight'] = convert_to_numeric(table[1][-1])

    # Close the report.
    report.close()

    # Standardize dates.
    obs = standardize_dates(obs)

    # Finish data collection with a freshly minted sample ID.
    obs = {**NE_LABS, **obs}
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['results'] = json.dumps(results)
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs[public_key],
        salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
    )
    obs['sample_hash'] = create_hash(obs)
    return obs


def standardize_dates(item: dict) -> dict:
    """Turn dates to ISO format."""
    date_columns = [x for x in item.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            item[date_column] = pd.to_datetime(item[date_column]).isoformat()
        except:
            pass
    return item


def extract_url(s):
    """Extract the URL from the string representation of the list."""
    try:
        list_rep = eval(s)
        return list_rep[0] if list_rep else None
    except:
        return None


# === Test ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc
        
    # === Read the data ===

    # Specify where your data lives.
    DATA_DIR = 'D:/data/connecticut/lab_results'
    PDF_DIR = 'D:/data/connecticut/lab_results/pdfs'
    stats_dir = '../data/ct'

    # Read in downloaded CT results.
    datafile = '../data/ct/ct-lab-results-latest.csv'
    ct_results = pd.read_csv(datafile)

    # Clean URLs.
    ct_results['image_url'] = ct_results['image_url'].apply(extract_url)
    ct_results['label_url'] = ct_results['images'].apply(extract_url)
    ct_results['lab_results_url'] = ct_results['lab_results_url'].apply(extract_url)

    # Rename certain columns.
    ct_results.rename(columns={
        'date_tested': 'date_reported',
        'producer': 'brand',
        'results': 'reported_results',
    }, inplace=True)

    # Drop certain columns.
    ct_results.drop(columns=['images'], inplace=True)


    # === Parse CT COAs ===

    # Find the COA for each sample.
    parser = CoADoc()
    missing = 0
    invalid = 0
    pdf_files = {}
    all_results = []
    for index, row in ct_results.iterrows():

        if index < 100:
            continue

        # Identify if the COA exists.
        pdf_file = os.path.join(PDF_DIR, row['id'] + '.pdf')
        if not os.path.exists(pdf_file):
            pdf_file = os.path.join(PDF_DIR, row['lab_id'] + '.pdf')
            if not os.path.exists(pdf_file):
                missing += 1
                continue

        # Record the PDF.
        pdf_files[row['id']] = pdf_file

        # TODO: Use the parser to extract data and identify the lab.
        # parser = CoADoc(lims={'NE Labs': NE_LABS_CT})
        # parser.identify_lims(front_page_text)

        # Identify the lab and extract the COA data.
        try:
            report = pdfplumber.open(pdf_file)
        except:
            print('Invalid file:', pdf_file)
            invalid += 1
            continue
        front_page_text = report.pages[0].extract_text()
        if NE_LABS['url'] in front_page_text:
            try:
                coa_data = parse_ne_labs_coa(parser, pdf_file)
            except:
                print('Failed to parse:', pdf_file)
                continue

        # Future work: Handle other labs, e.g. historic AltaSci.
        else:
            print('Unidentified lab:', pdf_file)
            continue

        # Merge details with COA data.
        all_results.append({**row.to_dict(), **coa_data})
        print('Parsed:', pdf_file)

    # Save the augmented CT lab results data.
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outfile = os.path.join(DATA_DIR, f'ct-coa-data-{timestamp}.xlsx')
    parser.save(pd.DataFrame(all_results), outfile)
