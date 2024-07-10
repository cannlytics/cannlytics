"""
Parse COAs | Utah
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/4/2024
Updated: 7/8/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Utah COA PDFs.
"""
# Standard imports:
from datetime import datetime
import json
from typing import Any, List, Optional

# External imports:
import pandas as pd
import pdfplumber

# Internal imports:
from cannlytics import __version__
from cannlytics.data.data import create_hash, create_sample_id, find_first_value
from cannlytics.utils.utils import convert_to_numeric, snake_case


# It is assumed that the lab has the following details.
UT_DEPT_OF_AG_AND_FOOD = {
    'coa_algorithm': 'utah.py',
    'coa_algorithm_entry_point': 'parse_utah_coa',
    'lims': 'Utah Department of Agriculture and Food',
    'lab': 'Utah Department of Agriculture and Food',
    'lab_street': '4451 South 2700 West',
    'lab_city': 'Taylorsville',
    'lab_state': 'UT',
    'lab_zipcode': '84129',
    'lab_phone': '(801) 816-3840',
    'fields': {
        'UDAF Lab #': 'lab_license_number',
        'Issue Date': 'date_tested',
        'Client': 'distributor',
        'Client Email': 'distributor_email',
        'Producer': 'producer',
        'Sample Type': 'product_type',
        'Description': 'product_name',
        'Batch/Lot Number': 'batch_number',
        'Date Received': 'date_received',
        'Date Collected': 'date_sampled',
        'Collected By': 'sampled_by',
        'Quantity Received': 'sample_weight',
        'Sample Number': 'lab_id',
        'MJ Batch Number': 'batch_number',
        'Strain': 'strain_name',
        'Lab Tracking Number': 'lab_id',
        'MJF Batch#': 'batch_number',
        'Report Issue Date': 'date_tested',
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


def find_consecutive_words(page, target):
    """
    Find the position of consecutive words on the page.
    Args:
        page (pdfplumber.page.Page): A PDFPlumber page object.
        target (str): The target string to find.
    Returns:
        Tuple[float, float, float, float] or None:
        Coordinates (x0, y0, x1, y1) of the bounding box around the
        words if found, else None.
    """
    words = page.extract_words()
    target_words = target.split(' ')
    num_target_words = len(target_words)
    for i in range(len(words) - num_target_words + 1):
        if all(words[i + j]['text'] == target_words[j] for j in range(num_target_words)):
            x0 = min(words[i]['x0'] for i in range(i, i + num_target_words))
            y0 = min(words[i]['top'] for i in range(i, i + num_target_words))
            x1 = max(words[i]['x1'] for i in range(i, i + num_target_words))
            y1 = max(words[i]['bottom'] for i in range(i, i + num_target_words))
            return x0, y0, x1, y1
    return None


def calculate_total(results, analysis='cannabinoids', places=2):
    """Calculate the total of an analysis from a list of results."""
    total = 0
    for result in results:
        if result.get('analysis') == analysis:
            value = convert_to_numeric(str(result.get('value')), strip=True)
            try:
                total += value
            except:
                pass
    return round(total, places)


def calculate_total_cannabinoid(
        results: List[dict],
        base_key: Optional[str] = 'delta_9_thc',
        acid_key: Optional[str] = 'thca',
        decarb: Optional[float] = 0.877,
    ) -> float:
    """Calculates total THC given a list of results.
    """
    results_data = pd.DataFrame(results)
    try:
        base = results_data.loc[results_data['key'] == base_key].iloc[0]['value']
    except IndexError:
        base = 0
    try:
        acid = results_data.loc[results_data['key'] == acid_key].iloc[0]['value']
    except IndexError:
        acid = 0
    base = convert_to_numeric(base)
    if not isinstance(base, float): base = 0
    acid = convert_to_numeric(acid)
    if isinstance(acid, float): base += acid * decarb
    return base


def parse_utah_coa(
        parser,
        doc: Any,
        coa_parameters: dict = UT_DEPT_OF_AG_AND_FOOD,
        **kwargs,
    ) -> dict:
    """Parse a Green Analytics COA PDF.
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

    # Handle historic COAs.
    front_page = report.pages[0]
    if 'UTAH DEPARTMENT OF AGRICULTURE AND FOOD' in front_page.extract_text():
        return parse_historic_utah_coa(parser, report, coa_parameters)

    # Get sample details.
    tables = front_page.extract_tables()
    fields = coa_parameters['fields']
    cells = [(row[i], row[i+1]) for row in tables[-1] for i in range(0, len(row), 2)]
    for cell in cells:
        if not cell[0]: continue
        key = cell[0].replace(':', '').strip()
        key = fields.get(key, key)
        obs[key] = cell[1].strip()

    # Define settings for extracting tables.
    table_settings = {
        'vertical_strategy': 'lines',
        'horizontal_strategy': 'lines',
        'intersection_x_tolerance': 5,
        'intersection_y_tolerance': 5,
    }

    # TODO: Get approved by field.

    # TODO: Get methods.

    # Get cannabinoids.
    analyses, results = [], []
    cannabinoids = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Cannabinoids' in text:
            cannabinoids = True
            analyses.append('cannabinoids')
            break
    if cannabinoids:
        table = page.extract_table(table_settings)
        table = [x[1:] for x in table]
        for row in table:
            if all(cell is None or cell.strip() == '' for cell in row[1:]):
                continue
            elif row[0] == 'Analyte':
                continue
            if row[0] == 'Total Cannabinoids':
                obs['total_cannabinoids'] = convert_to_numeric(row[3].replace('%', ''))
                continue
            elif row[0] == 'Total THC':
                obs['total_thc'] = convert_to_numeric(row[3].replace('%', ''))
                continue
            elif row[0] == 'Total CBD':
                obs['total_cbd'] = convert_to_numeric(row[3].replace('%', ''))
                continue
            name = row[1]
            key = parser.analytes.get(snake_case(name), snake_case(name))
            results.append({
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'cas': row[2],
                'value': convert_to_numeric(row[3].replace('%', '')),
                'mg_g': convert_to_numeric(row[4]),
            })

    # TODO: Get extra data points:
    # - Unknown Cannabinoid Peak Area
    # - THC-OAc Peak Area
    # - Mass Per Piece

    # Get foreign matter.
    foreign_matter = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Foreign Matter' in text:
            foreign_matter = True
            analyses.append('foreign_matter')
            break
    if foreign_matter:
        table = page.extract_table(table_settings)
        row = table[-1]
        results.append({
            'analysis': 'foreign_matter',
            'key': 'foreign_matter',
            'name': 'Foreign Matter',
            'value': row[2],
            'status': row[3],
        })

    # Get microbes.
    # TODO: Check if mycotoxins are being collected.
    microbes = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Microbial' in text:
            microbes = True
            analyses.append('microbes')
            break
    if microbes:
        table = page.extract_table(table_settings)
        table = [x[1:] for x in table]
        for row in table:
            if all(cell is None or cell.strip() == '' for cell in row[1:]):
                continue
            elif row[0] == 'Analyte' or row[0] == 'Organism':
                continue
            name = row[0]
            key = parser.analytes.get(snake_case(name), snake_case(name))
            results.append({
                'analysis': 'microbes',
                'key': key,
                'name': name,
                'value': convert_to_numeric(row[1]),
                'limit': convert_to_numeric(row[2]),
                'status': row[3],
            })

    # Get moisture content and water activity.
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Moisture Content' in text:
            table = page.extract_tables()[0]
            for row in reversed(table):
                line = ' '.join([str(x) for x in row])
                if 'Moisture Content (%)' in line:
                    obs['moisture_content'] = convert_to_numeric(row[2].replace('%', ''))
                    analyses.append('moisture_content')
                    break
            for row in reversed(table):
                line = ' '.join([str(x) for x in row])
                if 'Water Activity' in line:
                    obs['water_activity'] = convert_to_numeric(row[2])
                    analyses.append('water_activity')
                    break
            break

    # Get pesticide results.
    pesticides = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Pesticide' in text:
            pesticides = True
            analyses.append('pesticides')
            break
    if pesticides:
        table = page.extract_table(table_settings)
        table = [x[1:] for x in table]
        for row in table:
            # Filter out nuisance rows
            if all(cell is None or cell.strip() == '' for cell in row[1:]):
                continue
            elif row[0] == 'Analyte':
                continue

            # Split mis-formatted rows.
            if '\n' in str(row[0]):
                cells = row[0].split('\n')
                line = cells[0]
                parts = line.split(' ')
                midpoint = len(parts) // 2
                sub_rows = [parts[:midpoint]] + [parts[midpoint:]]

            # Split normal rows.
            else:
                midpoint = len(row) // 2
                sub_rows = [row[:midpoint]] + [row[midpoint:]]

            # Record the results.
            for sub_row in sub_rows:
                name = sub_row[0]
                if not name:
                    continue
                key = parser.analytes.get(snake_case(name), snake_case(name))
                results.append({
                    'analysis': 'pesticides',
                    'key': key,
                    'name': name,
                    'cas': sub_row[1],
                    'value': convert_to_numeric(row[2]),
                    'limit': convert_to_numeric(row[3]),
                    'status': row[4],
                })

    # Get heavy metals.
    heavy_metals = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Heavy Metal' in text:
            heavy_metals = True
            analyses.append('heavy_metals')
            break
    if heavy_metals:
        table = page.extract_table(table_settings)
        table = [x[1:] for x in table]
        for row in table:
            if all(cell is None or cell.strip() == '' for cell in row[1:]):
                continue
            elif row[0] == 'Analyte':
                continue
            name = row[0]
            key = parser.analytes.get(snake_case(name), snake_case(name))
            results.append({
                'analysis': 'heavy_metals',
                'key': key,
                'name': name,
                'cas': row[1],
                'value': convert_to_numeric(row[2]),
                'limit': convert_to_numeric(row[3]),
                'status': row[4],
            })

    # Get terpenes.
    terpenes = False
    for page in report.pages[1:]:
        text = page.extract_text()
        if 'Terpene' in text:
            terpenes = True
            analyses.append('terpenes')
            break
    if terpenes:
        table = page.extract_tables()[0]
        for row in table:
            if row[0] is None:
                name = row[1]
                key = parser.analytes.get(snake_case(name), snake_case(name))
                results.append({
                    'analysis': 'terpenes',
                    'key': key,
                    'name': name,
                    'cas': row[2],
                    'value': convert_to_numeric(row[4].replace('%', '')),
                })

        # Calculate total terpenes.
        obs['total_terpenes'] = calculate_total(results, analysis='terpenes')

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
    obs = {**UT_DEPT_OF_AG_AND_FOOD, **obs}
    del obs['fields']
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['analyses'] = json.dumps(list(set(analyses)))
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


def parse_historic_utah_coa(
        parser,
        doc: Any,
        coa_parameters: dict = UT_DEPT_OF_AG_AND_FOOD,
        **kwargs,
    ) -> dict:
    """Parse a Green Analytics COA PDF.
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

    # Get sample details.
    rows = []
    front_page = report.pages[0]
    batch_coords = find_consecutive_words(front_page, 'MJ Batch Number:')
    if not batch_coords:
        batch_coords = find_consecutive_words(front_page, 'Report Issue Date:')
    sample_coords = find_consecutive_words(front_page, 'Sample Information')
    results_coords = find_consecutive_words(front_page, 'Cannabinoid Analysis')
    if not results_coords:
        results_coords = find_consecutive_words(front_page, 'Analysis')
    if batch_coords and sample_coords and results_coords:
        left_section_bbox = (
            0,  # x0 (left side of the page)
            sample_coords[3],  # y0 (bottom of "Sample Information")
            batch_coords[0],  # x1 (left of "MJ Batch Number:")
            results_coords[1]  # y1 (top of "Cannabinoid Analysis")
        )
        left_section = front_page.within_bbox(left_section_bbox)
        rows.extend(left_section.extract_text().split('\n'))
        right_section_bbox = (
            batch_coords[0],  # x0 (left of "MJ Batch Number:")
            sample_coords[3],  # y0 (bottom of "Sample Information")
            front_page.width,  # x1 (right side of the page)
            results_coords[1]  # y1 (top of "Cannabinoid Analysis")
        )
        right_section = front_page.within_bbox(right_section_bbox)
        rows.extend(right_section.extract_text().split('\n'))
    else:
        print("FIXME: One or more target texts were not found on the page.")
        print(report.stream.name)
    fields = coa_parameters['fields']
    for line in rows:
        for field, key in fields.items():
            if field in line:
                value = line.split(':', maxsplit=1)[-1].strip()
                if key.startswith('date'):
                    value = value.split(' ')[0]
                obs[key] = value

    # Handle long producer names.
    if not obs.get('producer'):
        parts = extract_lines(rows, None, 'Description')
        value = ' '.join(parts).replace('Producer:', '').strip().replace('  ', ' ')
        obs['producer'] = value
    
    # Handle long product names.
    if not obs.get('product_name'):
        parts = extract_lines(rows, 'Producer', 'Collected By')
        value = ' '.join(parts).replace('Description:', '').strip().replace('  ', ' ')
        obs['product_name'] = value

    # Get analyses and results.
    # TODO: Get methods.
    analyses, results = [], []

    # Get cannabinoid results.
    text = front_page.extract_text()
    if 'Cannabinoid Analysis' in text:
        analyses.append('cannabinoids')
        lines = text.split('\n')
        rows = extract_lines(lines, 'Analyte', 'Total Cannabinoids')
        rows = extract_lines(rows, None, 'Analysis')
        for line in rows:
            if 'Analysis' in line or 'Analyte' in line or ' & ' in line or ' of ' in line:
                continue
            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = parser.analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            result = {
                'analysis': 'cannabinoids',
                'key': key,
                'name': name,
                'value': convert_to_numeric(values[0]),
            }
            if len(values) > 1:
                result['mg_g'] = convert_to_numeric(values[-1])
            results.append(result)

        # Get total cannabinoids.
        total_cannabinoids = False
        for line in lines:
            if 'Total Cannabinoids' in line:
                total_cannabinoids = True
                value = line.replace('Total Cannabinoids', '').strip().split(' ')[0]
                obs['total_cannabinoids'] = convert_to_numeric(value.replace('%', ''))
                break
        if not total_cannabinoids:
            obs['total_cannabinoids'] = calculate_total(results, analysis='cannabinoids')
        
        # Calculate total THC and total CBD.
        obs['total_thc'] = calculate_total_cannabinoid(results)
        obs['total_cbd'] = calculate_total_cannabinoid(results, base_key='cbd', acid_key='cbda')

    # Get foreign matter results.
    for page in report.pages:
        text = page.extract_text()
        if 'Foreign Matter Analysis' in text:
            analyses.append('foreign_matter')
            lines = text.split('\n')
            for row in reversed(lines):
                if 'Foreign Matter' in row:
                    values = row.replace('Foreign Matter', '').strip().split(' ')
                    status = values[-1]
                    value = values[0]
                    note = None
                    if len(values) > 2:
                        note = ' '.join(values[1:-1])
                    if str(status).lower() == 'fail':
                        obs['status'] = 'Fail'
                    results.append({
                        'analysis': 'foreign_matter',
                        'key': 'foreign_matter',
                        'name': 'Foreign Matter',
                        'value': value,
                        'status': status,
                        'note': note,
                    })
                    break
            break

    # Get moisture content and water activity.
    for page in report.pages:
        text = page.extract_text()
        if 'Moisture Content' in text:
            lines = text.split('\n')
            for line in lines:
                if line.startswith('Moisture Content (%)'):
                    analyses.append('moisture_content')
                    value = line.split(' ')[-1].replace('%', '')
                    obs['moisture_content'] = convert_to_numeric(value)
                elif line.startswith('Water Activity'):
                    analyses.append('water_activity')
                    values = line.split(' ')
                    obs['water_activity'] = convert_to_numeric(values[2])
                    if str(values[-1]).lower() != 'pass':
                        obs['status'] = values[-1]
                    break
            break

    # Get microbe results.
    for page in report.pages:
        text = page.extract_text()
        if 'Microbial Analysis' in text:
            analyses.append('microbes')
            lines = text.split('\n')
            rows = extract_lines(lines, 'Microbial Analysis', 'Notes')
            rows = extract_lines(rows, 'Analyte', 'DET = ')
            for line in rows:
                if 'Analysis' in line or 'Analyte' in line or ' of ' in line or 'Organism' in line:
                    continue
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) == 2:
                    limit = None
                else:
                    try:
                        limit = convert_to_numeric(str(values[1]).replace(',', ''))
                    except:
                        break
                results.append({
                    'analysis': 'microbes',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(values[0]),
                    'limit': limit,
                    'status': values[-1],
                })
            break

    # Get mycotoxin results.
    for page in report.pages:
        text = page.extract_text()
        if 'Mycotoxin Analysis' in text:
            analyses.append('mycotoxins')
            lines = text.split('\n')
            rows = extract_lines(lines, 'Mycotoxin', 'ND =')
            rows = extract_lines(rows, None, 'Note')
            for line in rows:
                if 'Analysis' in line or 'Analyte' in line or ' of ' in line:
                    continue
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                results.append({
                    'analysis': 'mycotoxins',
                    'key': key,
                    'name': name,
                    'value': convert_to_numeric(values[0]),
                    'limit': convert_to_numeric(values[1]),
                    'status': values[-1],
                })
            break

    # Get heavy metal results.
    for page in report.pages:
        text = page.extract_text()
        if 'Heavy Metal Analysis' in text:
            analyses.append('heavy_metals')
            lines = text.split('\n')
            rows = extract_lines(lines, 'Heavy Metal')
            rows = extract_lines(rows, 'Analyte', 'Analysis')
            rows = extract_lines(rows, None, 'Note')
            for line in rows:
                if 'Analysis' in line or 'Analyte' in line or ' of ' in line:
                    continue
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) > 3:
                    cas = values[0]
                else:
                    cas = None
                results.append({
                    'analysis': 'heavy_metals',
                    'key': key,
                    'name': name,
                    'cas': cas,
                    'value': convert_to_numeric(values[-3]),
                    'limit': convert_to_numeric(values[-2]),
                    'status': values[-1],
                })
            break

    # Get pesticide results.
    for page in report.pages:
        text = page.extract_text()
        if 'Pesticide Analysis' in text:
            analyses.append('pesticides')
            lines = text.split('\n')
            rows = extract_lines(lines, 'Pesticide')
            rows = extract_lines(rows, 'Analyte', 'Analysis')
            for line in rows:
                if 'Analysis' in line or 'Analyte' in line or ' of ' in line:
                    continue
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) != 4:
                    continue
                results.append({
                    'analysis': 'pesticides',
                    'key': key,
                    'name': name,
                    'cas': values[0],
                    'value': convert_to_numeric(values[1]),
                    'limit': convert_to_numeric(values[2]),
                    'status': values[3],
                })

    # Get terpene results.
    for page in report.pages:
        text = page.extract_text()
        if 'Terpene Analysis' in text:
            analyses.append('terpenes')
            lines = text.split('\n')
            rows = extract_lines(lines, 'Terpene Analysis')
            rows = extract_lines(rows, 'Analysis')
            rows = extract_lines(rows, 'Analyte', 'Analysis')
            for line in rows:
                if 'Analysis' in line or 'Analyte' in line or ' of ' in line:
                    continue
                first_value = find_first_value(line)
                name = line[:first_value].strip()
                key = parser.analytes.get(snake_case(name), snake_case(name))
                values = line[first_value:].strip().split(' ')
                if len(values) == 2:
                    cas = values[0]
                else:
                    cas = ' '.join(values[0:-1])
                results.append({
                    'analysis': 'terpenes',
                    'key': key,
                    'name': name,
                    'cas': cas,
                    'value': convert_to_numeric(values[-1]),
                })
            break

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
    obs = {**UT_DEPT_OF_AG_AND_FOOD, **obs}
    del obs['fields']
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['analyses'] = json.dumps(list(set(analyses)))
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
# Tested: 2024-06-30 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # [✓] TEST: Parse a current Utah COA.
    doc = r'D:\\data\\public-records\\Utah\\CN24129-6 Garlic Jam Flower_ 3.5g_7g (1).pdf'
    parser = CoADoc()
    coa_data = parse_utah_coa(parser, doc)
    assert coa_data is not None

    # [✓] TEST: Parse historic Utah COAs.
    docs = [
        r'D:\\data\\public-records\\Utah\\F0778 Dragonfly Greenhouse J1_ 230201HB - SERVICE SAMPLE.pdf',
        r'D:\\data\\public-records\\Utah\\F0344 Harvest Jack Herer.pdf',
        r'D:\\data\\public-records\\Utah\\Zion Flower COA - Fatso.pdf',
        r'D:\data\public-records\Utah\P0462 {FAIL} Zion Cultivars Watermelon Soda Shake  3.5g.pdf',
        r'D:\data\public-records\Utah\F0452 Cocomero Gelatti X Grumpz.pdf',
        r'D:\data\public-records\Utah\F0646 Harvest of Utah Mochi X Gelato.pdf',
        r'D:\data\public-records\Utah\P0046 H of U Jack Herer Prepack.pdf',
        r'D:\data\public-records\Utah\F0371 Wholesome Gorilla OG Trim.pdf',
        r'D:\data\public-records\Utah\F0349 Wholesome Ag Kiwi.pdf',
    ]
    for doc in docs:
        parser = CoADoc()
        coa_data = parse_historic_utah_coa(parser, doc)
        assert coa_data is not None
