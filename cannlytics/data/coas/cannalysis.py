"""
Parse Cannalysis CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/2/2022
Updated: 9/13/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Cannalysis CoA PDF.

Data Points:

    - analyses
    ✓ {analysis}_method
    ✓ {analysis}_status
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    ✓ date_produced
    ✓ batch_size
    ✓ lab_id
    - lab_results_url
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ product_name
    ✓ product_type
    ✓ results
    ✓ sample_id
    ✓ sample_size
    ✓ total_cannabinoids
    ✓ total_cbd
    ✓ total_thc
    ✓ total_terpenes

FIXME:

    - [ ] Occasional: Unknown string format "-02/18/202 11919" from OCR.
    - [ ] Occasional: list index out of range

"""
# Standard imports.
from datetime import datetime
import json
import re
from typing import Any, Optional
import warnings

# External imports.
import pandas as pd
import pdfplumber
from PIL import Image

# Internal imports.
from cannlytics.data.data import (
    create_sample_id,
    find_first_value,
)
from cannlytics.utils.constants import ANALYSES, ANALYTES, STANDARD_FIELDS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
)

# Convert `DecompressionBombWarning` into an error.
warnings.simplefilter('error', Image.DecompressionBombWarning)

# It is assumed that the lab has the following details.
CANNALYSIS =  {
    'coa_algorithm': 'cannalysis.py',
    'coa_algorithm_entry_point': 'parse_cannalysis_coa',
    'url': 'www.cannalysis.com',
    'lims': 'Cannalysis',
    'lab': 'Cannalysis',
    'lab_license_number': 'C8-0000012-LIC',
    'lab_image_url': 'https://www.cannalysis.com/img/img.c5effdd3.png',
    'lab_address': '1801 Carnegie Ave, Santa Ana CA 92705',
    'lab_street': '1801 Carnegie Ave',
    'lab_city': 'Santa Ana',
    'lab_county': 'Orange',
    'lab_state': 'CA',
    'lab_zipcode': '92705',
    'lab_latitude': 33.712190,
    'lab_longitude': -117.844650,
    'lab_phone': '949-329-8378',
    'lab_email': 'support@cannalysislabs.com',
    'lab_website': 'www.cannalysis.com',
}

# It is assumed that the CoA has the following parameters.
# Dimensions are percentages (x0, y0) to (x1, y1).
CANNALYSIS_COA = {
    'coa_distributor_area': [0, 0.66, 0.35, 0.725],
    'coa_producer_area': [0, 0.725, 0.35, 0.8],
    'coa_page_area': [
        [0, 0.1, 0.5, 0.9],
        [0.5, 0.1, 1.0, 0.9],
    ],
    'coa_sample_details_area': [
        [0, 0.15, 0.35, 0.9],
        [0.35, 0.15, 1.0, 0.9],
    ],
    'coa_result_fields': [
        'name',
        'value',
        'lod',
        'loq', 
        'limit',
        'status',
    ],
    'coa_skip_fields': [
        'ADDITIONAL',
        'Total',
        'undergone a calculation',
        'Individual Analyte',
        '   ',
        'AS',
        'Batch:',
        'ACCORDANCE',
        'criteria',
    ],
}


def parse_cannalysis_coa(
        parser,
        doc: Any,
        cleanup: Optional[bool] = True,
        resolution: Optional[int] = 180,
        temp_path: Optional[str] = '/tmp',
        coa_pdf: Optional[str] = None,
        **kwargs,
    ) -> Any:
    """Parse a Cannalysis CoA PDF.
    Args:
        parser (CoADoc): A CoADoc parsing client.
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        cleanup (bool): Whether or not to remove the files generated
            during OCR, `True` by default (optional).
        temp_path (str): A temporary directory to use for OCR.
        resolution (int): The resolution of rendered PDF images,
            180 by default (optional).
        coa_pdf (str): A filename to use for the `coa_pdf` field (optional).
    Returns:
        (dict): The sample data.
    """

    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = coa_pdf or doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = coa_pdf or report.stream.name.replace('\\', '/').split('/')[-1]

    # Get the QR code from the last page.
    # Note: After OCR, QR code decoding raises warning:
    # DecompressionBombWarning: Image size (154554704 pixels) exceeds
    # limit of 89478485 pixels, could be decompression bomb DOS attack.
    # try:
    #     obs['lab_results_url'] = parser.find_pdf_qr_code_url(report)
    # except Image.DecompressionBombWarning:
    #     obs['lab_results_url'] = ''

    # TODO: Get the image data, `images` and `image_url`.

    # Get the lab specifics.
    coa_parameters = CANNALYSIS_COA
    standard_result_fields = coa_parameters['coa_result_fields']
    skip_fields = coa_parameters['coa_skip_fields']

    # Get the front page and page dimensions.
    front_page = report.pages[0]
    w, h = front_page.width, front_page.height

    # Get the distributor area.
    x0, y0, x1, y1 = tuple(coa_parameters['coa_distributor_area'])
    coa_distributor_area = (x0 * w, y0 * h, x1 * w, y1 * h)

    # Get the producer area.
    x0, y0, x1, y1 = tuple(coa_parameters['coa_producer_area'])
    coa_producer_area = (x0 * w, y0 * h, x1 * w, y1 * h)

    # Get the page areas.
    coa_page_area = []
    for dimensions in coa_parameters['coa_page_area']:
        x0, y0, x1, y1 = tuple(dimensions)
        area = (x0 * w, y0 * h, x1 * w, y1 * h)
        coa_page_area.append(area)    

    # Get the sample details areas.
    coa_sample_details_area = []
    for dimensions in coa_parameters['coa_sample_details_area']:
        x0, y0, x1, y1 = tuple(dimensions)
        area = (x0 * w, y0 * h, x1 * w, y1 * h)
        coa_sample_details_area.append(area)

    # Get the distributor data based on page area.
    crop = front_page.within_bbox(coa_distributor_area)
    lines = crop.extract_text().split('\n')[1:]
    lines = [x.replace('  ', ' ').strip() for x in lines]
    obs['distributor_address'] = ' '.join([lines[0], lines[1]])
    obs['distributor_license_number'] = lines[-1].replace('License:', '').strip()

    # Get the producer data based on page area.
    crop = front_page.within_bbox(coa_producer_area)
    lines = crop.extract_text().split('\n')[1:]
    lines = [x.replace('  ', ' ').strip() for x in lines]
    obs['producer_address'] = ', '.join([lines[0], lines[1]])
    obs['producer_license_number'] = lines[-1].replace('License:', '').strip()

    # Optional: Is there any way to identify the `producer` and
    # `distributor` with their license numbers? Query Cannlytics API?

    # Check if OCR is required then re-run the routine.
    line = lines[0]
    if re.match(r'^\(cid:\d+\)', line):
        temp_file = f'{temp_path}/ocr-coa.pdf'
        parser.pdf_ocr(
            report.stream.name,
            temp_file,
            temp_path=temp_path,
            resolution=resolution,
            cleanup=cleanup,
        )
        return parse_cannalysis_coa(
            parser,
            report,
            cleanup=cleanup,
            resolution=resolution,
            temp_path=temp_path,
            coa_pdf=report.stream.name,
            **kwargs,
        )

    # Get the sample details.
    analyses = []
    for area in coa_sample_details_area:
        crop = front_page.within_bbox(area)
        lines = crop.extract_text().split('\n')
        analysis = None
        collect = False
        field = None
        for line in lines:

            # Determine any fields.
            line = line.replace('  ', ' ').strip()
            potential_field = STANDARD_FIELDS.get(snake_case(line))
            if potential_field:
                field = potential_field
                collect = True
                continue
            if collect and field:
                if field == 'date_collected':
                    dates = tuple(line.split(', '))
                    obs['date_collected'] = dates[0]
                    obs['date_received'] = dates[1]
                elif field == 'batch_size':
                    dates = tuple(line.split(', '))
                    obs['batch_size'] = dates[0]
                    obs['sample_size'] = dates[1]
                else:
                    obs[field] = line
                collect = False
                field = None
            
            # Collect the data.
            elif collect and analysis:
                obs[f'{analysis}_status'] = line.lower()
                collect = False
                analysis = None

            # Determine analyses.
            # FIXME: Not all analyses (e.g. cannabinoids) are being identified.
            potential_analysis = ANALYSES.get(line)
            if potential_analysis:
                analysis = potential_analysis
                analyses.append(potential_analysis)
                collect = True
                continue

    # Get the product name if it wasn't collected from the details.
    # Hot-fix: OCR misreads "Pass" as "G=>". How does OCR read "Fail"?
    if obs.get('product_name') is None:
        text = front_page.extract_text().split('Testing')[-1].split('\n')
        text = [x.replace('  ', ' ') for x in text if x.strip()]
        obs['product_name'] = text[0].replace('G=>', '').strip()

    # Get all page text, from the 2nd page on.
    results, date_tested = [], []
    for page_number, page in enumerate(report.pages[1:]):
        for area in coa_page_area:

            # Create cropped area.
            analysis, units = None, None
            crop = page.within_bbox(area)
            lines = crop.extract_text().split('\n')

            # Parse results from each line.
            for line in lines:

                # Strip whitespace for easy line recognition.
                line_text = line.replace(' ', '')

                # Identify the analysis (# FIXME: only works for 1st column).
                # Note: Hot-Fix for foreign matter.
                if 'ANALYSIS' in line or 'FILTH' in line:
                    analysis = line.split(' ANA')[0].title()
                    analysis = ANALYSES.get(analysis)

                # Identify the columns (unnecessary).
                elif 'ANALYTE' in line:
                    # parts = [snake_case(x) for x in line.split(' ')]
                    # columns = [standard_fields.get(x, x) for x in parts]
                    continue

                # Identify the units (# FIXME: only works for 1st column).
                elif 'UNIT' in line:
                    units = line.split(':')[-1].strip()
                    units = line[line.find('(') + 1: line.find(')')]
                    if page_number == 0:
                        units = 'percent' # Convert mg/g to percent.

                # Identify the instrument as the `method`.
                elif 'Instrument:' in line:
                    method = line.split('Instrument: ')[-1].split(' Sample Analyzed:')[0]
                    obs[f'{analysis}_method'] = method
                elif 'Method:' in line:
                    continue

                # Get the totals.
                elif 'TOTAL' in line and '@' not in line:
                    parts = line.split(':')
                    key = snake_case(parts[0].lower())
                    value = parts[1].strip()
                    if '(' in value:
                        value = value[value.find('(') + 1: value.find(')')]
                        value = convert_to_numeric(value, strip=True)
                    obs[key] = value

                # Get the dates tested.
                # FIXME: This is highly suboptimal and causes many errors.
                elif 'SampleApproved' in line_text:
                    date_time = line_text.split('Approved')[-1]
                    date_time = date_time.replace(':', '') \
                        .replace('.', '') \
                        .replace(',', '') \
                        .replace('-', '') \
                        .replace('_', '')
                    date, at = date_time[:10], date_time[10:]
                    try:
                        if len(at) != 4:
                            date_time = pd.to_datetime(date)
                        else:
                            date_time = pd.to_datetime(' '.join([date, at]))
                        date_tested.append(date_time)
                    except:
                        pass

                # Skip informational rows.
                elif any(s in line for s in skip_fields):
                    continue

                # End at the end of the report.
                elif line_text.startswith('Thisreport'):
                    break

                # Get the results.
                else:

                    # Remove extraneous results.
                    text = line.replace('mg/g', '').replace(' aw ', ' ')
                    text = re.sub('[\(\[].*?[\)\]]|=', '', text)
                    text = text.replace('  ', ' ').strip()

                    # Standardize analytes.
                    first_value = find_first_value(text)
                    name = text[:first_value].replace('\n', ' ').strip()
                    analyte = ANALYTES.get(name, snake_case(name))

                    # Hot-fix to skip non-sensical analytes.
                    if len(analyte) <= 1:
                        continue

                    # Create a result object.
                    result = {
                        'analysis': analysis,
                        'key': analyte,
                        'name': name,
                        'units': units,
                    }

                    # Add keys / values to the result, using standard fields.
                    values = text[first_value:].strip().split(' ')
                    values = [x for x in values if x]
                    try:
                        for i, v in enumerate(values):
                            key = standard_result_fields[i + 1]
                            value = convert_to_numeric(v)
                            if page_number == 0: # Convert mg/g to percent.
                                try:
                                    value = round(0.1 * value, 2)
                                except:
                                    pass
                            result[key] = value
                    except IndexError:
                        continue

                    # Record the result.
                    results.append(result)

    # Close the report.
    report.close()

    # Get the latest tested at date.
    obs['date_tested'] = max(date_tested)

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass

    # Finish data collection with a freshly minted sample ID.
    obs['analyses'] = list(set(analyses))
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=obs['date_tested'], # Note: The standard is `producer`.
    )
    obs['coa_parsed_at'] = datetime.now().isoformat()
    return {**CANNALYSIS, **obs}


# === Test ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # [✓] TEST: Parse a Cannalysis CoA PDF.
    # parser = CoADoc()
    # doc = '../../../tests/assets/coas/MothersMilk.pdf'
    # lab = parser.identify_lims(doc, lims={'Cannalysis': CANNALYSIS})
    # assert lab == 'Cannalysis'
    # data = parse_cannalysis_coa(parser, doc)
    # assert data is not None

    # [✓] TEST: Parse a Cannalysis CoA PDF after OCR is applied.
    # parser = CoADoc()
    # doc = '../../../.datasets/tests/test.pdf'
    # lab = parser.identify_lims(doc, lims={'Cannalysis': CANNALYSIS})
    # assert lab == 'Cannalysis'
    # data = parse_cannalysis_coa(parser, doc)
    # assert data is not None

    # [✓] TEST: Parse a Cannalysis CoA PDF, applying OCR.
    # parser = CoADoc()
    # doc = '../../../.datasets/tests/mist.pdf'
    # temp_path = '../../../.datasets/tests/tmp'
    # data = parser.parse_pdf(doc, temp_path=temp_path)
    # assert data is not None
