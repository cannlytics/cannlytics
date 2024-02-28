"""
Parse Confident Cannabis CoA
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/15/2022
Updated: 12/31/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a Confident Cannabis CoA PDF or URL. Labs include:

        - CaliGreen Laboratory
        - California Ag Labs
        - CB Labs Novato
        - Harrens Lab Inc

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
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
    ✓ strain_type
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
from datetime import datetime
import json
from time import sleep
from typing import Any, Optional

# External imports.
import pandas as pd
from pdfplumber.pdf import PDF
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Internal imports.
from cannlytics import __version__
from cannlytics.data.data import create_hash, create_sample_id
from cannlytics.data.web import initialize_selenium
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    strip_whitespace,
)


# It is assumed that the lab has the following details.
CONFIDENT_CANNABIS = {
    'coa_algorithm': 'confidentcannabis.py',
    'coa_algorithm_entry_point': 'parse_cc_coa',
    'lims': 'Con\x00dent Cannabis',
    'url': 'confidentcannabis.com',
    'public': True,
}


def parse_cc_url(
        parser,
        url: str,
        headers: Optional[Any] = None,
        max_delay: Optional[float] = 60,
        persist: Optional[bool] = False,
        headless: Optional[bool] = True,
        pause: Optional[float] = 10,
        **kwargs
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
    # Initialize a web driver.
    if parser.driver is None:
        parser.driver = initialize_selenium(
            headless=headless,
        )

    # Get the URL.
    parser.driver.get(url)

    # Handle shared URLs.
    if 'share.confidentcannabis.com' in url:
        iframe = WebDriverWait(parser.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe'))
        )
        url = iframe.get_attribute('src')
        parser.driver.switch_to.frame(iframe)
        sleep(pause)

    # Wait for the page to load by waiting to detect the image.
    else:
        try:
            el = (By.CLASS_NAME, 'product-box-cc')
            detect = EC.presence_of_element_located(el)
            WebDriverWait(parser.driver, max_delay).until(detect)
        except TimeoutException:
            print('Failed to load page within %i seconds.' % max_delay)

    # Create a sample observation.
    analyses, results = [], []
    obs = {'lims': 'Confident Cannabis'}

    # Find the sample image.
    # FIXME: Need to find the image with URL like this:
    # https://orders-confidentcannabis.imgix.net/samples/1909CH0015.0074/images/52de710b-5875-4903-b7f0-8b87f132ebf7?auto=enhance&fit=fill&bg=ffffff&w=287&h=260
    try:
        el = parser.driver.find_element(
            by=By.CLASS_NAME,
            value='col-md-12'
        )
        img = el.find_element(by=By.TAG_NAME, value='img')
        image_url = img.get_attribute('src')
        filename = image_url.split('/')[-1]
        obs['images'] = [{'url': image_url, 'filename': filename}]
    except:
        obs['images'] = []

    # Try to get the sample details.
    el = parser.driver.find_element(
        by=By.CLASS_NAME,
        value='product-desc',
    )
    try:
        block = el.text.split('\n')
        obs['product_name'] = block[0]
    except:
        obs['product_name'] = None
    try:
        obs['lab_id'] = block[1]
    except:
        obs['lab_id'] = None
    try:
        obs['strain_type'] = block[2]
    except:
        obs['strain_type'] = None
    try:
        parts = block[3].split(', ')
        obs['strain_name'] = strip_whitespace(', '.join(parts[:-1]))
    except:
        obs['strain_name'] = None
    try:
        obs['product_type'] = strip_whitespace(parts[-1])
    except:
        obs['product_type'] = None

    # Get the date tested.
    el = parser.driver.find_element(by=By.CLASS_NAME, value='report')
    span = el.find_element(by=By.TAG_NAME, value='span')
    tooltip = span.get_attribute('uib-tooltip')
    tested_at = tooltip.split(': ')[-1]
    obs['date_tested'] = pd.to_datetime(tested_at).isoformat()

    # Get the CoA URL.
    button = el.find_element(by=By.TAG_NAME, value='button')
    href = button.get_attribute('href')
    base = url.split('/report')[0]
    coa_url = base.replace('/#!', '') + href
    filename = url.split('/')[-1].split('?')[0] + '.pdf'
    obs['coa_urls'] = [{'url': coa_url, 'filename': filename}]

    # Find the `analyses` and `results`.
    els = parser.driver.find_elements(by=By.CLASS_NAME, value='ibox')
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
                obs[key] = convert_to_numeric(value)
                obs[f'{key}_units'] = units.replace('%', 'percent')

            # TODO: Generalize the below functionality into a function.

            # Get the cannabinoids totals.
            # Future work: Make the columns dynamic.
            columns = ['name', 'value', 'mg_g']
            try:
                table = el.find_element(by=By.TAG_NAME, value='table')
            except NoSuchElementException:
                continue
            rows = table.find_elements(by=By.TAG_NAME, value='tr')
            for row in rows[1:]:
                result = {'analysis': 'cannabinoids', 'units': 'percent'}
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                for i, cell in enumerate(cells):
                    key = columns[i]
                    value = cell.get_attribute('textContent').strip()
                    if key == 'name':
                        result['key'] = parser.analytes.get(value, snake_case(value))
                    else:
                        value = value.replace('%', '').replace('mg/g', '').strip()
                    result[key] = convert_to_numeric(value)
                results.append(result)

        # Try to get terpene data.
        # Future work: Make the columns dynamic.
        if title == 'terpenes':
            columns = ['name', 'value', 'mg_g']
            try:
                table = el.find_element(by=By.TAG_NAME, value='table')
            except NoSuchElementException:
                continue
            rows = table.find_elements(by=By.TAG_NAME, value='tr')
            for row in rows[1:]:
                result = {'analysis': 'terpenes', 'units': 'percent'}
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                for i, cell in enumerate(cells):
                    key = columns[i]
                    value = cell.get_attribute('textContent').strip()
                    if key == 'name':
                        result['key'] = parser.analytes.get(value, snake_case(value))
                    else:
                        value = value.replace('%', '').replace('mg/g', '').strip()
                    result[key] = convert_to_numeric(value)
                results.append(result)

            # Try to get predicted aromas.
            container = el.find_element(by=By.CLASS_NAME, value='row')
            aromas = container.text.split('\n')
            obs['predicted_aromas'] = [snake_case(x) for x in aromas]

        # Try to get screening data.
        if title == 'safety':
            try:
                obs['status'] = el.find_element(by=By.CLASS_NAME, value='sample-status').text
            except:
                obs['status'] = None
            try:
                table = el.find_element(by=By.TAG_NAME, value='table')
                rows = table.find_elements(by=By.TAG_NAME, value='tr')
            except:
                continue
            for row in rows[1:]:

                # Get the screening analysis.
                cells = row.find_elements(by=By.TAG_NAME, value='td')
                status = cells[1].get_attribute('textContent').strip()
                if status == 'Not Tested':
                    continue
                analysis = snake_case(cells[0].get_attribute('textContent'))
                obs[f'{analysis}_status'] = status.lower()
                analyses.append(analysis)

                # Scroll the row into view!
                parser.driver.execute_script('arguments[0].scrollIntoView(true);', row)

                # Click the row. and get all of the results from the modal!
                # Future work: Make the columns dynamic.
                columns = ['name', 'status', 'value', 'limit', 'loq']
                if row.get_attribute('class') == 'clickable-content':
                    row.click()
                    modal = parser.driver.find_element(
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
                        result = {'analysis': analysis, 'units': units}
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
                                result['key'] = parser.analytes.get(value, snake_case(value))
                            result[key] = convert_to_numeric(value)
                        results.append(result)

                    # Close the modal.
                    try:
                        button = parser.driver.find_element(
                            by=By.CLASS_NAME,
                            value='close',
                        )
                        button.click()
                    except ElementNotInteractableException:
                        continue

                    # sleep(0.33) # Brief pause to give modal time to close.
                    WebDriverWait(parser.driver, 10).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.uib-modal-window"))
                    )

        # Try to get lab data.
        producer = ''
        if title == 'order info':
            try:
                img = el.find_element(by=By.TAG_NAME, value='img')
                lab_image_url = img.get_attribute('src')
            except:
                lab_image_url = None
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

            # Extract the street, address line 1.
            try:
                lab_street = el.find_element(
                    by=By.CSS_SELECTOR,
                    value='div[ng-if="address.addressLine1 || address.address_line_1"]'
                ).text
            except NoSuchElementException:
                lab_street = ''

            # Extract address line 2, if it exists.
            try:
                suite = el.find_element(
                    by=By.CSS_SELECTOR,
                    value='div[ng-if="address.addressLine2 || address.address_line_2"]'
                ).text
                if suite:
                    lab_street = f'{lab_street} {suite}'
            except NoSuchElementException:
                pass

            # Extract city, state, and zipcode.
            try:
                address_el = el.find_element(
                    by=By.TAG_NAME,
                    value='confident-address',
                )
                city_state_zip_div = address_el.find_element(
                    by=By.XPATH,
                    value='.//div[contains(@class, "address-url")]/preceding-sibling::div[1]'
                )
                city_state_zip = city_state_zip_div.text
                lab_city, state_zip = city_state_zip.split(', ')
                lab_state, lab_zipcode = state_zip.split(' ')
            except:
                lab_city, lab_state, lab_zipcode = '', '', ''

            # Extract the lab's website
            try:
                lab_website = address_el.find_element(
                    by=By.CSS_SELECTOR,
                    value='.address-url'
                ).text
            except NoSuchElementException:
                lab_website = ''

            # Aggregate observation data.
            obs = {
                **obs,
                'lab': lab,
                'lab_address': f'{lab_street}, {lab_city}, {lab_state} {lab_zipcode}',
                'lab_street': lab_street,
                'lab_city': lab_city,
                'lab_state': lab_state,
                'lab_zipcode': lab_zipcode,
                'lab_phone': lab_phone,
                'lab_email': lab_email,
                'lab_image_url': lab_image_url,
                'lab_website': lab_website,
                'producer': producer
            }

    # Rename moisture as moisture_content.
    obs['moisture_content'] = obs.pop('moisture')

    # Calculate total terpenes.
    terp_results = [x for x in results if 'terp' in x['analysis']]
    if terp_results:
        total_terpenes = 0
        for result in terp_results:
            try:
                total_terpenes += float(result['value'])
            except ValueError:
                pass
        obs['total_terpenes'] = round(total_terpenes, 5)

    # Return the sample with a freshly minted sample ID.
    obs = {**CONFIDENT_CANNABIS, **obs}
    obs['lab_results_url'] = url
    obs['analyses'] = json.dumps(list(set(analyses)))
    obs['results'] = json.dumps(results)
    obs['coa_algorithm_version'] = __version__
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['results_hash'] = create_hash(results)
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=obs['product_name'],
        salt=producer,
    )
    obs['sample_hash'] = create_hash(obs)
    if not persist:
        parser.quit()
    return obs


def parse_cc_pdf(
        parser,
        doc: Any,
        **kwargs
    ) -> dict:
    """Parse a Confident Cannabis CoA PDF.
    Args:
        doc (str or PDF): A file path to a PDF or a pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    # FIXME: Actually parse the PDF.
    # Sometimes the data is not available through the URL.
    url = parser.find_pdf_qr_code_url(doc)
    return parse_cc_url(parser, url, **kwargs)


def parse_cc_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a Confident Cannabis CoA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('http'):
            return parse_cc_url(parser, doc, **kwargs)
        elif doc.endswith('.pdf'):
            data = parse_cc_pdf(parser, doc, **kwargs)
        else:
            data = parse_cc_pdf(parser, doc, **kwargs)
    else:
        data = parse_cc_pdf(parser, doc, **kwargs)
    if isinstance(doc, str):
        data['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    elif isinstance(doc, PDF):
        data['coa_pdf'] = doc.stream.name.replace('\\', '/').split('/')[-1]
    
    # FIXME: Supplement data from the PDF.
    if data.get('results') == '[]' and data.get('lab') == 'Encore Labs':
        print('Parsing Encore Labs PDF...')
    
    return data


# === Tests ===
# Tested: 2023-12-31 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':
    # pass

    # Test Confident Cannabis CoAs parsing.
    from cannlytics.data.coas import CoADoc

    # # [✓] Test: Ensure that the web driver works.
    # parser = CoADoc()
    # parser.driver = webdriver.Chrome(
    #     options=parser.options,
    #     service=parser.service,
    # )

    # # [✓] TEST: Parse a CoA URL.
    # cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/4ee67b54-be74-44e4-bb94-4f44d8294062'
    cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/f86633f2-a49a-4bb0-aece-8aab8e0f3b39'
    parser = CoADoc()
    data = parse_cc_url(parser, cc_coa_url, headless=False)
    assert data is not None

    # # [✓] TEST: Parse a CoA PDF.
    # cc_coa_pdf = f'{DATA_DIR}/Classic Jack.pdf'
    # parser = CoADoc()
    # data = parse_cc_pdf(parser, cc_coa_pdf)
    # assert data is not None

    # [✓] TEST: Parse a CoA PDF, figuring out that it's a CC CoA PDF.
    # directory = '../../../tests/assets/coas'
    # doc = f'{directory}/GDP.pdf'
    # parser = CoADoc()
    # lab = parser.identify_lims(doc)
    # assert lab == 'Confident Cannabis'
    # data = parse_cc_coa(parser, doc)
    # assert data is not None

    # [✓] TEST: Parse a CoA PDF, with safety screening but no terpenes.
    # directory = '../../../tests/assets/coas'
    # doc = f'{directory}/HGN_SOUR .pdf'
    # parser = CoADoc()
    # data = parse_cc_coa(parser, doc)
    # assert data is not None
