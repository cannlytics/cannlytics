"""
Parse COAs | Green Analytics
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/28/2024
Updated: 6/28/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Green Analytics COA PDFs.
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
GREEN_ANALYTICS = {
    'coa_algorithm': 'green_analytics.py',
    'coa_algorithm_entry_point': 'parse_green_analytics_coa',
    'lims': 'Green Analytics',
}
GREEN_ANALYTICS_COA = {
    'fields': {
        
    }
}


def parse_green_analytics_coa(
        parser,
        doc: Any,
        coa_parameters: dict = GREEN_ANALYTICS_COA,
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

    # TODO: Get lab details .
    front_page = report.pages[0]


    # TODO: Get producer details.


    # TODO: Get sample details.

    
    # Optional: Get lab results URL.
    # Note: This currently causes the interpreter to crash.
    # coa_url = parser.find_pdf_qr_code_url(front_page)
    # obs['lab_results_url'] = coa_url
    
    # TODO: Get analyses.

    # TODO: Get methods.

    # Get total cannabinoids.


    # Get cannabinoid results.
    results = []

    # Get terpenes.

    # Calculate total terpenes.
    # if terpenes:
    #     obs['total_terpenes'] = calculate_total_terpenes(results)

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
    obs = {**GREEN_ANALYTICS, **obs}
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
# Tested: 2024-06-28 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc

    # TODO: [ ] TEST: Identify LIMS.


    # [✓] TEST: Parse a COA PDF.
    docs = [
        'D://data/new-york\\NYSCannabis\\pdfs\\1c3sh5h-coa-1.pdf',
        'D://data/new-york\\NYSCannabis\\pdfs\\1cp4tdr-coa-1.pdf',
        'D://data/new-york\\NYSCannabis\\pdfs\\1c91onw-coa-1.pdf'
    ]
    for doc in docs:
        parser = CoADoc()
        data = parse_green_analytics_coa(parser, doc)
        assert data is not None
