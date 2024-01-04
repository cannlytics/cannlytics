"""
Parse Method Testing Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 5/21/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Method Testing Labs COA PDFs.

Data Points:

    - analyses
    - methods
    - coa_url
    - date_collected
    - date_tested
    - date_received
    - images
    - lab_results_url
    - producer
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number
    - product_name
    - lab_id
    - product_type
    - batch_number
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight
    - results
    - status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    - sample_id
    - strain_name (augmented)
    - lab
    - lab_image_url
    - lab_license_number
    - lab_address
    - lab_street
    - lab_city
    - lab_county (augmented)
    - lab_state
    - lab_zipcode
    - lab_phone
    - lab_email
    - lab_website
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
import json
import re
from typing import Any, Optional

# External imports.
import cv2
import pandas as pd
import pdfplumber
try:
    import pytesseract
except ImportError:
    print('Unable to import `Tesseract` library. This tool is used for OCR.')

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import STANDARD_UNITS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
MTL_LABS = {
    'coa_algorithm': 'mtl.py',
    'coa_algorithm_entry_point': 'parse_mtl_coa',
    'url': 'http://mete.labdrive.net',
    'lims': 'Method Testing Labs',
    'lab': 'Method Testing Labs',
    'lab_image_url': 'https://methodtestinglabs.com/wp-content/uploads/2020/08/method-logo-resize-b.png',
    'lab_address': '2720 Broadway Center Blvd, Brandon, FL 33510',
    'lab_street': '2720 Broadway Center Blvd',
    'lab_city': 'Brandon',
    'lab_county': 'Hillsborough',
    'lab_state': 'FL',
    'lab_zipcode': '33510',
    'lab_phone': '813-769-9567',
    'lab_email': 'info@methodtestinglabs.com',
    'lab_website': 'methodtestinglabs.com',
    'lab_latitude': 27.967740,
    'lab_longitude': -82.324950,
}


def parse_mtl_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a Method Testing Labs COA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """

    # Get the lab's analyses.
    # lab_analyses = GREEN_LEAF_LAB_ANALYSES
    # coa_parameters = GREEN_LEAF_LAB_COA
    # standard_analyses = list(lab_analyses.keys())
    # analysis_names = [x['name'] for x in lab_analyses.values()]

    # TODO: If the `doc` is a URL, then download the PDF to `temp_path`.
    if temp_path is None:
        # FIXME: Get the user's temp_path
        temp_path = '/tmp'

    # Read the PDF.
    obs = {}
    if isinstance(doc, str):
        report = pdfplumber.open(doc)
        obs['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    else:
        report = doc
        obs['coa_pdf'] = report.stream.name.replace('\\', '/').split('/')[-1]
    front_page = report.pages[0]

    # Add optional ability to collect the image.
    # - Get the image data.
    # - Save the image to Firebase Storage
    # - Create a dynamic link for the image.

    # TODO: Get the lab details.

    # TODO: Get the sample details.

    # TODO: Get the client details.

    # TODO: Get the analyses.

    # TODO: Get the results.


# === Tests ===
if __name__ == '__main__':

    from cannlytics.data.coas import CoADoc
    from dotenv import dotenv_values

    # # [✓] TEST: Identify LIMS from a COA URL.
    # parser = CoADoc()
    # url = 'http://mete.labdrive.net/s/KmXMdYTFR3dsceG'
    # lims = parser.identify_lims(url, lims={'Method Testing Labs': MTL_LABS})
    # assert lims == 'Method Testing Labs'

    # # [✓] TEST: Identify LIMS from a COA PDF.
    # parser = CoADoc()
    # doc = 'D://data/florida/lab_results/.datasets/pdfs/mtl/COA_2305CBR0001-004.pdf'
    # lims = parser.identify_lims(doc, lims={'Method Testing Labs': MTL_LABS})
    # assert lims == 'Method Testing Labs'

    # # [ ] TEST: Parse a Method Testing Labs COA from a URL.
    # urls = [
    #     'http://mete.labdrive.net/s/KmXMdYTFR3dsceG',
    #     'http://mete.labdrive.net/s/KmXMdYTFR3dsceG/download/COA_2305CBR0001-004.pdf',
    #     'https://mete.labdrive.net/s/se8BcYZJAMqaYrE',
    #     'https://coaportal.com/sunburn/report/?search=0524324712189959',
    #     'https://coaportal.com/sunburn/report/?search=9586770498778201',
    #     'https://coaportal.com/sunburn/report/?search=8315430847060831',
    #     'https://coaportal.com/sunburn/report/?search=Sunburn-3807806169682269-2303CTB0044-003',
    # ]


    import cv2
    import pytesseract
    import re

    # Define the image of the COA.
    doc = "3hmIuam.png"

    # Load the image
    image = cv2.imread(doc, 0)

    # Resize the image for better recognition.
    resized_img = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Perform OCR.
    text = pytesseract.image_to_string(resized_img)
    print(text)


    def parse_mtl_coa_report(text):
        data = {}
        
        # Extracting Producer or Lab Information
        lab_info = re.search(r"(\w+ TESTING LABS)\n([^\|]+)\|", text)
        if lab_info:
            data['producer'] = lab_info.group(1).strip()
            address_parts = lab_info.group(2).strip().split(", ")
            data['producer_address'] = ", ".join(address_parts)
            data['producer_street'] = address_parts[0]
            data['producer_city'], data['producer_state'], data['producer_zipcode'] = re.split(r" |, ", address_parts[1])
            
        # Extracting Date Tested
        date_tested = re.search(r"(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} (AM|PM))", text)
        if date_tested:
            data['date_tested'] = date_tested.group(1)
            
        # Extracting Product Name
        product_name = re.search(r"Product Name: ([^\n]+)", text)
        if product_name:
            data['product_name'] = product_name.group(1).strip()
            
        # Extracting Sample ID or Lot ID
        sample_id = re.search(r"Lot ID: (\d+ \d+ \d+ \d+)", text)
        if sample_id:
            data['sample_id'] = sample_id.group(1).replace(" ", "")
            
        # Extracting Results
        results_section = re.search(r"(ANALYTE .+?)(Total Terpenes: .+%)", text, re.DOTALL)
        if results_section:
            results_text = results_section.group(1)
            results_lines = results_text.split("\n")[1:]  # Skipping the "ANALYTE" header
            
            results = []
            for line in results_lines:
                line_parts = re.split(r"\s+", line.strip())
                if len(line_parts) >= 5:
                    result = {
                        "analysis": "cannabinoids",
                        "key": line_parts[0].lower(),
                        "name": line_parts[0],
                        "value": float(line_parts[2]) if line_parts[2] != "ND" else None,
                        "units": "percent",
                        "limit": None,
                        "lod": float(line_parts[1]),
                        "loq": None,
                        "status": None,
                    }
                    results.append(result)
            data['results'] = results
        
        # Extracting Total Cannabinoids, THC, CBD, and Terpenes
        total_values = re.search(r"Total THC: (.+%) Total CBD: (.+%) Total Cannabinoids: (.+%)", text)
        if total_values:
            data['total_thc'] = float(total_values.group(1).strip('%'))
            data['total_cbd'] = float(total_values.group(2).strip('%'))
            data['total_cannabinoids'] = float(total_values.group(3).strip('%'))
            
        total_terpenes = re.search(r"Total Terpenes: (.+%)", text)
        if total_terpenes:
            data['total_terpenes'] = float(total_terpenes.group(1).strip('%'))
        
        return data

    # TODO: Parse the COA!
    coa_data = parse_mtl_coa_report(text)

