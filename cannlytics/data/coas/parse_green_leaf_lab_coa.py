"""
Parse Green Leaf Lab CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/23/2022
Updated: 7/24/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Green Leaf Labs CoA.

Data Points:

    - analyses
    - {analysis}_method
    - analysis_type
    - {analysis}_status
    - classification
    x coa_urls
    - date_tested
    - date_received
    x images
    x lab_results_url
    - producer
    - product_name
    - product_type
    - predicted_aromas
    - results
    - sample_weight
    - status
    - total_cannabinoids (calculated)
    - total_thc
    - total_cbd
    - total_terpenes (calculated)
    - sample_id (generated)
    - strain_name
    - lab_id

Static Data Points:

    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number (should be dynamic)
    ✓ lab_address (should be dynamic)
    ✓ lab_street (should be dynamic)
    ✓ lab_city (should be dynamic)
    - lab_county (augmented)
    ✓ lab_state (should be dynamic)
    ✓ lab_zipcode (should be dynamic)
    ✓ lab_phone (should be dynamic)
    - lab_email
    ✓ lab_website
    - lab_latitude (augmented) (should be dynamic)
    - lab_longitude (augmented) (should be dynamic)

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

# Future work: Make this dynamic to handle multiple lab locations.
# E.g. Green Leaf Lab has a California and an Oregon location.
GREEN_LEAF_LAB = {
    'lab': 'Green Leaf Lab',
    'lab_image_url': 'https://cdn-djjmk.nitrocdn.com/MuWSCTBsUZpIUufaWqGQkErSrYFMxIqD/assets/static/optimized/rev-a199899/wp-content/uploads/2018/12/greenleaf-logo.png',
    'lab_license_number': ' C8-0000078-LIC', # <- Make dynamic.
    'lab_address': '251 Lathrop Way Suites D&E Sacramento, CA 95815', # <- Make dynamic.
    'lab_street': '251 Lathrop Way Suites D&E', # <- Make dynamic.
    'lab_city': 'Sacramento', # <- Make dynamic.
    'lab_county': '', # <- Make dynamic.
    'lab_state': 'CA', # <- Make dynamic.
    'lab_zipcode': '95815', # <- Make dynamic.
    'lab_phone': '916-924-5227', # <- Make dynamic.
    'lab_email': '', # <- Get this data.
    'lab_website': 'https://greenleaflab.org/',
    'lab_latitude': '', # <- Make dynamic.
    'lab_longitude': '', # <- Make dynamic.
}

GREEN_LEAF_LAB_ANALYSES = {
    'cannabinoids': {
        'name': '',
        'columns': [],
        'analytes': [],
    }
}

GREEN_LEAF_LABS_FIELDS = {
    'licensenumber': 'license_number',
    'lab_sample_id': 'lab_id',
    'matrix': 'product_type',
    'batch_size': 'batch_size',
    'sample_size': 'sample_weight',
    'date_sampled': 'date_sampled',
    'date_received': 'date_received',
    'harvesttoprocessing_date': '',
    'product_density': '',
    'overall_batch': 'status',
    'cannabinoids': 'cannabinoids_status',
    'pesticides': 'pesticides_status',
    'water_activity': 'water_activity_status',
    'moisture_content': 'moisture_content_status',
    'terpene_analysis_add_on': 'terpenes_status',
    'microbials': 'microbials_status',
    'metals': 'heavy_metals_status',
    'foreign_material': 'foreign_matter_status',
    'mycotoxins': 'mycotoxins_status',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
}


def parse_greenleaflab_pdf(
        self,
        doc: Any,
        headers: Optional[dict] = None,
        persist: Optional[bool] = False,
    ) -> dict:
    """Parse a Green Leaf Lab CoA PDF.
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
    return self.parse_pdf(
        self,
        doc,
        lims='Green Leaf Lab',
        headers=headers,
        persist=persist,
    )


def get_page_rows(page: Any) -> list:
    """Get the rows a given page.
    Args:
        pdf ():
        index ():
    Returns:
        (list): A list of text.
    """
    txt = page.extract_text()
    txt = txt.replace('\xa0\xa0', '\n').replace('\xa0', ',')
    return txt.split('\n')


if __name__ == '__main__':

    # DEV:
    from cannlytics.data.coas import CoADoc
    from cannlytics.utils.constants import ANALYTES

    # Initialize the CoA parser.
    parser = CoADoc()

    # Specify where your test CoA lives.
    DATA_DIR = '../../../.datasets/coas'
    coa_pdf = f'{DATA_DIR}/Raspberry Parfait.pdf'

    # Read the PDF.
    obs = {}
    report = pdfplumber.open(coa_pdf)
    # Optional: laparams={ "line_overlap": 1 }

    # Get the date the CoA was created.
    date_tested = parser.get_pdf_creation_date(report)

    # ✓ Test detection of Green Leaf Labs CoAs.
    known_lims = parser.identify_lims(report, 'greenleaflabs')
    assert known_lims == 'greenleaflabs'

    # Get all of the rows.
    all_rows = []
    for page in report.pages:
        rows = get_page_rows(page)
        for row in rows:
            if row in all_rows:
                pass
            else:
                all_rows.append(row)

    # Get a list of analytes.
    standard_analytes = list(set(ANALYTES.values()))
    
    # TODO: Augment with Green Leaf Labs specific analytes.
    
    # TODO: Iterate over all rows to get `analyses`, `results`, and
    # all sample details in one shot!
    analyses = []
    results = []
    for row in all_rows:
        snake = snake_case(row)
        for analyte in standard_analytes:
            if snake.startswith(analyte):
                # See if row starts with a standard analyte.
                print('Identified:', analyte)
                result = {}
                # TODO: Format `result`

                # TODO: Append `analysis` to `analyses`


        # Optional: Is there any way to determine the `{analysis}_method`?

        
        # TODO: Determine if the row is a standard detail.


    # Finish data collection with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=obs['producer'],
        public_key=obs['product_name'],
        salt=date_tested,
    )


    #-------------------------------------------------------------------
    # TEST: Parse a CoA PDF.
    # from cannlytics.data.coas import CoADoc
    # parser = CoADoc()
    # data = parse_greenleaflab_pdf(parser, coa_pdf)
    # assert data is not None
