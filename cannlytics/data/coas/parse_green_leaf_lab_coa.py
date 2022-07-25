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

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
    ✓ batch_size
    x coa_urls
    ✓ date_harvested
    ✓ date_tested
    ✓ date_received
    ✓ date_sampled
    ✓ distributor
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ distributor_license_number
    x images
    ✓ image_data
    x lab_results_url
    ✓ metrc_lab_id
    ✓ metrc_source_id
    ✓ producer
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
    ✓ producer_license_number
    ✓ product_name
    ✓ product_type
    - results
    ✓ sample_weight
    ✓ sample_size
    ✓ sampling_method
    ✓ status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    ✓ sample_id (generated)
    - strain_name
    ✓ lab_id

Static Data Points:

    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number (should be dynamic)
    ✓ lab_address (should be dynamic)
    ✓ lab_street (should be dynamic)
    ✓ lab_city (should be dynamic)
    ✓ lab_county (augmented)
    ✓ lab_state (should be dynamic)
    ✓ lab_zipcode (should be dynamic)
    ✓ lab_phone (should be dynamic)
    - lab_email
    ✓ lab_website
    ✓ lab_latitude (augmented) (should be dynamic)
    ✓ lab_longitude (augmented) (should be dynamic)

"""
# Standard imports.
import re
from typing import Any, Optional

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import ANALYSES, ANALYTES
from cannlytics.utils.utils import snake_case, split_list, strip_whitespace


GREEN_LEAF_LAB_ANALYSES = {
    'cannabinoids': {
        'key': 'cannabinoids',
        'name': 'Potency Analysis by HPLC',
        'columns': [],
        'analytes': [],
    },
    'pesticides': {
        'key': 'pesticides',
        'name': 'Pesticide Analysis by GCMS/LCMS',
        'columns': [],
        'analytes': [],
    },
    'water_activity': {
        'key': 'water_activity',
        'name': 'Water Activity by Aqua Lab',
        'columns': [],
        'analytes': [],
    },
    'moisture_content': {
        'key': 'moisture_content',
        'name': 'Moisture by Moisture Balance',
        'columns': [],
        'analytes': [],
    },
    'terpene_analysis_add_on': {
        'key': 'terpenes',
        'name': 'Terpene Analysis by GCMS',
        'columns': [],
        'analytes': [],
    },
    'microbials': {
        'key': 'microbials',
        'name': 'Microbials by PCR',
        'columns': [],
        'analytes': [],
    },
    'metals': {
        'key': 'heavy_metals',
        'name': 'Metals Analysis by ICPMS',
        'columns': [],
        'analytes': [],
    },
    'foreign_material': {
        'key': 'foreign_matter',
        'name': 'Filth and Foreign Material Inspection by Magnification',
        'columns': [],
        'analytes': [],
    },
    'mycotoxins': {
        'key': 'mycotoxins',
        'name': 'Mycotoxins by LCMSMS',
        'columns': [],
        'analytes': [],
    },
}

GREEN_LEAF_LABS_FIELDS = {
    'licensenumber': 'lab_license_number',
    'lab_sample_id': 'lab_id',
    'matrix': 'product_type',
    'batch_size': 'batch_size',
    'sample_size': 'sample_size',
    'date_sampled': 'date_sampled',
    'date_received': 'date_received',
    'harvesttoprocessing_date': 'date_harvested',
    'product_density': 'sample_weight',
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
    'sampling_method': 'sampling_method',
    'Test RFID': 'metrc_lab_id',
    'Source RFID': 'metrc_source_id',
    'Lab Sample ID': 'lab_id',
    'Sampling Method/SOP': 'sampling_method',
    'Source Batch ID': 'batch_id',
    'Matrix': 'product_type',
    'Batch Size': 'batch_size',
    'Sample Size': 'sample_size',
    'Date Sampled': 'date_sampled',
    'Date Received': 'date_received',
    'Harvest/Processing Date': 'date_harvested',
    'Product Density': 'sample_weight',
}

# Future work: Make this dynamic to handle multiple lab locations.
# E.g. Green Leaf Lab has a California and an Oregon location.
GREEN_LEAF_LAB = {
    'analyses': GREEN_LEAF_LAB_ANALYSES,
    'coa_fields': GREEN_LEAF_LABS_FIELDS,
    'coa_parsing_algorithm': 'parse_green_leaf_lab_pdf',
    'coa_qr_code_index': None,
    'coa_image_index': 2,
    'lab': 'Green Leaf Lab',
    'lab_image_url': 'https://cdn-djjmk.nitrocdn.com/MuWSCTBsUZpIUufaWqGQkErSrYFMxIqD/assets/static/optimized/rev-a199899/wp-content/uploads/2018/12/greenleaf-logo.png',
    'lab_license_number': ' C8-0000078-LIC', # <- Make dynamic.
    'lab_address': '251 Lathrop Way Suites D&E Sacramento, CA 95815', # <- Make dynamic.
    'lab_street': '251 Lathrop Way Suites D&E', # <- Make dynamic.
    'lab_city': 'Sacramento', # <- Make dynamic.
    'lab_county': 'Sacramento', # <- Make dynamic.
    'lab_state': 'CA', # <- Make dynamic.
    'lab_zipcode': '95815', # <- Make dynamic.
    'lab_phone': '916-924-5227', # <- Make dynamic.
    'lab_email': '', # <- Make dynamic.
    'lab_website': 'https://greenleaflab.org/',
    'lab_latitude': '38.596060', # <- Make dynamic.
    'lab_longitude': '-121.459870', # <- Make dynamic.
}


def parse_green_leaf_lab_pdf(
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


def get_page_rows(page: Any, **kwargs) -> list:
    """Get the rows a given page.
    Args:
        page (Page): A pdfplumber page containing rows to extract.
    Returns:
        (list): A list of text.
    """
    txt = page.extract_text(**kwargs)
    txt = txt.replace('\xa0\xa0', '\n').replace('\xa0', ',')
    return txt.split('\n')


if __name__ == '__main__':

    # Test parsing a Green Leaf Lab CoA
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
    p0 = report.pages[0]

    # ✓ Test detection of Green Leaf Labs CoAs.
    lab = 'Green Leaf Lab'
    known_lims = parser.identify_lims(report, lab)
    assert known_lims == lab
    y, x = p0.height, p0.width
    header_area = (0, 0, x, y * 0.25)
    footer_area = (0, y * 0.875, x, y)
    page_area = (0, y * 0.25, x, y * 0.875)
    sample_details_area = (0, y * 0.16, x, y * 0.26)
    distributor_area = (0, y * 0.1, x * 0.4, y * 0.18)
    producer_area = (x * 0.4, y * 0.1, x, y * 0.18)

    # ✓ Get all distributor details.
    crop = p0.within_bbox(distributor_area)
    details = crop.extract_text().split('\n')
    address = details[2]
    parts = address.split(',')
    street = parts[0]
    subparts = parts[-1].strip().split(' ')
    city = ' '.join(subparts[:-2])
    state, zipcode = subparts[-2], subparts[-1]
    address = ','.join([street, details[3]])
    obs['distributor'] = details[1]
    obs['distributor_address'] = address
    obs['distributor_street'] = street
    obs['distributor_city'] = city
    obs['distributor_state'] = state
    obs['distributor_zipcode'] = zipcode
    obs['distributor_license_number'] = details[-1]
    
    # ✓ Get all producer details.
    crop = p0.within_bbox(producer_area)
    details = crop.extract_text().split('\n')
    producer = details[1]
    street = details[2]
    parts = details[3].split(',')
    city = parts[0]
    state, zipcode = tuple(parts[-1].strip().split(' '))
    address = ','.join([street, details[3]])
    obs['producer'] = producer
    obs['producer_address'] = address
    obs['producer_street'] = street
    obs['producer_city'] = city
    obs['producer_state'] = state
    obs['producer_zipcode'] = zipcode
    obs['producer_license_number'] = details[-1]

    # ✓ Get the image data.
    image_index = parser.lims[lab]['coa_image_index']
    obs['image_data'] = parser.get_pdf_image_data(report.pages[0], image_index)
    obs['images'] = []

    # ✓ Get the sample details.
    fields = [
        'Test RFID',
        'Source RFID',
        'Lab Sample ID',
        'Sampling Method/SOP',
        'Source Batch ID',
        'Matrix',
        'Batch Size',
        'Sample Size',
        'Date Sampled',
        'Date Received',
        'Harvest/Processing Date',
        'Product Density',
    ]
    crop = p0.within_bbox(sample_details_area)
    details = crop.extract_text()
    details = re.split('\n|' + '|'.join(fields), details)
    product_name = details[0]
    index = 0
    for i, detail in enumerate(details[1:]):
        if detail:
            field = fields[index]
            key = GREEN_LEAF_LABS_FIELDS[field]
            obs[key] = detail.replace(':', '').strip()
            index += 1  

    # Get the `analyses` and `{analysis}_status`.
    analyses = []
    table = report.pages[0].extract_table()
    for rows in table:
        for row in rows:
            cells = row.split('\n')
            for cell in cells:
                parts = cell.split(':')
                key = snake_case(parts[0])
                try:
                    value = strip_whitespace(parts[1])
                except IndexError:
                    continue
                field = GREEN_LEAF_LABS_FIELDS.get(key, key)
                obs[field] = value.lower()
                if field != 'status':
                    analysis = field.replace('_status', '')
                    analyses.append(analysis)

    # FIXME: Identify `{analysis}_method`s.
    # Also find the times for all of the tests and find when all
    # tests were completed. Future work: record finish time of analyses.
    methods = []
    tested_at = []
    for page in report.pages[1:]:
        text = page.extract_text()
        parts = text.split('Analysis Method/SOP')
        for part in parts[1:]:
            method = part.split('\n')[0].replace(':', '').strip()
            method = method.split('Date/Time')[0] # <-- Hot-fix.
            methods.append(method)
        try:
            parts = text.split('Analyzed:')
            date = parts[1].split('\n')[0].strip()
            tested_at.append(pd.to_datetime(date))
        except:
            pass
    date_tested = max(tested_at).isoformat()

    # -- FIXME: Get ALL of the results! ---

    # Get a list of standard analytes and fields to collect.
    # Optional: Augment with Green Leaf Lab's analyses?
    # field_keys = list(parser.lims[lab]['coa_fields'].keys())
    standard_analytes = list(set(ANALYTES.values()))
    field_keys = list(GREEN_LEAF_LABS_FIELDS.keys())
    analysis_names = [x['name'] for x in GREEN_LEAF_LAB_ANALYSES.values()]
    analysis_keys = [x['key'] for x in GREEN_LEAF_LAB_ANALYSES.values()]

    # Get all of the `results` rows.
    all_rows = []
    for page in report.pages[1:]:
        crop = page.within_bbox(page_area)
        rows = get_page_rows(crop)
        for row in rows:
            if row in all_rows:
                pass
            else:
                all_rows.append(row)

    # Iterate over all rows to get the `results` rows
    # seeing if row starts with an analysis or analyte.
    columns = []
    results = []
    current_analysis = None
    for row in all_rows:

        # Identify the analysis.
        analysis = current_analysis
        for i, name in enumerate(analysis_names):
            if name in row:
                analysis = analysis_keys[i]
                break
        if analysis != current_analysis:
            current_analysis = analysis
            continue
        
        # Skip detail rows.
        if row.startswith('Date/Time') or row.startswith('Analysis Method'):
            continue

        # TODO: Identify the analyte!
        # for analyte in standard_analytes:
        #     if snake.startswith(analyte):


        # TODO: Identify the columns (static by analysis to make it easy!).


        # TODO: Get the results!
        values = row.replace('< LOQ', '<LOQ').replace('< LOD', '<LOD')
        values = values.split(' ')
        values = [x for x in values if x]
        print(analysis, values)

        # Record the result.
        result = {
            'analysis': analysis,
            'analyte': None,
            'value': '',
            'mg_g': '',
            'units': '',
            'status': '',
            'limit': '',
            'lod': '',
            'loq': '',
        }
        results.append(result)

    # Finish data collection with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=producer,
        public_key=product_name,
        salt=date_tested,
    )

    # Data cleaning.
    obs['analyses'] = analyses
    obs['date_tested'] = date_tested
    obs['methods'] = methods
    obs['product_name'] = product_name
    obs['results'] = results

    # Turn dates to ISO format.
    date_columns = [x for x in obs.keys() if x.startswith('date')]
    for date_column in date_columns:
        try:
            obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
        except:
            pass


    # Optional: Calculate THC to CBD ratio.

    # Optional: Calculate terpene ratios:
    # - beta-pinene to d-limonene ratio
    # - humulene to caryophyllene
    # - linalool and myrcene? (Research these!)

    # Optional: Calculate terpinenes total.
    # analytes = ['alpha_terpinene', 'gamma_terpinene', 'terpinolene', 'terpinene']
    # compounds = sum_columns(compounds, 'terpinenes', analytes, drop=False)

    # Optional: Sum `nerolidol` and `ocimene`.

    # Optional: Calculate total_cbg, total_thcv, total_cbc, etc.

    # Future work: Attempt to identify `strain_name`.

    # Future work: Standardize the `product_type`


    #-------------------------------------------------------------------
    # TEST: Parse a CoA PDF.
    # from cannlytics.data.coas import CoADoc
    # parser = CoADoc()
    # data = parse_green_leaf_lab_pdf(parser, coa_pdf)
    # assert data is not None
    #-------------------------------------------------------------------
    del obs['image_data']
    del obs['results']
    print('Obs:', obs)
