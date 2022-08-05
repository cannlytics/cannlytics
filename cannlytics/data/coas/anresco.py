"""
Parse Anresco Laboratories CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/3/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Anresco Laboratories CoA.

Data Points:

    - analyses
    - {analysis}_method
    - {analysis}_status
    ✓ batch_number
    - classification
    - coa_urls
    ✓ date_tested
    - date_received
    ✓ images
    ✓ lab_results_url
    - metrc_source_id
    ✓ project_id
    ✓ producer
    - product_name
    ✓ product_type
    - predicted_aromas
    - results
    ✓ sample_weight
    - total_cannabinoids (calculated)
    - total_thc
    - total_cbd
    - total_terpenes (calculated)
    ✓ sample_id (generated)
    - strain_name
    - lab_id
    - lab
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

Static Data Points:

"""
# Standard imports.
from ast import literal_eval
import re
from typing import Any

# External imports.
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import requests
from cannlytics.data.coas import CoADoc

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.utils.utils import (
    snake_case,
    split_list,
    strip_whitespace,
)

# External imports.
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
try:
    import chromedriver_binary  # Adds chromedriver binary to path.
except ImportError:
    print('Proceeding assuming that you have ChromeDriver in your path.')


# It is assumed that the lab has the following details.
ANRESCO =  {
    'coa_algorithm': 'anresco.py',
    'coa_algorithm_entry_point': 'parse_anresco_coa',
    'lims': 'Anresco Laboratories',
    'lab': 'Anresco Laboratories',
    'lab_website': 'www.anresco.com',
    'lab_address': '1375 Van Dyke Ave, San Francisco, CA 94124',
    'lab_street': '1375 Van Dyke Ave',
    'lab_city': 'San Francisco',
    'lab_state': 'CA',
    'lab_zipcode': '94124',
    'lab_latitude': 37.726610,
    'lab_longitude': -122.388450,
    'public': True,
}

ANRESCO_COA = {
    'coa_fields': {
        'Company': 'producer',
        'Anresco ID': 'lab_id',
        'Order ID': 'project_id',
        'Lot/Batch Number': 'batch_number',
        'Sample Wt': 'sample_weight',
        'Type': 'product_type',
        'Date': 'date_tested',
    },
}


def parse_anresco_coa(**kwargs):
    """Parse an Anresco Laboratories CoA PDF or URL."""
    raise NotImplementedError


# DEV:
parser = CoADoc()
doc = '../../../.datasets/coas/Flore COA/Betty Project/Peanutbutter Breath.pdf'
max_delay = 7

# Create the observation.
obs = {}

# Read the PDF.
if isinstance(doc, str):
    report = pdfplumber.open(doc)
else:
    report = doc
front_page = report.pages[0]

# Get the QR code from the last page.
url = parser.find_pdf_qr_code_url(report, page_index=-1)

# # Get the HTML!
# headers = DEFAULT_HEADERS
# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.content, 'html.parser')
service = Service()
options = Options()
options.add_argument('--window-size=1920,1200')
# Uncomment for dev:
# self.options.headless = False
# Uncomment for production!!!
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
driver = webdriver.Chrome(
    options=options,
    service=service,
)
driver.get(url)

# Wait for the page to load.
try:
    el = (By.CLASS_NAME, 'public-sample')
    detect = EC.presence_of_element_located(el)
    WebDriverWait(driver, max_delay).until(detect)
except TimeoutException:
    print('Failed to load page within %i seconds.' % max_delay)

# TODO: Get the lab details.

# TODO: Get the distributor details.

# TODO: Get the producer details.

# Get the image URL.
el = driver.find_element_by_css_selector('[alt="Sample picture"]')
image_url = el.get_attribute('src')
filename = image_url.split('/')[-1]
obs['images'] = [{'url': image_url, 'filename': filename}]

# Get the sample details.
button = driver.find_element(by=By.CLASS_NAME, value='ps-show-more-btn')
button.click()
standard_fields = ANRESCO['coa_fields']
fields = driver.find_elements(by=By.CLASS_NAME, value='ps-sample-info-table-static')
values = driver.find_elements(by=By.CLASS_NAME, value='ps-sample-info-table-variable')
for i, value in enumerate(values):
    key = fields[i].text
    key = standard_fields.get(key, snake_case(key))
    obs[key] = value.text

# Open all of the results.
els = driver.find_elements(by=By.CLASS_NAME, value='fa-chevron-down')
for el in els:
    el.click()

# Iterate over the sections.
methods = []
sections = driver.find_elements(by=By.CLASS_NAME, value='ps-mobile-section-expanded')

# DEV:
section = sections[0]

# TODO: Get the analysis.

# TODO: Get the analysis status.

# Get the method.
el = section.find_element(by=By.CLASS_NAME, value='ps-section-description')
method = el.text
methods.append({'analysis': '', 'method': method})


# FIXME: Get all of the results!


# TODO: Get the columns and units.
# ps-analyte-th


# TODO: Get and parse each analyte row.
# ps-analyte


# TODO: Get the LOD and LOQ for each result.


# TODO: Get the totals!
# - total_cannabinoids
# - total_thc
# - total_cbd


#--------------------------
# PDF Parsing if necessary
#--------------------------

# # Get all of the result rows.
# result_rows = []
# for page in report.pages:
#     rows = page.extract_table({
#         'vertical_strategy': 'text',
#         'horizontal_strategy': 'lines',
#         'explicit_vertical_lines': page.lines,
#         'keep_blank_chars': False,
#     })
#     rows = [[cell for cell in row if cell.strip()] for row in rows]

#     # FIXME: Remove rows that are too long or too short. 
#     # rows = [row for row in rows if row and len(rows) <= 6]

#     # FIXME: Split any double lines.
#     # rows = [[cell.split('\n')[0].strip() for cell in row] for row in rows]

#     result_rows.extend(rows)

# # FIXME: Extract the results.
# print(result_rows)


#--------------------------
# Data aggregation
#--------------------------

# Aggregate results.
# obs['analyses'] = analyses
# obs['results'] = results
obs['lab_results_url'] = url

# Turn dates to ISO format.
date_columns = [x for x in obs.keys() if x.startswith('date')]
for date_column in date_columns:
    try:
        obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
    except:
        pass

# Finish data collection with a freshly minted sample ID.
obs['sample_id'] = create_sample_id(
    private_key=obs['producer'],
    public_key=obs['product_name'],
    salt=obs['date_tested'],
)

print({**ANRESCO, **obs})


#--------------------------
# Future work
#--------------------------

# Standardize analytes with NLP!


# [ ] TEST: Parse an Anresco Laboratories CoA PDF.
