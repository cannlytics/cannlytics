"""
Parse Confident Cannabis CoA
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/26/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Confident Cannabis CoA.

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
    ✓ classification
    ✓ coa_urls
    ✓ date_tested
    - date_received
    ✓ images
    ✓ lab_results_url
    ✓ producer
    ✓ product_name
    ✓ product_type
    ✓ predicted_aromas
    ✓ results
    - sample_weight
    - total_cannabinoids (calculated)
    ✓ total_thc
    ✓ total_cbd
    - total_terpenes (calculated)
    ✓ sample_id (generated)
    ✓ strain_name
    ✓ lab_id
    ✓ lab
    ✓ lab_image_url
    - lab_license_number
    ✓ lab_address
    ✓ lab_city
    - lab_county (augmented)
    ✓ lab_state
    ✓ lab_zipcode
    ✓ lab_phone
    ✓ lab_email
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from typing import Any, Optional

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

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import snake_case, strip_whitespace


CONFIDENT_CANNABIS = {
    'coa_parsing_algorithm': 'parse_cc_url',
    'coa_qr_code_index': 3,
    'lims': 'Con\x00dent Cannabis',
    'url': 'https://orders.confidentcannabis.com',
}


def parse_cc_pdf(
        self,
        doc: Any,
        max_delay: Optional[float] = 7,
        persist: Optional[bool] = False,
    ) -> dict:
    """Parse a Confident Cannabis CoA PDF.
    Args:
        doc (str or PDF): A file path to a PDF or a pdfplumber PDF.
        max_delay (float): The maximum number of seconds to wait
            for the page to load.
        persist (bool): Whether to persist the driver.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """
    return self.parse_pdf(
        self,
        doc,
        lims='Confident Cannabis',
        max_delay=max_delay,
        persist=persist,
    )

def parse_cc_url(
        self,
        url: str,
        headers: Optional[Any] = None,
        max_delay: Optional[float] = 7,
        persist: Optional[bool] = False,
    ) -> dict:
    """Parse a Confident Cannabis CoA URL.
    Args:
        url (str): The CoA URL.
        headers (Any): Optional headers for standardization.
        max_delay (float): The maximum number of seconds to wait
            for the page to load.
        persist (bool): Whether to persist the driver.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """
    lims = 'Confident Cannabis'

    # Load the lab results with Selenium.
    if self.service is None:
        self.service = Service()
        self.options = Options()
        self.options.add_argument('--window-size=1920,1200')
        # Uncomment for dev:
        # self.options.headless = False
        # Uncomment for production!!!
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
    if self.driver is None:
        self.driver = webdriver.Chrome(
            options=self.options,
            service=self.service,
        )
    self.driver.get(url)
    try:
        el = (By.CLASS_NAME, 'product-box-cc')
        detect = EC.presence_of_element_located(el)
        WebDriverWait(self.driver, max_delay).until(detect)
    except TimeoutException:
        print('Failed to load page within %i seconds.' % max_delay)

    # Get sample observation.
    obs = {'analyses': [], 'results': [], 'lims': lims}

    # Find the sample image.
    el = self.driver.find_element(
        by=By.CLASS_NAME,
        value='product-box-cc'
    )
    img = el.find_element(by=By.TAG_NAME, value='img')
    image_url = img.get_attribute('src')
    filename = image_url.split('/')[-1]
    obs['images'] = [{'url': image_url, 'filename': filename}]

    # Try to get sample details.
    el = self.driver.find_element(
        by=By.CLASS_NAME,
        value='product-desc',
    )
    block = el.text.split('\n')
    product_name = block[0]
    strain_name, product_type = tuple(block[3].split(', '))
    obs['product_name'] = product_name
    obs['lab_id'] = block[1]
    obs['classification'] = block[2]
    obs['strain_name'] = strip_whitespace(strain_name)
    obs['product_type'] = strip_whitespace(product_type)

    # Get the date tested.
    el = self.driver.find_element(by=By.CLASS_NAME, value='report')
    span = el.find_element(by=By.TAG_NAME, value='span')
    tooltip = span.get_attribute('uib-tooltip')
    tested_at = tooltip.split(': ')[-1]
    date_tested = pd.to_datetime(tested_at).isoformat()
    obs['date_tested'] = date_tested

    # Get the CoA URL.
    button = el.find_element(by=By.TAG_NAME, value='button')
    href = button.get_attribute('href')
    base = url.split('/report')[0]
    coa_url = base.replace('/#!', '') + href
    filename = image_url.split('/')[-1].split('?')[0] + '.pdf'
    obs['coa_urls'] = [{'url': coa_url, 'filename': filename}]

    # Find the `analyses` and `results`.
    els = self.driver.find_elements(by=By.CLASS_NAME, value='ibox')
    for i, el in enumerate(els):
        try:
            title = el.find_element(
                by=By.TAG_NAME,
                value='h5',
            ).text.lower()
        except:
            continue

        # Try to get cannabinoids data.
        if title == 'cannabinoids':
            totals = el.find_elements(
                by=By.TAG_NAME,
                value='compound-box',
            )
            for total in totals:
                value = total.find_element(
                    by=By.CLASS_NAME,
                    value='value',
                ).text
                units = total.find_element(
                    by=By.CLASS_NAME,
                    value='unit',
                ).text
                name = total.find_element(
                    by=By.CLASS_NAME,
                    value='name',
                ).text
                key = snake_case(name)
                obs[key] = value
                obs[f'{key}_units'] = units.replace('%', 'percent')

            # Get the cannabinoids totals.
            columns = ['name', 'value', 'mg_g']
            table = el.find_element(by=By.TAG_NAME, value='table')
            rows = table.find_elements(by=By.TAG_NAME, value='tr')
            for row in rows[1:]:
                result = {}
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                for i, cell in enumerate(cells):
                    key = columns[i]
                    value = cell.get_attribute('textContent').strip()
                    if key == 'name':
                        value = self.analytes.get(value, snake_case(value))
                    result[key] = value
                obs['results'].append(result)

        # Try to get terpene data.
        if title == 'terpenes':
            columns = ['name', 'value', 'mg_g']
            table = el.find_element(by=By.TAG_NAME, value='table')
            rows = table.find_elements(by=By.TAG_NAME, value='tr')
            for row in rows[1:]:
                result = {}
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                for i, cell in enumerate(cells):
                    key = columns[i]
                    value = cell.get_attribute('textContent').strip()
                    if key == 'name':
                        value = self.analytes.get(value, snake_case(value))
                    result[key] = value
                obs['results'].append(result)

            # Try to get predicted aromas.
            container = el.find_element(by=By.CLASS_NAME, value='row')
            aromas = container.text.split('\n')
            obs['predicted_aromas'] = [snake_case(x) for x in aromas]

        # Ty to get screening data.
        if title == 'safety':
            obs['status'] = el.find_element(
                by=By.CLASS_NAME,
                value='sample-status',
            ).text
            table = el.find_element(by=By.TAG_NAME, value='table')
            rows = table.find_elements(by=By.TAG_NAME, value='tr')
            for row in rows[1:]:
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                status = cells[1].get_attribute('textContent').strip()
                if status == 'Not Tested':
                    continue
                analysis = snake_case(cells[0].get_attribute('textContent'))
                obs[f'{analysis}_status'] = status.lower()
                obs['analyses'].append(analysis)

                # Click the row. and get all of the results from the modal!
                # Future work: Make these columns dynamic.
                columns = ['name', 'status', 'value', 'limit', 'loq']
                if row.get_attribute('class') == 'clickable-content':
                    try:
                        row.click()
                    except ElementNotInteractableException:
                        continue
                    modal = self.driver.find_element(
                        by=By.ID,
                        value='safety-modal-table'
                    )
                    modal_table = modal.find_element(
                        by=By.TAG_NAME,
                        value='tbody'
                    )
                    modal_rows = modal_table.find_elements(
                        by=By.TAG_NAME,
                        value='tr'
                    )
                    headers = modal.find_elements(
                        by=By.TAG_NAME,
                        value='th',
                    )
                    units = headers[-1].text.split('(')[-1].replace(')', '')
                    for modal_row in modal_rows:
                        result = {'units': units}
                        modal_cells = modal_row.find_elements(
                            by=By.TAG_NAME,
                            value='td'
                        )
                        for i, modal_cell in enumerate(modal_cells):
                            key = columns[i]
                            value = modal_cell.get_attribute(
                                'textContent'
                            ).strip()
                            if key == 'name':
                                value = self.analytes.get(value, snake_case(value))
                            result[key] = value
                        obs['results'].append(result)   
                    try:
                        body = self.driver.find_element(
                            by=By.TAG_NAME,
                            value='body'
                        )
                        body.click()
                    except ElementNotInteractableException:
                        continue  

        # Try to get lab data.
        producer = ''
        if title == 'order info':
            img = el.find_element(by=By.TAG_NAME, value='img')
            producer = el.find_element(
                by=By.CLASS_NAME,
                value='public-name',
            ).text
            license_el = el.find_element(
                by=By.TAG_NAME,
                value='confident-address',
            )
            lab = license_el.find_element(
                by=By.CLASS_NAME,
                value='address-name',
            ).text
            lab_phone = license_el.find_element(
                by=By.CLASS_NAME,
                value='address-phone',
            ).text.split(': ')[-1]
            lab_email = license_el.find_element(
                by=By.CLASS_NAME,
                value='address-email',
            ).text
            block = el.find_element(
                by=By.TAG_NAME,
                value='confident-address',
            ).text.split('\n')
            street = block[1]
            address = tuple(block[2].split(', '))
            obs['lab'] = lab
            obs['lab_address'] = f'{street} {", ".join(address)}'
            obs['lab_image_url'] = img.get_attribute('src')
            obs['lab_street'] = street
            obs['lab_city'] = address[0]
            obs['lab_state'], obs['lab_zipcode'] = tuple(address[-1].split(' '))
            obs['lab_phone'] = lab_phone
            obs['lab_email'] = lab_email
            obs['producer'] = producer

    # Return the sample with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=producer,
        public_key=product_name,
        salt=date_tested,
    )

    # Close the Chrome driver once all PDFs have been parsed.
    if not persist:
        self.quit()
    return obs

if __name__ == '__main__':

    # Test Confident Cannabis CoAs parsing.
    from cannlytics.data.coas import CoADoc

    # Specify where your test data lives.
    DATA_DIR = '../../../.datasets/coas'
    cc_coa_pdf = f'{DATA_DIR}/Classic Jack.pdf'
    cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/4ee67b54-be74-44e4-bb94-4f44d8294062'

    # [✓] TEST: Parse a CoA URL.
    parser = CoADoc()
    data = parse_cc_url(parser, cc_coa_url)
    assert data is not None

    # [✓] TEST: Parse a CoA PDF.
    parser = CoADoc()
    data = parse_cc_pdf(parser, cc_coa_pdf)
    assert data is not None
