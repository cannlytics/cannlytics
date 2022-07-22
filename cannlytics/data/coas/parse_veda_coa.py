"""
CoA Doc | A Certificate of Analysis Parser
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/20/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Veda Scientific CoA

Data Points:

    - analyses
    ✓ {analysis}_method
    ✓ analysis_type
    - {analysis}_status
    - classification
    - coa_urls
    ✓ date_tested
    - date_received
    - images
    - lab_results_url
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
    ✓ lab
    - lab_image_url
    - lab_license_number
    - lab_address
    - lab_city
    - lab_county (augmented)
    - lab_state
    - lab_zipcode
    - lab_phone
    - lab_email
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from typing import Any, Optional

# External imports.
# from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import pdfplumber
# from requests import Session

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import snake_case, strip_whitespace

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

if __name__ == '__main__':

    # DEV:
    import itertools
    from cannlytics.data.coas import CoADoc
    from cannlytics.utils.constants import ANALYTES

    # Initialize the CoA paresr.
    parser = CoADoc()

    # Specify where your test CoA lives.
    DATA_DIR = '../../../.datasets/coas'
    coa_pdf = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'

    # Read the PDF.
    pdf_file = pdfplumber.open(coa_pdf)

    # Get the date the CoA was created.
    date_tested = parser.get_pdf_creation_date(pdf_file)

    # ✓ Test detection of Veda Scientific CoAs.
    known_lims = parser.identify_lims(pdf_file, 'veda scientific')
    assert known_lims == 'veda scientific'

    # # Get all table data.
    # tables = []
    # for page in pdf_file.pages:
    #     pdf_tables = page.find_tables()
    #     for t in pdf_tables:
    #         tables += t.extract()
    #         print(t.extract())
        
    # # Get all unique tables and remove empty tables..
    # tables = list(k for k, _ in itertools.groupby(tables))
    # tables = [x for x in tables if not (len(x) == 1 and x[0] == '')]
    # print('Found %i tables' % len(tables))

    # Parse it to the best of our abilities!
    obs = {
        'analyses': [],
        # '{analysis}_method
        # '{analysis}_status
        'coa_urls': [],
        'date_tested': '',
        'date_received': '',
        'images': '',
        'lab_results_url': '',
        'producer': '',
        'product_name': '',
        'product_type': '',
        'results': [],
        'sample_weight': '',
        'total_cannabinoids' : 0,
        'total_thc': 0,
        'total_cbd': 0,
        'total_terpenes': 0,
        'strain_name': '',
        'lab_id': '',
        'lab': 'Veda Scientific',
        'lab_image_url': '',
        'lab_license_number': '',
        'lab_address': '1601 W Central Ave Building A Unit A, Lompoc, CA',
        'lab_street': '1601 W Central Ave Building A Unit A',
        'lab_city': 'Lompoc',
        'lab_county': '', # Augmented
        'lab_state': 'CA',
        'lab_zipcode': '93436',
        'lab_phone': '(805) 324-7728',
        'lab_email': '',
        'lab_website': 'vedascientific.co',
        'lab_latitude': '', # Augmented
        'lab_longitude': '', # Augmented
    }

    # # Get analysis details.
    # table_data = tables[0][0]
    # analysis_details = table_data.replace('\xa0\xa0\xa0\xa0', '\n').split('\n')
    # mm, dd, yyyy = table_data[2].split(':')[-1].strip().split('/')
    # date_tested = f'{yyyy}-{mm}-{dd}'
    # obs['date_tested'] = date_tested
    # obs['analysis_type'] = analysis_details[0]
    # obs['status'] = analysis_details[-1].split(':')[-1].strip().lower()

    # # Get lab license number.
    # lab_details = tables[1][0].replace('\xa0', '\n').split('\n')
    # lab_details = [x.strip() for x in lab_details if x.replace('|', '').strip() != '' ]
    # for detail in lab_details:
    #     if 'license' in detail.lower():
    #         obs['lab_license_number'] = detail.split(':')[-1].strip()
    
    # TODO: Get details from the front page!
    # - sample_name
    # - lab_id
    # - order_number
    # - product_type
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
    # - density
    # - total_thc
    # - total_cbd
    # - total_cannabinoids
    front_page = pdf_file.pages[0]

    # Get all analyte names.
    analyte_names = list(ANALYTES.values())

    # Define all of the analyses.
    analyses = {
        'cannabinoids': {
            'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                        'mg_per_serving', 'mg_per_package'],
            'units': 'mg/g',
        },
        'terpenes': {
            'columns': ['name', 'lod', 'loq', 'mg_g', 'value',
                        'mg_per_serving', 'mg_per_package'],
            'units': 'mg/g',
        },
        'moisture': {
            'columns': ['name', 'value'],
            'units': 'percent',
        },
        'water_activity': {
            'columns': ['name', 'value', 'limit', 'status'],
            'units': 'aW',
        },
        'pesticides': {
            'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
            'units': 'ug/g',
        },
        'mycotoxins': {
            'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
            'units': 'ug/kg',
        },
        'heavy_metals': {
            'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
            'units': 'ug/g',
        },
        'foreign_matter': {
            'columns': ['name', 'limit', 'status'],
            'units': 'percent',
        },
        'microbials': {
            'columns': ['name', 'value', 'status'],
            'units': 'count',
        },
        'residual_solvents': {
            'columns': ['name', 'lod', 'loq', 'limit', 'value', 'status'],
            'units': 'ug/g',
        },
    }

    # Get results page text.
    page_texts = []
    for page in pdf_file.pages:
        page_text = page.extract_text()
        page_text = page_text \
            .replace('\xa0\xa0', '\n') \
            .replace('\xa0', ',') \
            .split('\n')
        page_texts.append(page_text)

    # List analysis names and key identifiers.
    analysis_names = list([x for x in analyses.keys()])
    analysis_keys = [
        x.rstrip('s').replace('_', ' ').title() for x in analysis_names
    ]
    
    # TODO: Get all of the `results` and `{analysis}_method`s!
    current_analysis = None
    methods = []
    for page_text in page_texts:
        for row in page_text:

            # 1. Try to identify analysis.
            parts = row.split(' ')
            value =  snake_case(strip_whitespace(parts[0]))
            key = value.rstrip('s').replace('_', ' ').title()
            print(value)
            if key in analysis_keys:
                print('Working with analysis:', key)
                current_analysis = analysis_names[analysis_keys.index(key)]

            # 2. Try to identify analytes.
            # analyte = snake_case(parts[0])
            # if analyte in analyte_names:
            #     break

            # 3. Try to identify all methods.
            if value == 'method':
                method = ' '.join([x.strip() for x in parts[1:] if x])
                if 'Change:' in method:
                    continue
                method = method.split(':')[0].split(',')[0].strip()
                methods.append(method)

    # Match methods to analyses.
    for method in methods:
        for analysis in analysis_keys:
            if analysis in method:
                key = analysis_keys.index(analysis)
                analysis_name = analysis_names[key]
                obs[f'{analysis_name}_method'] = method
            
    # Standardize and normalize the data.

    # Return the beautiful data!

    # TODO: Test Veda Scientific CoA parsing.
    # parser = CoADoc()
    # data = parse_veda_pdf(parser, coa_pdf)
    # assert data is not None

    # Try to get `lab_image_url`.

    # Try to get `images`

    # TODO: Get the `producer`, `product_name`.

    # Return the sample with a freshly minted sample ID.
    # obs['sample_id'] = create_sample_id(
    #     private_key=producer,
    #     public_key=product_name,
    #     salt=date_tested,
    # )
