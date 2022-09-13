"""
Parse TagLeaf LIMS CoA
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/15/2022
Updated: 8/30/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a TagLeaf LIMS CoA PDF or URL.

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
    - coa_urls
    ✓ date_tested
    - date_received
    ✓ distributor
    ✓ distributor_license_number
    ✓ distributor_license_type
    - distributor_latitude (augmented)
    - distributor_longitude (augmented)
    ✓ images
    ✓ lab_results_url
    ✓ producer
    - producer_latitude (augmented)
    - producer_longitude (augmented)
    ✓ product_name
    ✓ product_type
    ✓ results
    - sample_weight
    ✓ status
    ✓ total_cannabinoids
    ✓ total_thc
    ✓ total_cbd
    - total_terpenes (calculated)
    ✓ sample_id (generated)
    - lab_id
    ✓ lab
    ✓ lab_image_url
    ✓ lab_license_number
    ✓ lab_address
    - lab_city
    - lab_county (augmented)
    - lab_state
    - lab_zipcode
    ✓ lab_phone
    - lab_email
    - lab_latitude (augmented)
    - lab_longitude (augmented)

"""
# Standard imports.
from datetime import datetime
import json
from typing import Any, Optional

# External imports.
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import pdfplumber
from requests import Session

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.constants import ANALYSES, STANDARD_UNITS
from cannlytics.utils.utils import (
    convert_to_numeric,
    snake_case,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
TAGLEAF = {
    'coa_algorithm': 'tagleaf.py',
    'coa_algorithm_entry_point': 'parse_tagleaf_coa',
    'lims': 'lims.tagleaf',
    'url': 'https://lims.tagleaf.com',
    'public': True,
}


def parse_tagleaf_url(
        parser,
        url: str,
        headers: Optional[dict] = None,
        keys: Optional[dict] = None,
        persist: Optional[bool] = False,
        **kwargs,
    ) -> dict:
    """Parse a TagLeaf LIMS CoA URL.
    Args:
        url (str): The CoA URL.
        headers (dict): Headers for HTTP requests.
        keys (dict): A dictionary of keys for standardization.
        max_delay (float): Unused argument for standardization.
        persist (bool): Whether to persist the session.
            The default is `False`. If you do persist
            the driver, then make sure to call `quit`
            when you are finished.
    Returns:
        (dict): The sample data.
    """

    # Get the HTML.
    if keys is None:
        keys = parser.fields
    if headers is None:
        headers = parser.headers
    if parser.session is None:
        parser.session = Session()
    response = parser.session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the date tested.
    obs = {}
    el = soup.find('p', attrs={'class': 'produced-statement'})
    date_tested = pd.to_datetime(el.text.split(': ')[-1]).isoformat()
    obs['date_tested'] = date_tested

    # Get lab details.
    el = soup.find('section', attrs={'class': 'header-container'})
    img = el.find('img')
    pars = el.find_all('p')
    details = [strip_whitespace(x) for x in pars[0].text.split('//')]
    address = details[1]
    obs['lab'] = details[0]
    obs['lab_address'] = address
    obs['lab_image_url'] = img.attrs['src']
    obs['lab_phone'] = details[2].replace('PH: ', '')

    # Get data from headings.
    text = soup.find_all('p', attrs={'class': 'h5'}, limit=2)
    parts = strip_whitespace(text[0].text.split('//')[0]).split(' (')
    product_name = parts[0]
    obs['product_name'] = product_name
    obs['product_type'] = parts[1].replace(')', '')
    obs['status'] = strip_whitespace(text[1].text.split(':')[-1]).lower()

    # Get cannabinoid totals.
    el = soup.find('div', attrs={'class': 'cannabinoid-overview'})
    rows = el.find_all('div', attrs={'class': 'row'})
    for row in rows:
        pars = row.find_all('p')
        key = snake_case(strip_whitespace(pars[1].text))
        value = strip_whitespace(pars[0].text)
        if key == 'sample_weight':
            continue
        if key in ['value', 'mg_g', 'lod', 'loq']:
            value = convert_to_numeric(value, strip=True)
        obs[key] = value

    # Get cultivator and distributor details.
    els = soup.find_all('div', attrs={'class': 'license'})
    values = [x.text for x in els[0].find_all('p')]
    producer = values[1]
    obs['producer'] = producer
    obs['license_number'] = values[3]
    obs['license_type'] = values[5]
    values = [x.text for x in els[1].find_all('p')]
    obs['distributor'] = values[1]
    obs['distributor_license_number'] = values[3]
    obs['distributor_license_type'] = values[5]

    # Get the sample image.
    el = soup.find('div', attrs={'class': 'sample-photo'})
    img = el.find('img')
    image_url = img['src']
    filename = image_url.split('/')[-1]
    obs['images'] = [{'url': image_url, 'filename': filename}]

    # Get the sample details
    el = soup.find('div', attrs={'class': 'sample-info'})
    pars = el.find_all('p')
    for par in pars:
        key = snake_case(par.find('span').text)
        key = keys.get(key, key) # Get preferred key.
        text = par.contents
        value = ''.join([x for x in text if type(x) == NavigableString])
        value = strip_whitespace(value)
        obs[key] = value

    # Get the lab ID and metrc ID.
    obs['lab_id'] = obs.get('sample_id', '')
    obs['metrc_ids'] = [obs.get('source_metrc_uid', '')]

    # Format `date_collected` and `date_received` dates.
    try:
        obs['date_collected'] = pd.to_datetime(obs['date_collected']).isoformat()
        obs['date_received'] = pd.to_datetime(obs['date_received']).isoformat()
    except KeyError:
        pass

    # Get the analyses and `{analysis}_status`.
    analyses = []
    el = soup.find('div', attrs={'class': 'tests-overview'})
    blocks = strip_whitespace(el.text)
    blocks = [x for x in blocks.split('    ') if x]
    for i, value in enumerate(blocks):
        if i % 2:
            analysis = analyses[-1]
            if value != '\xa0':
                obs[f'{analysis}_status'] = value.lower()
        else:
            analysis = snake_case(value)
            analysis = keys.get(analysis, analysis) # Get preferred key.
            analyses.append(analysis)
    obs['analyses'] = analyses

    # Get `{analysis}_method`s.
    els = soup.find_all('div', attrs={'class': 'table-header'})
    for el in els:
        analysis = el.attrs['id'].replace('_test', '')
        analysis = keys.get(analysis, analysis) # Get preferred key.
        title = el.find('h3').contents
        text = ''.join([x for x in title if type(x) == NavigableString])
        obs[f'{analysis}_method'] = strip_whitespace(text)

    # Get the `results`, using the table header for the columns,
    # noting that `value` is repeated for `mg_g`.
    results = []
    tables = soup.find_all('table')
    for table in tables:

        # Find the analysis of the table.
        title = table.find_previous('h3').contents
        text = ''.join([x for x in title if type(x) == NavigableString])
        analysis = strip_whitespace(text).split(':')[-1].split('by')[0].strip()
        analysis = ANALYSES.get(analysis, snake_case(analysis))
        units = STANDARD_UNITS.get(analysis)

        # Find the columns of the table.
        headers = table.find_all('th')
        columns = [keys[strip_whitespace(x.text)] for x in headers]

        # Iterate over all of the rows of the table.
        rows = table.find_all('tr')[1:]
        for row in rows:
            analyte = None
            mg_g = False
            result = {
                'analysis': analysis,
                'units': units,
            }
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                key = columns[i]
                value = strip_whitespace(cell.text)
                if key == 'name':
                    analyte = parser.analytes.get(value, snake_case(value))
                    result['key'] = analyte
                if key == 'value' and mg_g:
                    key = 'mg_g'
                if key == 'value':
                    mg_g = True
                if key in ['value', 'mg_g', 'lod', 'loq', 'limit'] and value != 'ND':
                    value = value.replace('< 1 mg/g', 'ND')
                    value = convert_to_numeric(value, strip=True)
                result[key] = value

            # Hot-fix: Handle status.
            if result.get('status') == 'N/A':
                result['status'] = None

            # Handle totals.
            if analyte.startswith('total') and obs.get(analyte) is None:
                obs[analyte] = convert_to_numeric(value, strip=True)
            else:
                results.append(result)

    # Return the sample with a freshly minted sample ID.
    obs['results'] = results
    obs['sample_id'] = create_sample_id(
        private_key=json.dumps(results),
        public_key=product_name,
        salt=producer,
    )
    obs['coa_parsed_at'] = datetime.now().isoformat()
    if not persist:
        parser.quit()
    return {**TAGLEAF, **obs}


def parse_tagleaf_pdf(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a TagLeaf LIMS CoA PDF.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    url = parser.find_pdf_qr_code_url(doc)
    return parse_tagleaf_url(parser, url, **kwargs)


def parse_tagleaf_coa(
        parser,
        doc: Any,
        **kwargs,
    ) -> dict:
    """Parse a TagLeaf LIMS CoA PDF or URL.
    Args:
        doc (str or PDF): A PDF file path or pdfplumber PDF.
    Returns:
        (dict): The sample data.
    """
    if isinstance(doc, str):
        if doc.startswith('http'):
            return parse_tagleaf_url(parser, doc, **kwargs)
        elif doc.endswith('.pdf'):
            data = parse_tagleaf_pdf(parser, doc, **kwargs)
        else:
            data = parse_tagleaf_pdf(parser, doc, **kwargs)
    else:
        data = parse_tagleaf_pdf(parser, doc, **kwargs)
    if isinstance(doc, str):
        data['coa_pdf'] = doc.replace('\\', '/').split('/')[-1]
    elif isinstance(doc, pdfplumber.pdf.PDF):
        data['coa_pdf'] = doc.stream.name.replace('\\', '/').split('/')[-1]
    return data


if __name__ == '__main__':

    # Test TagLeaf LIMS CoAs parsing.
    from cannlytics.data.coas import CoADoc

     # Specify where your test data lives.
    DATA_DIR = '../../../tests/assets/coas'
    tagleaf_coa_pdf = f'{DATA_DIR}/Sunbeam.pdf'
    tagleaf_coa_url = 'https://lims.tagleaf.com/coas/F6LHqs9rk9vsvuILcNuH6je4VWCiFzdhgWlV7kAEanIP24qlHS'
    tagleaf_coa_short_url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'

    # [✓] TEST: Parse a CoA URL.
    parser = CoADoc()
    data = parse_tagleaf_url(parser, tagleaf_coa_url)
    assert data is not None

    # [✓] TEST: Parse a TagLeaf LIMS CoA PDF.
    parser = CoADoc()
    data = parse_tagleaf_pdf(parser, tagleaf_coa_pdf)
    assert data is not None
