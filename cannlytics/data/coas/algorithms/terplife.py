"""
Parse TerpLife Labs COAs
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/20/2023
Updated: 5/21/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse TerpLife Labs COA PDFs.

Data Points:

    - analyses
    - methods
    - status
    - coa_urls
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
    - metrc_ids
    - metrc_lab_id
    - metrc_source_id
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
import pandas as pd
import pdfplumber

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
TERPLIFE_LABS = {
    'coa_algorithm': 'terplife.py',
    'coa_algorithm_entry_point': 'parse_terplife_coa',
    'lims': 'TerpLife Labs',
    'lab': 'TerpLife Labs',
    'lab_image_url': 'https://www.terplifelabs.com/wp-content/uploads/2022/03/website-logo.png',
    'lab_address': '10350 Fisher Ave, Tampa',
    'lab_street': '10350 Fisher Ave',
    'lab_city': 'Tampa',
    'lab_county': 'Hillsborough County',
    'lab_state': 'FL',
    'lab_zipcode': '33619',
    'lab_phone': '813-726-3103',
    'lab_email': 'info@terplifelabs.com',
    'lab_website': 'https://www.terplifelabs.com/',
    'lab_latitude': 27.959174,
    'lab_longitude': -82.3278,
}


def parse_terplife_coa(
        parser,
        doc: Any,
        temp_path: Optional[str] = None,
        **kwargs,
    ) -> dict:
    """Parse a TerpLife Labs COA PDF.
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

    # [ ] TEST: Identify LIMS.
    # parser = CoADoc()
    # doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229%20TLMB0216202301.pdf'
    # lims = parser.identify_lims(doc, lims={'TerpLife Labs': TERPLIFE_LABS})
    # assert lims == 'TerpLife Labs'

    # [ ] TEST: Parse a full-panel COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/T302229 TLMB0216202301.pdf'


    # [ ] TEST: Parse a cannabinoid and terpene COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU310823-2327TT.pdf'

    # [ ] TEST: Parse a R&D COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU180222-6925CKC.pdf'


    # [ ] TEST: Parse a COA that requires OCR.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/BU090222-9534DD.pdf'


    # [ ] TEST: Parse a cannabinoid-only COA.
    doc = 'D:/data/florida/lab_results/.datasets/pdfs/terplife/36782.pdf'

    # === DEV ===
    import os

    # Initialize the parser.
    parser = CoADoc()

    # Get the front page text.
    report = pdfplumber.open(doc)
    front_page = report.pages[0]
    front_page_text = report.pages[0].extract_text()

    # Clean extraneous text from the front page.
    extras = [
        'Unless otherwise stated all quality control samples',
        ' performed within specifications established by the Laboratory.'
    ]
    front_page_text = front_page_text.split('The data contained')[0]
    for extra in extras:
        front_page_text = front_page_text.replace(extra, '')
    print(front_page_text)

    # Process the text.
    front_page_text = front_page_text.replace('█', '\n')    
    lines = front_page_text.split('\n')
    lines = [x for x in lines if x != '']

    # Get the image data.
    image_file = doc.split('/')[-1].replace('.pdf', '.png')
    image_dir = 'D:/data/florida/lab_results/.datasets/images/terplife'
    images = front_page.images

    # Determine the largest image by pixel area using width and height.
    image_index, _ = max(
        enumerate(front_page.images),
        key=lambda img: img[1]['width'] * img[1]['height']
    )
    image_data = parser.get_pdf_image_data(front_page, image_index=image_index)
    parser.save_image_data(image_data, os.path.join(image_dir, image_file))


    # === Parse with AI ===
    from openai import OpenAI
    from dotenv import dotenv_values


    # Instructional prompt.
    INSTRUCTIONAL_PROMPT = 'Return JSON.'

    
    # Prompt to parse metadata from the first page.
    COA_PROMPT = """Given text, extract any of the following fields you see as JSON. Fields:

    | Field | Example | Description |
    |-------|---------|-------------|
    | `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
    | `status` | "pass" | The overall pass, fail, or N/A status for pass / fail analyses.   |
    | `methods` | [{"analysis: "cannabinoids", "method": "HPLC"}] | The methods used for each analysis. |
    | `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
    | `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
    | `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
    | `lab` | "MCR Labs" | The lab that tested the sample. |
    | `lab_address` | "85 Speen St, Framingham, MA 01701" | The lab's address. |
    | `lab_street` | "85 Speen St" | The lab's street. |
    | `lab_city` | "Framingham" | The lab's city. |
    | `lab_state` | "MA" | The lab's state. |
    | `lab_zipcode` | "01701" | The lab's zipcode. |
    | `distributor` | "Fred's Dispensary" | The name of the product distributor, if applicable. |
    | `distributor_address` | "420 State Ave, Olympia, WA 98506" | The distributor address, if applicable. |
    | `distributor_street` | "420 State Ave" | The distributor street, if applicable. |
    | `distributor_city` | "Olympia" | The distributor city, if applicable. |
    | `distributor_state` | "WA" | The distributor state, if applicable. |
    | `distributor_zipcode` | "98506" | The distributor zip code, if applicable. |
    | `distributor_license_number` | "L-123" | The distributor license number, if applicable. |
    | `producer` | "Grow House" | The producer of the sampled product. |
    | `producer_address` | "3rd & Army, San Francisco, CA 55555" | The producer's address. |
    | `producer_street` | "3rd & Army" | The producer's street. |
    | `producer_city` | "San Francisco" | The producer's city. |
    | `producer_state` | "CA" | The producer's state. |
    | `producer_zipcode` | "55555" | The producer's zipcode. |
    | `producer_license_number` | "L2Calc" | The producer's license number. |
    | `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
    | `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
    | `product_type` | "flower" | The type of product. |
    | `batch_number` | "Order-0001" | A batch number for the sample or product. |
    | `traceability_ids` | ["1A4060300002199000003445"] | A list of relevant traceability IDs. |
    | `product_size` | 2000 | The size of the product in milligrams. |
    | `serving_size` | 1000 | An estimated serving size in milligrams. |
    | `servings_per_package` | 2 | The number of servings per package. |
    | `sample_weight` | 1 | The weight of the product sample in grams. |
    | `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
    | `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
    | `total_thc` | 14.00 | The analytical total of THC and THCA. |
    | `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
    | `total_terpenes` | 0.42 | The sum of all terpenes measured. |
    | `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, try to parse the `strain_name` from the `product_name`. |
    """

    # Prompt used to parse results from all pages.
    RESULTS_PROMPT = """Given text, extract JSON. Extract only `results` as a list of JSON objects, e.g.:

    {
        "results": [
            {
                "analysis": str,
                "key": str,
                "name": str,
                "value": float,
                "mg_g": float,
                "units": str,
                "limit": float,
                "lod": float,
                "loq": float,
                "status": str
            }
        ]
    }

    Where:

    | Field | Example| Description |
    |-------|--------|-------------|
    | `analysis` | "pesticides" | The analysis used to obtain the result. |
    | `key` | "pyrethrins" | A standardized key for the result analyte. |
    | `name` | "Pyrethrins" | The lab's internal name for the result analyte |
    | `value` | 0.42 | The value of the result. |
    | `mg_g` | 0.00000042 | The value of the result in milligrams per gram. |
    | `units` | "ug/g" | The units for the result `value`, `limit`, `lod`, and `loq`. |
    | `limit` | 0.5 | A pass / fail threshold for contaminant screening analyses. |
    | `lod` | 0.01 | The limit of detection for the result analyte. Values below the `lod` are typically reported as `ND`. |
    | `loq` | 0.1 | The limit of quantification for the result analyte. Values above the `lod` but below the `loq` are typically reported as `<LOQ`. |
    | `status` | "pass" | The pass / fail status for contaminant screening analyses. |
    """


    # Initialize OpenAI
    os.environ['OPENAI_API_KEY'] = dotenv_values('.env')['OPENAI_API_KEY']
    openai_api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI()

    # TODO: Parse TerpLife Labs COAs.

    # Define the parsing prompt.
    coa_prompt = COA_PROMPT
    metadata_prompt = 'Text: ' + front_page_text + '\n\nJSON:'
    instructional_prompt = INSTRUCTIONAL_PROMPT
    messages = [
        {'role': 'system', 'content': coa_prompt},
        {'role': 'system', 'content': instructional_prompt},
        {'role': 'user', 'content': metadata_prompt},
    ]
    temperature = 0.0
    user = 'cannlytics'
    max_tokens = 4_096

    # Prompt AI to extract COA metadata as JSON.
    completion = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
    )
    print(completion.choices[0].message)
    usage = completion.model_dump()['usage']
    content = completion.choices[0].message.content
    extracted_json = content.lstrip('```json\n').rstrip('\n```')
    extracted_data = json.loads(extracted_json)

    # Prompt AI to extract COA results as JSON.
    # FIXME: Get all results!
    results_prompt = RESULTS_PROMPT
    messages = [
        {'role': 'system', 'content': results_prompt},
        {'role': 'system', 'content': instructional_prompt},
    ]
    content = 'Text: ' + front_page_text #  + '\n\nList of results as JSON:'
    messages.append({'role': 'user', 'content': content})
    results_completion = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
    )
    print(results_completion.choices[0].message)
    usage = results_completion.model_dump()['usage']
    content = results_completion.choices[0].message.content
    extracted_json = content.lstrip('```json\n').rstrip('\n```')
    extracted_data = json.loads(extracted_json)
