"""
Parse Anresco Laboratories CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/8/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Anresco Laboratories CoA PDFs and URLs.

Data Points:

    - analyses
    - {analysis}_method
    ✓ {analysis}_status
    ✓ batch_number
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    - images
    ✓ lab_results_url
    - metrc_source_id
    ✓ project_id
    ✓ producer
    ✓ producer_address

    ✓ product_name
    ✓ product_type
    - results
    ✓ sample_weight
    ✓ status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    ✓ sample_id (generated)
    ✓ lab_id
    ✓ lab
    - lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    - lab_city (augmented)
    - lab_county (augmented)
    - lab_state (augmented)
    - lab_zipcode (augmented)
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from ast import literal_eval
import re
from typing import Any, Optional

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
    convert_to_numeric,
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
    'coa_distributor_area': '(200, 60, 380, 130)',
    'coa_lab_area': '(0, 60, 200, 130)',
    'coa_producer_area': '(380, 60, 580, 130)',
    'coa_sample_details_area': [
        '(200, 130, 385, 310)',
        '(385, 130, 590, 310)',
    ],
    'coa_analyses': {},
    'coa_analytes': {
        '8_thc': 'delta_8_thc',
        '9_thc': 'delta_9_thc',
        '9_thca': 'thca',
        'moisture': 'moisture_content',
        'salmonella_aoac': 'salmonella',
    },
    'coa_fields': {
        'Company': 'producer',
        'Anresco ID': 'lab_id',
        'Order ID': 'project_id',
        'Lot/Batch Number': 'batch_number',
        'Sample Wt': 'sample_weight',
        'Type': 'product_type',
        'Date': 'date_tested',
        'date_reported': 'date_tested',
        'total_sample_weight_g': 'sample_weight',
        'increment_g': 'sample_weight_used',
        'sample_no': 'lab_id',
        'matrix': 'product_type',
        'cannabinoid_pro_le': 'cannabinoids_status',
        'pesticide_residue_screen': 'pesticides_status',
        'foreign_material': 'foreign_matter_status',
        'water_activity': 'water_activity_status',
        'microbiological_screen': 'microbes_status',
        'heavy_metal_screen': 'heavy_metals_status',
        'mycotoxin_screen': 'mycotoxins_status',
        'other_analyses': 'moisture_status',
        'overall': 'status',
        'total_cannabinoids': 'sum_of_cannabinoids',
        'total_active_cannabinoids': 'total_cannabinoids',
    },
    'coa_result_fields': {
        'Analyte': 'name',
        'Cannabinoid': 'name',
        'Findings': 'value',
        'Limit': 'limit',
        'LOD/LOQ': 'lod',
        'Method': 'method',
        'Status': 'status',
        'Instrument': 'instrument',
        'mg/g': 'mg_g',
        '%': 'percent',
    },
    'coa_drop_columns': [
        'sample_weight_to',
        'sample_information',
        'test_summary',
        'harvest',
    ],
}


def find_first_value(
        string: str,
        breakpoints: Optional[list]=None,
    ) -> str:
    """Find the first value of a string, be it a digit, a 'ND', '<',
    or other specified breakpoints.
    Args:
        string (str): The string containing a value.
        breakpoints (list): A list of breakpoints (optional).
    Returns:
        (int): Returns the index of the first value.
    """
    if breakpoints is None:
        breakpoints = [' \d+', 'ND', '<']
    detects = []
    for breakpoint in breakpoints:
        try:
            detects.append(string.index(re.search(breakpoint, string).group()))
        except AttributeError:
            pass
    try:
        return min([x for x in detects if x])
    except ValueError:
        return None


def parse_anresco_coa(**kwargs):
    """Parse an Anresco Laboratories CoA PDF or URL."""
    raise NotImplementedError


# === Tests ===
# if __name__ == '__main__':

# Test parsing Anresco Laboratories CoAs.
parser = CoADoc()
doc = '../../../.datasets/coas/Flore COA/Betty Project/Peanutbutter Breath.pdf'
coa_url = 'https://portal.anresco.com/#/ps/68bcb967c0f2b39d'


#--------------------------
# Development
#--------------------------

# Create the observation.
obs = {}

# Read the PDF.
if isinstance(doc, str):
    report = pdfplumber.open(doc)
else:
    report = doc
front_page = report.pages[0]

# Get the QR code from the last page.
lab_results_url = parser.find_pdf_qr_code_url(report, page_index=-1)


#--------------------------------------------
# TODO: Parse a Anresco Laboratories CoA PDF.
#--------------------------------------------

# Get the standard analyses, analytes, and fields.
coa_parameters = ANRESCO_COA
standard_analytes = coa_parameters['coa_analytes']
standard_fields = coa_parameters['coa_fields']
standard_result_fields = coa_parameters['coa_result_fields']

# Get the sample details based on page area.
sample_details_area = coa_parameters['coa_sample_details_area']
if isinstance(sample_details_area, str):
    sample_details_area = [sample_details_area]
for area in sample_details_area:
    crop = front_page.within_bbox(literal_eval(area))
    lines = crop.extract_text().split('\n')
    for line in lines:
        parts = line.replace('\xa0', ' ').split(':')
        key = snake_case(parts[0])
        key = standard_fields.get(key, key)
        if not key:
            continue
        value = parts[-1].replace('✔', '')
        obs[key] = value.strip()

# Hot-fix.
drop_columns = coa_parameters['coa_drop_columns']
for column in drop_columns:
    try:
        del obs[column]
    except:
        pass

# Get the lab data based on page area.
area = coa_parameters['coa_lab_area']
crop = front_page.within_bbox(literal_eval(area))
lines = crop.extract_text().split('\n')[1:]
obs['lab'] = lines[0]
obs['lab_address'] = ', '.join([lines[1], lines[2]])
obs['lab_license_number'] = lines[-1]

# Get the producer data based on page area.
area = coa_parameters['coa_producer_area']
crop = front_page.within_bbox(literal_eval(area))
lines = crop.extract_text().split('\n')[1:]
obs['producer'] = lines[0]
obs['producer_address'] = ', '.join([lines[1], lines[2]])
obs['producer_license_number'] = lines[-1]

# Get the distributor data based on page area.
area = coa_parameters['coa_distributor_area']
crop = front_page.within_bbox(literal_eval(area))
lines = crop.extract_text().split('\n')[1:]
obs['distributor'] = lines[0]
obs['distributor_address'] = ' '.join([lines[1], lines[2]])
obs['distributor_license_number'] = lines[-1]

# Future work: Get all GIS data for `lab`, `producer`, and `distributor`.

# Get the result data.
# TODO: Get the `analyses` and `{analysis}_status`.
# TODO: Add `analysis` to results.
analyses = []
analysis = None
columns = []
results = []
units = None
for page in report.pages:

    # Iterate over the lines of text on the page.
    lines = page.extract_text().split('www.anresco.com')[0].split('\n')
    for line in lines:

        # TODO: Get the analysis.

        # Get the totals.
        if line.startswith('Total'):

            first_value = find_first_value(line)
            name = line[:first_value].strip()
            key = snake_case(name)
            key = standard_fields.get(key, key)
            values = line[first_value:].strip().split(' ')
            values = [x for x in values if x]
            obs[key] = convert_to_numeric(values[-1])

        # Get the columns.
        # Note: Hot-fix for cannabinoids.
        elif line.startswith('Analyte') or line.startswith('Cannabinoid mg/g'):

            # Try to get the units.
            if '(' in line:
                units = line.split('(')[-1].split(')')[0]
            elif line.startswith('Cannabinoid'):
                units = 'percent'
            else:
                units = None # FIXME: Determine units another way.

            # Get the standard columns.
            text = re.sub('[\(\[].*?[\)\]]', '', line)
            columns = [
                standard_result_fields[x] for x in text.split(' ') if x
            ]

        # Get the analysis method.
        # FIXME: Not all analyses have a method and instrument.
        elif 'Method:' in line:
            continue

        elif 'Instrument:' in line:
            continue

        # SKip extraneous rows.
        elif not line or not columns or '✔' in line or 'Anresco Laboratories' in line:
            continue

        # Extract the results!
        else:

            # Find the first value.
            first_value = find_first_value(line)
            if not first_value or line.startswith('STEC'):
                # FIXME: Microbes have text values.
                print('FIX:', line)
                continue
        
            # FIXME: Hot-fix for foreign matter.
            line = line.replace('1 per 3g', '1/3g')

            # FIXME: Also exclude other analyses and the dates.

            # Parse the result values.
            print('Processing:', line)
            name = line[:first_value].strip()
            analyte = standard_analytes.get(snake_case(name), snake_case(name))
            values = line[first_value:].strip().split(' ')
            values = [x for x in values if x]
            result = {
                'analysis': None, # FIXME: <-- Add this data point!
                'key': analyte,
                'name': name,
                'units': None, # FIXME: <-- Add this data point!
            }
            try:
                for i, value in enumerate(values):
                    key = columns[i + 1]
                    result[key] = convert_to_numeric(value)
            except IndexError:
                continue 
            results.append(result)

# Turn dates to ISO format.
date_columns = [x for x in obs.keys() if x.startswith('date')]
for date_column in date_columns:
    try:
        obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
    except:
        pass

# Finish data collection with a freshly minted sample ID.
obs['analyses'] = analyses
obs['lab_results_url'] = lab_results_url
obs['results'] = results
obs['sample_id'] = create_sample_id(
    private_key=obs['producer'],
    public_key=obs['product_name'],
    salt=obs['date_tested'],
)

# print('Obs fields:', len(obs.keys()))


#--------------------------------------------
# TODO: Parse a Anresco Laboratories CoA URL.
#--------------------------------------------

# DEV: Default parameters
# max_delay = 7

# # # Get the HTML!
# # headers = DEFAULT_HEADERS
# # response = requests.get(url, headers=headers)
# # soup = BeautifulSoup(response.content, 'html.parser')
# service = Service()
# options = Options()
# options.add_argument('--window-size=1920,1200')
# # Uncomment for dev:
# # self.options.headless = False
# # Uncomment for production!!!
# # options.add_argument('--headless')
# # options.add_argument('--disable-gpu')
# # options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(
#     options=options,
#     service=service,
# )
# driver.get(url)

# # Wait for the page to load.
# try:
#     el = (By.CLASS_NAME, 'public-sample')
#     detect = EC.presence_of_element_located(el)
#     WebDriverWait(driver, max_delay).until(detect)
# except TimeoutException:
#     print('Failed to load page within %i seconds.' % max_delay)

# # TODO: Get the lab details.

# # TODO: Get the distributor details.

# # TODO: Get the producer details.

# # Get the image URL.
# el = driver.find_element_by_css_selector('[alt="Sample picture"]')
# image_url = el.get_attribute('src')
# filename = image_url.split('/')[-1]
# obs['images'] = [{'url': image_url, 'filename': filename}]

# # Get the sample details.
# button = driver.find_element(by=By.CLASS_NAME, value='ps-show-more-btn')
# button.click()
# standard_fields = ANRESCO['coa_fields']
# fields = driver.find_elements(by=By.CLASS_NAME, value='ps-sample-info-table-static')
# values = driver.find_elements(by=By.CLASS_NAME, value='ps-sample-info-table-variable')
# for i, value in enumerate(values):
#     key = fields[i].text
#     key = standard_fields.get(key, snake_case(key))
#     obs[key] = value.text

# # Open all of the results.
# els = driver.find_elements(by=By.CLASS_NAME, value='fa-chevron-down')
# for el in els:
#     el.click()

# # Iterate over the sections.
# methods = []
# sections = driver.find_elements(by=By.CLASS_NAME, value='ps-mobile-section-expanded')

# # DEV:
# section = sections[0]

# # TODO: Get the analysis.

# # TODO: Get the analysis status.

# # Get the method.
# el = section.find_element(by=By.CLASS_NAME, value='ps-section-description')
# method = el.text
# methods.append({'analysis': '', 'method': method})


# # FIXME: Get all of the results!


# # TODO: Get the columns and units.
# # ps-analyte-th


# # TODO: Get and parse each analyte row.
# # ps-analyte


# # TODO: Get the LOD and LOQ for each result.


# # TODO: Get the totals!
# # - total_cannabinoids
# # - total_thc
# # - total_cbd


# print({**ANRESCO, **obs})


#--------------------------
# Future work
#--------------------------

# Standardize analytes with NLP!


# [ ] TEST: Parse an Anresco Laboratories CoA PDF.
