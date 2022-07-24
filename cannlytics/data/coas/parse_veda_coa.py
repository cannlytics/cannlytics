"""
Parse Veda Scientific CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/24/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Veda Scientific CoA.

Data Points:

    ✓ analyses
    ✓ {analysis}_method
    ✓ analysis_type
    - {analysis}_status
    - classification
    x coa_urls
    ✓ date_tested
    - date_received
    x images
    x lab_results_url
    - producer
    - product_name
    - product_type
    - predicted_aromas
    - results
    - sample_weight
    ✓ status
    - total_cannabinoids (calculated)
    - total_thc
    - total_cbd
    - total_terpenes (calculated)
    - sample_id (generated)
    - strain_name
    - lab_id

Static Data Points:

    ✓ lab
    - lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    ✓ lab_street
    ✓ lab_city
    - lab_county (augmented)
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    - lab_email
    ✓ lab_website
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import ANALYSES, ANALYTES
from cannlytics.utils.utils import snake_case, split_list, strip_whitespace


VEDA = {
    'lab': 'Veda Scientific',
    'lab_image_url': '', # <- Get this data.
    'lab_license_number': '', # <- Get this data.
    'lab_address': '1601 W Central Ave Building A Unit A, Lompoc, CA',
    'lab_street': '1601 W Central Ave Building A Unit A',
    'lab_city': 'Lompoc',
    'lab_county': '', # <- Get this data.
    'lab_state': 'CA',
    'lab_zipcode': '93436',
    'lab_phone': '(805) 324-7728',
    'lab_email': '', # <- Get this data.
    'lab_website': 'vedascientific.co',
    'lab_latitude': '',# <- Get this data.
    'lab_longitude': '',# <- Get this data.
}

# Define all of the analyses.
VEDA_SCIENTIFIC_ANALYSES = {
    'cannabinoids': {
        'name': 'Cannabinoids',
        'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                    'mg_per_serving', 'mg_per_package'],
        'units': 'mg/g',
        'analytes': [
            'cbd',
            'cbda',
            'cbdv',
            'cbdva',
            'cbg',
            'cbga',
            'cbl',
            'cbc',
            'cbca',
            'cbn',
            'cbna',
            'delta_9_thc',
            'thca',
            'delta_8_thc',
            'thcv',
            'thcva',
        ],
    },
    'terpenes': {
        'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                    'mg_per_serving', 'mg_per_package'],
        'units': 'mg/g',
        'analytes': [],
    },
    'moisture': {
        'columns': ['name', 'value'],
        'units': 'percent',
        'analytes': [],
    },
    'water_activity': {
        'columns': ['name', 'value', 'limit', 'status'],
        'units': 'aW',
        'analytes': [],
    },
    'pesticides': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
        'analytes': [],
    },
    'mycotoxins': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/kg',
        'analytes': [],
    },
    'heavy_metals': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
        'analytes': [],
    },
    'foreign_matter': {
        'analytes': [
            'mold',
        ],
        'columns': ['name', 'limit', 'status'],
        'units': 'percent',
        'analytes': [],
    },
    'microbials': {
        'columns': ['name', 'value', 'status'],
        'units': 'count',
        'analytes': [],
    },
    'residual_solvents': {
        'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
        'units': 'ug/g',
        'analytes': [],
    },
}


def parse_veda_pdf(
        self,
        doc: Any,
        headers: Optional[dict] = None,
        persist: Optional[bool] = False,
    ) -> dict:
    """Parse a Veda Scientific CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
        headers (dict): Headers for HTTP requests.
        persist (bool): Whether to persist the session.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """
    # TODO: Implement!!!
    # return self.parse_pdf(
    #     self,
    #     doc,
    #     lims='TagLeaf LIMS',
    #     headers=headers,
    #     persist=persist,
    # )
    raise NotImplementedError


def get_page_rows(
        pdf_file: Any,
        index: list,
        analytes: dict,
    ) -> list:
    """Get the rows a given page.
    Split long rows at the first analyte!
    Args:

    Returns:
    """
    analyte_keys = list(set(analytes.keys()))
    analyte_values = list(set(analytes.values()))
    page_rows, texts = [], []
    for i in index:
        page = pdf_file.pages[i]
        text = page.extract_text()
        text = text \
            .replace('\xa0\xa0', '\n') \
            .replace('\xa0', ',') \
            .split('\n')
        texts.append(text)
    
    # TODO: Split into separate function.
    for text in texts:
        for row in text:
            parts = row.split(' ')
            initial_value = parts[0]
            analyte_key =  snake_case(strip_whitespace(initial_value))
            if initial_value in analyte_values:
                analyte_key = analytes[analysis_name]
            if analyte_key in analyte_keys:
                second_index = None
                for i, part in enumerate(parts[1:]):
                    second_key = snake_case(strip_whitespace(part))
                    if second_key in analyte_keys:
                        second_index = i + 1
                        break
                if second_index is None:
                    page_rows.append(parts)
                else:
                    double_rows = split_list(parts, second_index)
                    page_rows.append(double_rows[0])
                    page_rows.append(double_rows[1])
            else:
                page_rows.append(parts)
    return page_rows


if __name__ == '__main__':

    # DEV:
    import itertools
    from cannlytics.data.coas import CoADoc
    from cannlytics.utils.constants import ANALYTES

    # Initialize the CoA parser.
    parser = CoADoc()

    # Specify where your test CoA lives.
    DATA_DIR = '../../../.datasets/coas'
    coa_pdf = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'

    # Read the PDF.
    report = pdfplumber.open(coa_pdf)

    # Get the date the CoA was created.
    date_tested = parser.get_pdf_creation_date(report)

    # ✓ Test detection of Veda Scientific CoAs.
    known_lims = parser.identify_lims(report, 'veda scientific')
    assert known_lims == 'veda scientific'

    # Veda Scientific parameters.
    page_columns = 2

    # Get the header and footer.
    p0 = report.pages[0]
    top = p0.lines[0]
    bottom = p0.lines[-1]

    # Get the header text.
    y0 = p0.height
    crop = p0.within_bbox((0, 0, p0.width / 2, 300))
    text = crop.extract_text()
    print(text)

    # Get the footer text.
    crop = p0.within_bbox((0, 360, p0.width, 420))
    text = crop.extract_text()

    # FIXME: Parse tables smarter!

    # Get all table data.
    # tables = []
    # for page in pdf_file.pages:
    #     pdf_tables = page.find_tables()
    #     for t in pdf_tables:
    #         tables += t.extract(
    #             x_tolerance=1,
    #             y_tolerance=1,
    #         )
    # print(tables)
        
    # Get all unique tables and remove empty tables.
    tables = list(k for k, _ in itertools.groupby(tables))
    tables = [x for x in tables if not (len(x) == 1 and x[0] == '')]

    # Parse observation to the best of our abilities!
    # Start with known Veda Scientific data and the
    # fields that are known to be blank.
    obs = {
        'coa_urls': [],
        'images': [],
        'lab_results_url': '',
    }

    # Get all analyte names.
    analyte_keys = list(set(ANALYTES.keys()))
    analyte_values = list(set(ANALYTES.values()))

    # List analysis names and key identifiers.
    analysis_names = list([x for x in VEDA_SCIENTIFIC_ANALYSES.keys()])
    analysis_keys = [
        x.rstrip('s') for x in analysis_names
    ]

    # TODO: Try to get all sample details from the front page!
    front_page_rows = get_page_rows(report, index=[0], analytes=ANALYTES)

    # FIXME: Try to read the front page in quadrants.

    # TODO: Get the `producer`, `product_name`.
    for row in front_page_rows:
        initial_value = row[0].lower()

        if initial_value == 'business':
            second_index = row[1:].index('Business')
            distributor = ' '.join(row[2:second_index])
            producer = ' '.join(row[second_index + 1:])

        if 'License' in row and 'Number' in row:
            second_index = row.index('Number')



    product_name = ''

    # - product_name
    # - product_type 
    # - lab_id
    # - order_number
    # - batch_number
    # - lab_metrc_id
    # - metrc_id
    # - metrc_ids = [lab_metrc_id, metrc_id]

    # - date_collected
    # - date_received

    # - batch_size
    # - sample_size
    # - serving_size
    # - servings_per_package
    # - density -> sample_weight

    # - total_thc
    # - total_cbd
    # - total_cannabinoids

    # - producer
    # - producer_license_number
    # - producer_address
    # - producer_street
    # - producer_city
    # - producer_state
    # - producer_zipcode
    # - producer_longitude (augmented)
    # - producer_latitude (augmented)

    # Get all page rows.
    page_rows = front_page_rows
    index = range(1, len(report.pages))
    page_rows += get_page_rows(report, index=index, analytes=ANALYTES)

    # Get analysis details.
    table_data = tables[0][0]
    analysis_details = table_data.replace('\xa0\xa0\xa0\xa0', '\n').split('\n')
    mm, dd, yyyy = analysis_details[2].split(':')[-1].strip().split('/')
    date_tested = f'{yyyy}-{mm}-{dd}'
    obs['date_tested'] = date_tested
    obs['analysis_type'] = analysis_details[0]
    obs['status'] = analysis_details[-1].split(':')[-1].strip().lower()

    # Get lab license number.
    table_data = tables[1][0]
    lab_details = table_data.replace('\xa0', '\n').split('\n')
    lab_details = [x.strip() for x in lab_details if x.replace('|', '').strip() != '' ]
    for detail in lab_details:
        if 'license' in detail.lower():
            obs['lab_license_number'] = detail.split(':')[-1].strip()

    # Get all of the `results` and `{analysis}_method`s!
    current_analysis = None
    collected_analytes = []
    analyses = []
    methods = []
    results = []
    for row in page_rows:

        # Try to get all sample details.

        # Try to identify analysis.
        initial_value = row[0].replace(',', '')
        analyte_key =  snake_case(strip_whitespace(initial_value))
        analysis_key = analyte_key.rstrip('s') # replace('_', ' ').title()
        print(row)
        if analysis_key in analysis_keys:
            current_analysis = analysis_names[
                analysis_keys.index(analysis_key)
            ]
            print('Current analysis:', current_analysis)
            analyses.append(current_analysis)
        
        # Handle Aspergillus and totals.
        elif initial_value == 'Total' or initial_value == 'Aspergillus':
            analyte_key = ' '.join([analyte_key, snake_case(row[1])])
            initial_value = ' '.join([initial_value, row[1]])

        # Try to identify analytes.
        if analyte_key in analyte_keys:
            
            # Find the analyte columns (this can probably be improved).
            analyte_columns = ANALYSES.get(current_analysis)

            # Collect results if the analyte hasn't been collected.
            if analyte_key in collected_analytes:
                continue
            else:
                print('%s analyte:' % current_analysis, initial_value)
                collected_analytes.append(analyte_key)
                result = {'analyte': analyte_key}
                for i, value in enumerate(row):
                    analyte_column = analyte_columns[i]
                    result[analyte_column] = value
                results.append(result)

                # TODO: Match result `analysis` afterwards?
                # 'analysis': '',

        # Try to identify all methods.
        if analyte_key == 'method':
            method = ' '.join([x.strip() for x in row[1:] if x])
            if 'Change:' in method:
                continue
            method = method.split(':')[0].split(',')[0].strip()
            methods.append(method)

    # Match methods to analyses.
    for method in methods:
        for analysis_key in analysis_keys:
            analysis_name = analysis_key.replace('_', ' ').title()
            if analysis_name in method:
                obs[f'{analysis_key}_method'] = method
            
    # Standardize and normalize the data.
    obs['date_tested'] = date_tested
    obs['results'] = results
    obs['analyses'] = list(set(analyses))

    # Return the sample with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=producer,
        public_key=product_name,
        salt=date_tested,
    )

    # TODO: Test Veda Scientific CoA parsing.
    # parser = CoADoc()
    # data = parse_veda_pdf(parser, coa_pdf)
    # assert data is not None
