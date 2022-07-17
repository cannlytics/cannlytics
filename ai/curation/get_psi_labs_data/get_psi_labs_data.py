"""
PSI Labs Test Result Data Collection
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: July 4th, 2022
Updated: 7/12/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    1. Archive all of the PSI Labs test results.

    2. Analyze all of the PSI Labs test results, separating
    training and testing data to use for prediction models.

    3. Create and use re-usable prediction models.

Data Sources:

    - PSI Labs Test Results
    URL: <https://results.psilabs.org/test-results/>

Resources:

    - ChromeDriver
    URL: <https://chromedriver.chromium.org/home>

    - Automation Cartoon
    URL: https://xkcd.com/1319/

    - Efficiency Cartoon
    URL: https://xkcd.com/1445/

    - SHA in Python
    URL: https://www.geeksforgeeks.org/sha-in-python/

    - Split / Explode a column of dictionaries into separate columns with pandas
    URL: https://stackoverflow.com/questions/38231591/split-explode-a-column-of-dictionaries-into-separate-columns-with-pandas

    - Tidyverse: Wide and Long Data Tables
    URL: https://rstudio-education.github.io/tidyverse-cookbook/tidy.html

    - Web Scraping using Selenium and Python
    URL: <https://www.scrapingbee.com/blog/selenium-python/>

Setup:

    1. Create a data folder `../../.datasets/lab_results/psi_labs/raw_data`.

    2. Download ChromeDriver and put it in your `C:\Python39\Scripts` folder
    or pass the `executable_path` to the `Service`.

    3. Specify the `PAGES` that you want to collect.

"""
# Standard imports.
from ast import literal_eval
from datetime import datetime
from hashlib import sha256
import hmac
from time import sleep

# External imports.
from cannlytics.utils.utils import snake_case
import pandas as pd

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Setup.
DATA_DIR = '../../.datasets/lab_results/raw_data/psi_labs'
TRAINING_DATA = '../../../.datasets/lab_results/training_data'

# API Constants
BASE = 'https://results.psilabs.org/test-results/?page={}'
PAGES = range(1, 10) # 4921 total!

# Desired order for output columns.
COLUMNS = [
    'sample_id',
    'date_tested',
    'analyses',
    'producer',
    'product_name',
    'product_type',
    'results',
    'coa_urls',
    'images',
    'lab_results_url',
    'date_received',
    'method',
    'qr_code',
    'sample_weight',
]


def create_sample_id(private_key, public_key, salt='') -> str:
    """Create a hash to be used as a sample ID.
    The standard is to use:
        1. `private_key = producer`
        2. `public_key = product_name`
        3. `salt = date_tested`
    Args:
        private_key (str): A string to be used as the private key.
        public_key (str): A string to be used as the public key.
        salt (str): A string to be used as the salt, '' by default (optional).
    Returns:
        (str): A sample ID hash.
    """
    secret = bytes(private_key, 'UTF-8')
    message = snake_case(public_key) + snake_case(salt)
    sample_id = hmac.new(secret, message.encode(), sha256).hexdigest()
    return sample_id


#-----------------------------------------------------------------------
# Getting ALL the data.
#-----------------------------------------------------------------------

def get_psi_labs_test_results(driver, max_delay=5, reverse=True) -> list:
    """Get all test results for PSI labs.
    Args:
        driver (WebDriver): A Selenium Chrome WebDiver.
        max_delay (float): The maximum number of seconds to wait for rendering (optional).
        reverse (bool): Whether to collect in reverse order, True by default (optional).
    Returns:
        (list): A list of dictionaries of sample data.
    """

    # Get all the samples on the page.
    samples = []
    try:
        detect = EC.presence_of_element_located((By.TAG_NAME, 'sample-card'))
        WebDriverWait(driver, max_delay).until(detect)
    except TimeoutException:
        print('Failed to load page within %i seconds.' % max_delay)
        return samples
    cards = driver.find_elements(by=By.TAG_NAME, value='sample-card')
    if reverse:
        cards.reverse()
    for card in cards:

        # Begin getting sample details from the card.
        details = card.find_element(by=By.TAG_NAME, value='md-card-title')

        # Get images.
        image_elements = details.find_elements(by=By.TAG_NAME, value='img')
        images = []
        for image in image_elements:
            src = image.get_attribute('src')
            filename = src.split('/')[-1]
            images.append({'url': src, 'filename': filename})

        # Get the product name.
        product_name = details.find_element(by=By.CLASS_NAME, value='md-title').text

        # Get the producer, date tested, and product type.
        headers = details.find_elements(by=By.CLASS_NAME, value='md-subhead')
        producer = headers[0].text
        try:
            mm, dd, yy = tuple(headers[1].text.split(': ')[-1].split('/'))
            date_tested = f'20{yy}-{mm}-{dd}'
        except ValueError:
            date_tested = headers[1].text.split(': ')[-1]
        product_type = headers[2].text.split(' ')[-1]

        # Create a sample ID.
        private_key = bytes(date_tested, 'UTF-8')
        public_key = snake_case(product_name)
        salt = snake_case(producer)
        sample_id = hmac.new(private_key, (public_key + salt).encode(), sha256).hexdigest()

        # Get the analyses.
        analyses = []
        container = details.find_element(by=By.CLASS_NAME, value='layout-row')
        chips = container.find_elements(by=By.TAG_NAME, value='md-chip')
        for chip in chips:
            hidden = chip.get_attribute('aria-hidden')
            if hidden == 'false':
                analyses.append(chip.text)

        # Get the lab results URL.
        links = card.find_elements(by=By.TAG_NAME, value='a')
        lab_results_url = links[0].get_attribute('href')

        # Aggregate sample data.
        sample = {
            'analyses': analyses,
            'date_tested': date_tested,
            'images': images,
            'lab_results_url': lab_results_url,
            'producer': producer,
            'product_name': product_name,
            'product_type': product_type,
            'sample_id': sample_id,
        }
        samples.append(sample)

    return samples


def get_psi_labs_test_result_details(driver, max_delay=5) -> dict:
    """Get the test result details for a specific PSI lab result.
    Args:
        driver (WebDriver): A Selenium Chrome WebDiver.
        max_delay (float): The maximum number of seconds to wait for rendering.
    Returns:
        (dict): A dictionary of sample details.
    """

    # Deemed optional:
    # Wait for elements to load, after a maximum delay of X seconds.
    qr_code, coa_urls = None, []
    # try:

    #     # Wait for the QR code to load.
    #     detect = EC.presence_of_element_located((By.CLASS_NAME, 'qrcode-link'))
    #     qr_code_link = WebDriverWait(driver, max_delay).until(detect)

    #     # Get the QR code.
    #     qr_code = qr_code_link.get_attribute('href')

    #     # Get CoA URLs by finding all links with with `analytics-event="PDF View"`.
    #     actions = driver.find_elements(by=By.TAG_NAME, value='a')
    #     coa_urls = []
    #     for action in actions:
    #         event = action.get_attribute('analytics-event')
    #         if event == 'PDF View':
    #             href = action.get_attribute('href')
    #             coa_urls.append({'filename': action.text, 'url': href})

    # except TimeoutException:
    #     print('QR Code not loaded within %i seconds.' % max_delay)


    # Wait for the results to load.
    try:
        detect = EC.presence_of_element_located((By.TAG_NAME, 'ng-include'))
        WebDriverWait(driver, max_delay).until(detect)
    except TimeoutException:
        print('Results not loaded within %i seconds.' % max_delay)

    # Get results for each analysis.
    results = []
    date_received, sample_weight, method = None, None, None
    values = ['name', 'value', 'margin_of_error']
    analysis_cards = driver.find_elements(by=By.TAG_NAME, value='ng-include')
    for analysis in analysis_cards:
        try:
            analysis.click()
        except ElementNotInteractableException:
            continue
        rows = analysis.find_elements(by=By.TAG_NAME, value='tr')
        if rows:
            for row in rows:
                result = {}
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                for i, cell in enumerate(cells):
                    key = values[i]
                    result[key] = cell.text
                if result:
                    results.append(result)

        # Get the last few sample details: method, sample_weight, and received_at
        if analysis == 'potency':
            extra = analysis.find_element(by=By.TAG_NAME, value='md-card-content')
            headings = extra.find_elements(by=By.TAG_NAME, value='h3')
            mm, dd, yy = tuple(headings[0].text.split('/'))
            date_received = f'20{yy}-{mm}-{dd}'
            sample_weight = headings[1].text
            method = headings[-1].text

    # Aggregate sample details.
    details = {
        'coa_urls': coa_urls,
        'date_received': date_received,
        'method': method,
        'qr_code': qr_code,
        'results': results,
        'sample_weight': sample_weight,
    }
    return details


# FIXME: This function doesn't work well.
def get_all_psi_labs_test_results(service, pages, pause=0.125, verbose=True):
    """Get ALL of PSI Labs test results.
    Args:
        service (ChromeDriver): A ChromeDriver service.
        pages (iterable): A range of pages to get lab results from.
        pause (float): A pause between requests to respect PSI Labs' server.
        verbose (bool): Whether or not to print out progress, True by default (optional).
    Returns:
        (list): A list of collected lab results.
    """

    # Create a headless Chrome browser.
    options = Options()
    options.headless = True
    options.add_argument('--window-size=1920,1200')
    driver = webdriver.Chrome(options=options, service=service)

    # Iterate over all of the pages to get all of the samples.
    test_results = []
    for page in pages:
        if verbose:
            print('Getting samples on page:', page)
        driver.get(BASE.format(str(page)))
        results = get_psi_labs_test_results(driver)
        if results:
            test_results += results
        else:
            print('Failed to find samples on page:', page)
        sleep(pause)

    # Get the details for each sample.
    for i, test_result in enumerate(test_results):
        if verbose:
            print('Getting details for:', test_result['product_name'])
        driver.get(test_result['lab_results_url'])
        details = get_psi_labs_test_result_details(driver)
        test_results[i] = {**test_result, **details}
        sleep(pause)

    # Close the browser and return the results.
    driver.quit()
    return test_results


#-----------------------------------------------------------------------
# Test: Data aggregation with `get_all_psi_labs_test_results`.
#-----------------------------------------------------------------------

# if __name__ == '__main__':

#     # Specify the full-path to your chromedriver.
#     # You can also put your chromedriver in `C:\Python39\Scripts`.
#     # DRIVER_PATH = '../assets/tools/chromedriver_win32/chromedriver'
#     # full_driver_path = os.path.abspath(DRIVER_PATH)
#     start = datetime.now()
#     service = Service()

#     # Create a headless Chrome browser.
#     options = Options()
#     options.headless = True
#     options.add_argument('--window-size=1920,1200')
#     driver = webdriver.Chrome(options=options, service=service)

#     # Iterate over all of the pages to get all of the samples.
#     errors = []
#     test_results = []
#     pages = list(PAGES)
#     pages.reverse()
#     for page in pages:
#         print('Getting samples on page:', page)
#         driver.get(BASE.format(str(page)))
#         results = get_psi_labs_test_results(driver)
#         if results:
#             test_results += results
#         else:
#             print('Failed to find samples on page:', page)
#             errors.append(page)

#     # Get the details for each sample.
#     rows = []
#     samples = pd.DataFrame(test_results)
#     total = len(samples)
#     for index, values in samples.iterrows():
#         percent = round((index  + 1) / total * 100, 2)
#         print('Collecting (%.2f%%) (%i/%i):' % (percent, index + 1, total), values['product_name'])
#         driver.get(values['lab_results_url'])
#         details = get_psi_labs_test_result_details(driver)
#         rows.append({**values.to_dict(), **details})
            
#     # Save the results.
#     data = pd.DataFrame(rows)
#     timestamp = datetime.now().isoformat()[:19].replace(':', '-')
#     datafile = f'{DATA_DIR}/psi-lab-results-{timestamp}.xlsx'
#     data.to_excel(datafile, index=False)
#     end = datetime.now()
#     print('Runtime took:', end - start)

#     # Close the browser.
#     driver.quit()


#-----------------------------------------------------------------------
# TODO: Preprocessing the Data
#-----------------------------------------------------------------------

ANALYSES = {
    'cannabinoids': ['potency', 'POT'],
    'terpenes': ['terpene', 'TERP'],
    'residual_solvents': ['solvent', 'RST'],
    'pesticides': ['pesticide', 'PEST'],
    'microbes': ['microbial', 'MICRO'],
    'heavy_metals': ['metal', 'MET'],
}
ANALYTES = {
    # TODO: Define all of the known analytes from the Cannlytics library.
}
DECODINGS = {
    '<LOQ': 0,
    '<LOD': 0,
    'ND': 0,
}


# Read in the saved results.
datafile = f'{DATA_DIR}/aggregated-cannabis-test-results.xlsx'
data = pd.read_excel(datafile, sheet_name='psi_labs_raw_data')

# Optional: Drop rows with no analyses at this point.
drop = ['coa_urls', 'date_received', 'method', 'qr_code', 'sample_weight']
data.drop(drop, axis=1, inplace=True)

# Isolate a training sample.
sample = data.sample(100, random_state=420)


# Create both wide and long data for ease of use.
# See: https://rstudio-education.github.io/tidyverse-cookbook/tidy.html
# Normalize and clean the data. In particular, flatten:
# ✓ `analyses`
# ✓ `results`
# - `images`
wide_data = pd.DataFrame()
long_data = pd.DataFrame()
for index, row in sample.iterrows():
    series = row.copy()
    analyses = literal_eval(series['analyses'])
    images = literal_eval(series['images'])
    results = literal_eval(series['results'])
    series.drop(['analyses', 'images', 'results'], inplace=True)

    # Code analyses.
    if not analyses:
        continue
    for analysis in analyses:
        series[analysis] = 1
    
    # Add to wide data.
    wide_data = pd.concat([wide_data, pd.DataFrame([series])])

    # Iterate over results, cleaning results and adding columns.
    # Future work: Augment results with key, limit, and CAS.
    for result in results:

        # Clean the values.
        analyte_name = result['name']
        measurements = result['value'].split(' ')
        try:
            measurement = float(measurements[0])
        except:
            measurement = None
        try:
            units = measurements[1]
        except:
            units = None
        key = snake_case(analyte_name)
        try:
            margin_of_error = float(result['margin_of_error'].split(' ')[-1])
        except:
            margin_of_error = None

        # Format long data.
        entry = series.copy()
        entry['analyte'] = key
        entry['analyte_name'] = analyte_name
        entry['result'] = measurement
        entry['units'] = units
        entry['margin_of_error'] = margin_of_error

        # Add to long data.
        long_data = pd.concat([long_data, pd.DataFrame([entry])])


# Fill null observations.
wide_data = wide_data.fillna(0)

# Rename columns
analyses = {
    'POT': 'cannabinoids',
    'RST': 'residual_solvents',
    'TERP': 'terpenes',
    'PEST': 'pesticides',
    'MICRO': 'micro',
    'MET': 'heavy_metals',
}
wide_data.rename(columns=analyses, inplace=True)
long_data.rename(columns=analyses, inplace=True)


#------------------------------------------------------------------------------
# Processing the data.
#------------------------------------------------------------------------------

# Calculate totals:
# - `total_cbd`
# - `total_thc`
# - `total_terpenes`
# - `total_cannabinoids`
# - `total_cbg`
# - `total_thcv`
# - `total_cbc`
# - `total_cbdv`


# Optional: Add `status` variables for pass / fail tests.


# TODO: Augment with:
# - lab details: lab, lab_url, lab_license_number, etc.
# - lab_latitude, lab_longitude

# Future work: Calculate average results by state, county, and zip code.


#------------------------------------------------------------------------------
# Exploring the data.
#------------------------------------------------------------------------------

# Count the number of various tests.
terpenes = wide_data.loc[wide_data['terpenes'] == 1]

# Find all of the analytes.
analytes = list(long_data.analyte.unique())

# Find all of the product types.
product_types = list(long_data.product_type.unique())

# Look at cannabinoid distributions by type.
flower = long_data.loc[long_data['product_type'] == 'Flower']
flower.loc[flower['analyte'] == '9_thc']['result'].hist(bins=100)

concentrates = long_data.loc[long_data['product_type'] == 'Concentrate']
concentrates.loc[concentrates['analyte'] == '9_thc']['result'].hist(bins=100)


# Look at terpene distributions by type!
terpene = flower.loc[flower['analyte'] == 'dlimonene']
terpene['result'].hist(bins=100)

terpene = concentrates.loc[concentrates['analyte'] == 'dlimonene']
terpene['result'].hist(bins=100)


# Find the first occurrences of famous strains.
gorilla_glue = flower.loc[
    (flower['product_name'].str.contains('gorilla', case=False)) |
    (flower['product_name'].str.contains('glu', case=False))    
]

# Create strain fingerprints: histograms of dominant terpenes.
compound = gorilla_glue.loc[gorilla_glue['analyte'] == '9_thc']
compound['result'].hist(bins=100)


#------------------------------------------------------------------------------
# Exploring the data.
#------------------------------------------------------------------------------

# Future work: Augment results with key, limit, and CAS.

# TODO: Save the curated data, both wide and long data.


# TODO: Standardize the `analyte` names! Ideally with a re-usable function.


# TODO: Standardize `analyses`.


# TODO: Standardize the `product_type`.


# TODO: Standardize `strain_name`.


# TODO: Add any new entries to the Cannlypedia:
# - New `analyses`
# - New `analytes`
# - New `strains`
# - New `product_types`


# Optional: Create data / CoA NFTs for the lab results!!!


#------------------------------------------------------------------------------
# Exploring the data.
#------------------------------------------------------------------------------

# TODO: Count the number of lab results scraped!


# TODO: Count the number of unique data points scraped!


# TODO: Look at cannabinoid concentrations over time.


# TODO: Look at cannabinoid distributions by type.


# TODO: Look at terpene distributions by type!


#-----------------------------------------------------------------------
# Modeling the data.
#-----------------------------------------------------------------------

# TODO: Given a lab result, predict if it's in the Xth percentile.


# TODO: Use in ARIMA model to approach the question:
# Are terpene or cannabinoid concentrations increasing over time by sample type?
# - total_terpenes
# - D-limonene
# - beta-pinene
# - myrcene
# - caryophyllene
# - linalool
# - cbg
# - thcv
# - total_thc
# - total_cbd
# - total_cannabinoids


# Calculate THC to CBD ratio.


# Calculate average terpene ratios by strain:
# - beta-pinene to d-limonene ratio
# - humulene to caryophyllene
# - linalool and myrcene? (Research these!)


# Future work: Add description of why the ratio is meaningful.


# Future work: Calculator to determine the number of mg's of each
# compound are in a given unit of weight.
# E.g. How much total THC in mg is in an eighth given that it tests X%.
# mg = percent * 10 * grams
# mg_per_serving = percent * 10 * grams_per_serving (0.33 suggested?)


# TODO: Find parents and crosses of particular strains.
# E.g. Find all Jack crosses.


#-----------------------------------------------------------------------
# Training and testing the model.
#-----------------------------------------------------------------------

# TODO: Separate results after 2020 as test data.


# TODO: Estimate a large number of ARIMA models on the training data,
# use the models to predict the test data, and measure the accuracies.


# TODO: Pick the model that predicts the test data the best.


#-----------------------------------------------------------------------
# Evaluating the model.
#-----------------------------------------------------------------------

# TODO: Re-estimate the model with the entire dataset.


# TODO: Predict if cannabinoid and terpene concentrations are trending
# up or down and to what degree if so.


# TODO: Take away an insight: Is there statistical evidence that
# cannabis cultivated in Michigan is successfully being bred to, on average,
# have higher levels of cannabinoids or terpenes? If so, which compounds?


# TODO: Forecast: If the trend continues, what would cannabis look like
# in 10 years? What average cannabinoid and terpene concentration can
# we expect to see in Michigan in 2025 and 2030?



#-----------------------------------------------------------------------
# Saving the data, statistics, and model.
#-----------------------------------------------------------------------
# Note: The data, statistics, and model are only useful if we can get
# them # in front of people's eyeballs. Therefore, saving the data and
# making them available to people is arguably the most important step.
#-----------------------------------------------------------------------

# TODO: Upload the data to Firestore.


# TODO: Test getting the data and statistics through the Cannlytics API.


# TODO: Test using the statistical model through the Cannlytics API.
