"""
Parse TagLeaf LIMS CoA
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/21/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse a TagLeaf LIMS CoA.

Data Points:

    ✓ analyses
    - {analysis}_method
    ✓ {analysis}_status
    - classification
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
    - strain_name (predict later)
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
from typing import Any, Optional

# External imports.
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
from requests import Session

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import snake_case, strip_whitespace


TAGLEAF = {
    'coa_parsing_algorithm': 'parse_tagleaf_url',
    'coa_qr_code_index': 2,
    'key': 'lims.tagleaf',
    'url': 'https://lims.tagleaf.com',
}


def parse_tagleaf_pdf(
        self,
        doc: Any,
        headers: Optional[dict] = None,
        persist: Optional[bool] = False,
    ) -> dict:
    """Parse a TagLeaf LIMS CoA PDF.
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
        lims='TagLeaf LIMS',
        headers=headers,
        persist=persist,
    )


def parse_tagleaf_url(
        self,
        url: str,
        headers: Optional[dict] = None,
        keys: Optional[dict] = None,
        max_delay: Optional[float] = 7,
        persist: Optional[bool] = False,
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
    lims = 'TagLeaf LIMS'

    # Get the HTML.
    if keys is None:
        keys = self.keys
    if headers is None:
        headers = self.headers
    if self.session is None:
        self.session = Session()
    response = self.session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the date tested.
    obs = {'analyses': [], 'results': [], 'lims': lims}
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
    tables = soup.find_all('table')
    for table in tables:
        headers = table.find_all('th')
        columns = [keys[strip_whitespace(x.text)] for x in headers]
        rows = table.find_all('tr')[1:]
        for row in rows:
            mg_g = False
            result = {}
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                key = columns[i]
                value = strip_whitespace(cell.text)
                if key == 'name':
                    value = self.analytes.get(value, snake_case(value))
                if key == 'value' and mg_g:
                    key = 'mg_g'
                if key == 'value':
                    mg_g = True
                result[key] = value
            obs['results'].append(result)

    # Return the sample with a freshly minted sample ID.
    obs['sample_id'] = create_sample_id(
        private_key=producer,
        public_key=product_name,
        salt=date_tested,
    )
    if not persist:
        self.quit()
    return obs


if __name__ == '__main__':

     # Specify where your test data lives.
    DATA_DIR = '../../../.datasets/coas'

    # Test TagLeaf LIMS CoAs parsing.
    tagleaf_coa_pdf = f'{DATA_DIR}/Sunbeam.pdf'
    tagleaf_coa_url = 'https://lims.tagleaf.com/coas/F6LHqs9rk9vsvuILcNuH6je4VWCiFzdhgWlV7kAEanIP24qlHS'
    tagleaf_coa_short_url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'

    from cannlytics.data.coas import CoADoc

    # # Parse a CoA URL.
    # parser = CoADoc()
    # data = parse_tagleaf_url(parser, tagleaf_coa_url)
    # assert data is not None

    # FIXME: Parse a CoA PDF.
    parser = CoADoc()
    data = parse_tagleaf_pdf(parser, tagleaf_coa_pdf)
    assert data is not None
