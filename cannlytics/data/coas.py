"""
CoA Parser
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/17/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Certificates of analysis (CoAs) are abundant for cultivators,
    processors, and retailers, but the data is often locked away.
    Rich, valuable laboratory data so close, yet so far away!
    Cannlytics puts these vital data points in your hands by
    parsing the PDFs, finding all the data, standardizing the data,
    and cleanly returning the data to you.

"""
# Standard imports.
import os
from typing import Any, Optional
from bs4 import BeautifulSoup
from bs4.element import NavigableString

# External imports.
import pandas as pd
import pdfplumber
from pyzbar.pyzbar import decode
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils import strip_whitespace, snake_case


# Specify where your data lives by default.
DATA_DIR = '../../.datasets/coas'


# TODO: Load known analyses and analytes from the Cannlytics library.
ANALYSES = {
    'cannabinoids': {'names': ['potency', 'POT']},
    'terpenes': {'names': ['terpene', 'TERP', 'terpenoids']},
    'residual_solvents': {'names': ['solvent', 'RST']},
    'pesticides': {'names': ['pesticide', 'PEST']},
    'microbes': {'names': ['microbial', 'MICRO']},
    'mycotoxins': {'names': ['mycotoxins', 'MYCO']},
    'heavy_metals': {'names': ['metal', 'MET']},
    'foreign_matter': {'names': ['foreign_materials']},
    'moisture_content': {'names': ['moisture']},
    'water_activity': {'names': ['WA']},
}
ANALYTES = {
    'CBC': 'cbc',
    'CBCA': 'cbca',
    'CBD': 'cbd',
    'CBDA': 'cbda',
    'CBDV': 'cbdv',
    'CBDVA': 'cbdva',
    'CBG': 'cbg',
    'CBGA': 'cbga',
    'CBN': 'cbn',
    'Δ8-THC': 'delta_8_thc',
    'Δ9-THC': 'delta_9_thc',
    'THCA': 'thca',
    'THCV': 'thcv',
    'THCVA': 'thcva',
    'Total THC(Total THC = (THCA x 0.877) + THC)': 'total_thc',
    'Total CBD(Total CBD = (CBDA x 0.877) + CBD)': 'total_cbd',
    'Total Terpenes *': 'total_terpenes',
    'Terpinolene': 'terpinolene',
    'β-Caryophyllene': 'beta_caryophyllene',
    'α-Humulene': 'humulene',
    'β-Myrcene': 'beta_myrcene',
    'Linalool': 'linalool',
    'β-Pinene': 'beta_pinene',
    'd-Limonene': 'd_limonene',
    'α-Pinene': 'alpha_pinene',
    'β-Ocimene': 'ocimene',
    'cis-Nerolidol': 'cis_nerolidol',
    'α-Bisabolol': 'alpha_bisabolol',
    'Δ3-Carene': 'carene',
    'trans-Nerolidol': 'trans_nerolidol',
    'α-Terpinene': 'alpha_terpinene',
    'γ-Terpinene': 'gamma_terpinene',
    'Caryophyllene Oxide': 'caryophyllene_oxide',
    'Geraniol': 'geraniol',
    'Eucalyptol': 'eucalyptol',
    'Camphene': 'camphene',
    'Guaiol': 'guaiol',
    'Isopulegol': 'isopulegol',
    'p-Cymene': 'p_cymene',
    'α-Ocimene': 'alpha_ocimene',
    '* Beyond scope of accreditation': 'wildcard',
    'Moisture': 'moisture_content',
    'Aspergillus flavus': 'aspergillus_flavus',
    'Aspergillus fumigatus': 'aspergillus_fumigatus',
    'Aspergillus niger': 'aspergillus_niger',
    'Aspergillus terreus': 'aspergillus_terreus',
    'Salmonella spp.': 'salmonella_spp',
    'Shiga toxin-producing E. coli': 'shiga_toxin_producing_e_coli',
    'Aflatoxin B1': 'aflatoxin_b1',
    'Aflatoxin B2': 'aflatoxin_b2',
    'Aflatoxin G1': 'aflatoxin_g1',
    'Aflatoxin G2': 'aflatoxin_g2',
    'Aflatoxins': 'total_aflatoxins',
    'Ochratoxin A': 'ochratoxin_a',
    'Abamectin': 'abamectin',
    'Acephate': 'acephate',
    'Acequinocyl': 'acequinocyl',
    'Acetamiprid': 'acetamiprid',
    'Aldicarb': 'aldicarb',
    'Azoxystrobin': 'azoxystrobin',
    'Bifenazate': 'bifenazate',
    'Bifenthrin': 'bifenthrin',
    'Boscalid': 'boscalid',
    'Captan': 'captan',
    'Carbaryl': 'carbaryl',
    'Carbofuran': 'carbofuran',
    'Chlorantranil-iprole': 'chlorantraniliprole',
    'Chlordane': 'chlordane',
    'Chlorfenapyr': 'chlorfenapyr',
    'Chlorpyrifos': 'chlorpyrifos',
    'Clofentezine': 'clofentezine',
    'Coumaphos': 'coumaphos',
    'Cyfluthrin': 'cyfluthrin',
    'Cypermethrin': 'cypermethrin',
    'Daminozide': 'daminozide',
    'Diazinon': 'diazinon',
    'Dichlorvos': 'dichlorvos',
    'Dimethoate': 'dimethoate',
    'Dimethomorph': 'dimethomorph',
    'Ethoprophos': 'ethoprophos',
    'Etofenprox': 'etofenprox',
    'Etoxazole': 'etoxazole',
    'Fenhexamid': 'fenhexamid',
    'Fenoxycarb': 'fenoxycarb',
    'Fenpyroximate': 'fenpyroximate',
    'Fipronil': 'fipronil',
    'Flonicamid': 'flonicamid',
    'Fludioxonil': 'fludioxonil',
    'Hexythiazox': 'hexythiazox',
    'Imazalil': 'imazalil',
    'Imidacloprid': 'imidacloprid',
    'Kresoxim-methyl': 'kresoxim_methyl',
    'Malathion': 'malathion',
    'Metalaxyl': 'metalaxyl',
    'Methiocarb': 'methiocarb',
    'Methomyl': 'methomyl',
    'Methyl parathion': 'methyl_parathion',
    'Mevinphos': 'mevinphos',
    'Myclobutanil': 'myclobutanil',
    'Naled': 'naled',
    'Oxamyl': 'oxamyl',
    'Paclobutrazol': 'paclobutrazol',
    'Pentachloroni-trobenzene': 'pentachloroni_trobenzene',
    'Permethrin': 'permethrin',
    'Phosmet': 'phosmet',
    'Piperonylbuto-xide': 'piperonyl_butoxide',
    'Prallethrin': 'prallethrin',
    'Propiconazole': 'propiconazole',
    'Propoxur': 'propoxur',
    'Pyrethrins': 'pyrethrins',
    'Pyridaben': 'pyridaben',
    'Spinetoram': 'spinetoram',
    'Spinosad': 'spinosad',
    'Spiromesifen': 'spiromesifen',
    'Spirotetramat': 'spirotetramat',
    'Spiroxamine': 'spiroxamine',
    'Tebuconazole': 'tebuconazole',
    'Thiacloprid': 'thiacloprid',
    'Thiamethoxam': 'thiamethoxam',
    'Trifloxystrob-in': 'trifloxystrobin',
    'Arsenic': 'arsenic',
    'Cadmium': 'cadmium',
    'Lead': 'lead',
    'Mercury': 'mercury',
    'Water Activity': 'water_activity',
    'Imbedded Foreign Material': 'foreign_matter',
    'Insect Fragments, Hair, Mammal Excrement': 'foreign_matter_fragments',
    'Mold': 'mold',
    'Sand, Soil, Cinders, Dirt': 'soil',
}
DECARB = 0.877 # Source: <https://www.conflabs.com/why-0-877/>
DECODINGS = {
    '<LOQ': 0,
    '<LOD': 0,
    'ND': 0,
    'NR': None,
    'N/A': None,
}
KEYS = {
    'Analyte': 'name',
    'Labeled Amount': 'sample_weight',
    'Limit': 'limit',
    'Detected': 'value',
    'LOD': 'lod',
    'LOQ': 'loq',
    'Pass/Fail': 'status',
    'metrc_src_uid': 'source_metrc_uid',
    'matrix': 'product_type',
    'collected_on': 'date_collected',
    'received_on': 'date_received',
    'moisture': 'moisture_content',
    'terpenoids': 'terpenes',
    'foreign_materials': 'foreign_matter',
}
LIMS = {
    'Confident Cannabis': {
        'key': 'Con\x00dent Cannabis',
        'qr_code_index': 2,
    },
    'TagLeaf LIMS': {
        'key': 'lims.tagleaf',
        'qr_code_index': 2,
    },
}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}


class CoAParser:
    """Parse certificates of analysis (CoAs)."""

    def __init__(
            self,
            analyses: Optional[dict] = None,
            analytes: Optional[dict] = None,
            decodings: Optional[dict] = None,
            headers: Optional[dict] = None,
            keys: Optional[dict] = None,
            lims: Optional[Any] = None,
        ) -> None:
        """Initialize CoA parser.
        Args:
            analyses (dict): A dictionary of analyses for standardization.
            analytes (dict): A dictionary of analytes for standardization.
            decodings (dict): A dictionary of decodings for standardization.
            headers (dict): Headers for HTTP requests.
            keys (dict): A dictionary of keys for standardization.
            lims (str or dict): Specific LIMS to parse CoAs.
        """
        # Define analyses.
        self.analyses = analyses
        if analyses is None:
            self.analyses = ANALYSES

        # Define analytes.
        self.analytes = analytes
        if analytes is None:
            self.analytes = ANALYTES

        # Define decodings
        self.decodings = decodings
        if decodings is None:
            self.decodings = DECODINGS

        # Define headers.
        self.headers = headers
        if headers is None:
            self.headers = HEADERS

        # Define keys.
        self.keys = keys
        if keys is None:
            self.keys = KEYS

        # Define LIMS.
        self.lims = lims
        if lims is None:
            self.lims = LIMS

    def decode_pdf_qr_code(self, page, img) -> list:
        """Decode a PDF QR Code from a given image."""
        height = page.height
        bbox = (img['x0'], height - img['y1'], img['x1'], height - img['y0'])
        cropped_page = page.crop(bbox)
        image_obj = cropped_page.to_image(resolution=400)
        return decode(image_obj.original)

    def find_pdf_qr_code(self, doc, image_index=None) -> str:
        """Find the QR code given a CoA PDF or page.
        If no `image_index` is provided, then all images are tried to be
        decoded until a QR code is found. If no QR code is found, then a
        `TypeError` is raised.
        Args:
            doc (PDF or Page): A pdfplumber PDF or Page.
            image_index (int): A known image index for the QR code.
        Returns:
            (str): The QR code URL.
        """
        if isinstance(doc, pdfplumber.pdf.PDF):
            page = doc.pages[0]
        else:
            page = doc
        if image_index:
            img = page.images[image_index]
            image_data = self.decode_pdf_qr_code(page, img)
        else:
            for img in page.images:
                try:
                    img = page.images[image_index]
                    image_data = self.decode_pdf_qr_code(page, img)
                    break
                except:
                    continue
        return image_data[0].data.decode('utf-8')

    def get_pdf_creation_date(self, doc: Any) -> str:
        """Get the creation date of a PDF in ISO format.
        Args:
            doc (PDF): A pdfplumber PDF.
        Returns:
            (str): An ISO formatted date.
        """
        date = doc.metadata['CreationDate'].split('D:')[-1]
        isoformat = f'{date[0:4]}-{date[4:6]}-{date[6:8]}'
        isoformat += f'T{date[8:10]}:{date[10:12]}:{date[12:14]}'
        return isoformat

    def identify_lims(self, doc: Any, lims: Optional[Any] = None) -> str:
        """Identify if a CoA was created by a common LIMS.
        Args:
            doc (PDF or Page): A pdfplumber PDF or Page.
            lims (str or dict): The name of a specific LIMS or a dictionary
                of known LIMS.
        Returns:
            (str): Returns the known LIMS if found, otherwise returns `None`.
        """
        known = None
        text = page.extract_text()
        if lims is None:
            lims = LIMS
        if isinstance(doc, pdfplumber.pdf.PDF):
            page = doc.pages[0]
        else:
            page = doc
        if isinstance(lims, str):
            if lims in text:
                known = lims
        else:
            for key, values in lims.items():
                if values['key'] in text:
                    known = key
                    break
        return known

    def parse(
            self,
            data: Any,
            kind: Optional[str] = 'pdf'
        ) -> list:
        """Parse all CoAs given a directory, a list of files,
        or a list of URLs.
        Args:
            data (str or list): A directory (str) or a list
                of PDF file paths or a list of CoA URLs.
            kind (str): The kind of CoA input, PDF or URL.
        Returns:
            (list): Returns a list of all of the PDFs.
        """
        coas = []
        if isinstance(data, str):
            docs = [
                f for f in os.listdir(DATA_DIR) \
                if os.path.isfile(os.path.join(DATA_DIR, f)) \
                and f.endswith('pdf')
            ]
        else:
            docs = data
        for doc in docs:
            if kind == 'pdf':
                coa_data = self.parse_pdf(doc)
            else:
                coa_data = self.parse_url(doc)
            coas.append(coa_data)
        return coas


    def parse_pdf(self, pdf, lims=None) -> dict:
        """Parse a CoA PDF."""
        if lims is None:
            lims = self.lims
        # FIXME: Find out if the CoA is generated by one of the common LIMS.
        front_page = pdf.pages[0]
        known_lims = parser.identify_lims(front_page)
        sample['lims'] = known_lims
        raise NotImplementedError


    def parse_url(self, url) -> dict:
        """Parse a CoA PDF."""
        # TODO: Implement.
        raise NotImplementedError


    def parse_cc_pdf(self, doc) -> dict:
        """Parse a Confident Cannabis CoA PDF."""
        if isinstance(doc, str):
            pdf = pdfplumber.open(filename)
        else:
            pdf = doc 
        qr_code_index = LIMS['Confident Cannabis']['qr_code_index']
        lab_results_url = parser.find_pdf_qr_code(pdf, qr_code_index)
        data = self.parse_cc_url(lab_results_url)
        sample = {
            'date_tested': self.get_pdf_creation_date(pdf),
            'lab_results_url': lab_results_url,
            'lims': 'Confident Cannabis',
        }
        return {**sample, **data}
    
    
    def parse_cc_url(self, url, max_delay: Optional[float] = 7) -> dict:
        """Parse a Confident Cannabis CoA URL."""
        
        # FIXME: Keep driver and session alive when possible.
        # Load the lab results with Selenium.
        service = Service()
        options = Options()
        options.headless = False
        options.add_argument('--window-size=1920,1200')
        driver = webdriver.Chrome(options=options, service=service)
        driver.get(url)
        try:
            detect = EC.presence_of_element_located((By.CLASS_NAME, 'product-box-cc'))
            WebDriverWait(driver, max_delay).until(detect)
        except TimeoutException:
            print('Failed to load page within %i seconds.' % max_delay)

        # Find the sample image.
        element = driver.find_element(by=By.CLASS_NAME, value='product-box-cc')
        img = element.find_element(by=By.TAG_NAME, value='img')
        image_url = img.get_attribute('src')
        filename = image_url.split('/')[-1]
        sample['images'] = [{'url': image_url, 'filename': filename}]

        # Try to get sample details.
        el = driver.find_element(by=By.CLASS_NAME, value='product-desc')
        block = el.text.split('\n')
        sample['product_name'] = block[0]
        sample['lab_id'] = block[1]
        sample['classification'] = block[2]
        sample['strain_name'], sample['product_type'] = tuple(block[3].split(', '))

        # Get the date tested.
        el = driver.find_element(by=By.CLASS_NAME, value='report')
        span = el.find_element(by=By.TAG_NAME, value='span')
        tooltip = span.get_attribute('uib-tooltip')
        tested_at = tooltip.split(': ')[-1]
        sample['date_tested'] = pd.to_datetime('10/20/21 5:07 PM').isoformat()

        # Get the CoA URL.
        button = el.find_element(by=By.TAG_NAME, value='button')
        href = button.get_attribute('href')
        base = lab_results_url.split('/report')[0]
        coa_url = base.replace('/#!', '') + href
        filename = image_url.split('/')[-1].split('?')[0] + '.pdf'
        sample['coa_urls'] = [{'url': coa_url, 'filename': filename}]

        # Find the analyses and results.
        els = driver.find_elements(by=By.CLASS_NAME, value='ibox')
        for i, el in enumerate(els):
            try:
                title = el.find_element(by=By.TAG_NAME, value='h5').text.lower()
            except:
                continue

            # Try to get cannabinoids data.
            if title == 'cannabinoids':
                totals = el.find_elements(by=By.TAG_NAME, value='compound-box')
                for total in totals:
                    value = total.find_element(by=By.CLASS_NAME, value='value').text
                    units = total.find_element(by=By.CLASS_NAME, value='unit').text
                    name = total.find_element(by=By.CLASS_NAME, value='name').text
                    key = snake_case(name)
                    sample[key] = value
                    sample[f'{key}_units'] = units.replace('%', 'percent')

                # Get the cannabinoids totals.
                columns = ['name', 'value', 'mg_g']
                table = el.find_element(by=By.TAG_NAME, value='table')
                rows = table.find_elements(by=By.TAG_NAME, value='tr')
                for row in rows[1:]:
                    result = {}
                    cells = row.find_elements(by=By.TAG_NAME, value='td')
                    for i, cell in enumerate(cells):
                        key = columns[i]
                        result[key] = cell.get_attribute('textContent').strip()
                    sample['results'].append(result)

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
                        result[key] = cell.get_attribute('textContent').strip()
                    sample['results'].append(result)

                # Try to get predicted aromas.
                container = el.find_element(by=By.CLASS_NAME, value='row')
                aromas = container.text.split('\n')
                sample['predicted_aromas'] = [snake_case(x) for x in aromas]

            # Ty to get screening data.
            if title == 'safety':
                sample['status'] = el.find_element(by=By.CLASS_NAME, value='sample-status').text
                table = el.find_element(by=By.TAG_NAME, value='table')
                rows = table.find_elements(by=By.TAG_NAME, value='tr')
                for row in rows[1:]:
                    cells = row.find_elements(by=By.TAG_NAME, value='td')
                    status = cells[1].get_attribute('textContent').strip()
                    if status == 'Not Tested':
                        continue
                    analysis = snake_case(cells[0].get_attribute('textContent'))
                    sample[f'{analysis}_status'] = status.lower()
                    sample['analyses'].append(analysis)

                    # Click the row. and get all of the results from the modal!
                    columns = ['compound', 'status', 'value', 'limit', 'loq']
                    if row.get_attribute('class') == 'clickable-content':
                        row.click()
                        modal = driver.find_element(by=By.ID, value='safety-modal-table')
                        modal_table = modal.find_element(by=By.TAG_NAME, value='tbody')
                        modal_rows = modal_table.find_elements(by=By.TAG_NAME, value='tr')
                        headers = modal.find_elements(by=By.TAG_NAME, value='th')
                        units = headers[-1].text.split('(')[-1].replace(')', '')
                        for modal_row in modal_rows:
                            result = {'units': units}
                            modal_cells = modal_row.find_elements(by=By.TAG_NAME, value='td')
                            for i, cell in enumerate(cells):
                                key = columns[i]
                                result[key] = cell.get_attribute('textContent').strip()
                            sample['results'].append(result)     

            # Try to get lab data.
            if title == 'order info':
                img = el.find_element(by=By.TAG_NAME, value='img')
                block = el.find_element(by=By.TAG_NAME, value='confident-address').text.split('\n')
                street = block[1]
                address = tuple(block[2].split(', '))
                sample['lab'] = block[0]
                sample['lab_address'] = f'{street} {address}'
                sample['lab_image_url'] = img.get_attribute('src')
                sample['lab_street'] = street
                sample['lab_city'] = address[0]
                sample['lab_state'], sample['lab_zipcode'] = tuple(address.split(' '))
                sample['lab_phone'] = block[-2].split(': ')[-1]
                sample['lab_email'] = block[-1]
                sample['producer'] = el.find_element(by=By.CLASS_NAME, value='public-name').text

        # Return the sample with a freshly minted sample ID.
        sample['sample_id'] = create_sample_id(
            private_key=sample['producer'],
            public_key=sample['product_name'],
            salt=sample['date_tested'],
        )

        # FIXME: Close the Chrome driver once all PDFs have been parsed.
        driver.quit()
        return sample


    def parse_tagleaf_pdf(self, doc) -> dict:
        """Parse a TagLeaf LIMS CoA PDF.
        Args:
            doc (str or PDF): A PDF file path or pdfplumber PDF.
        Returns:
            (dict): The sample data.
        """
        if isinstance(doc, str):
            pdf = pdfplumber.open(filename)
        else:
            pdf = doc 
        qr_code_index = LIMS['TagLeaf LIMS']['qr_code_index']
        lab_results_url = parser.find_pdf_qr_code(pdf, qr_code_index)
        data = self.parse_tagleaf_url(lab_results_url)
        sample = {
            'date_tested': self.get_pdf_creation_date(pdf),
            'lab_results_url': lab_results_url,
            'lims': 'TagLeaf LIMS',
        }
        return {**sample, **data}


    def parse_tagleaf_url(self, url, headers=None, keys=None) -> dict:
        """Parse a TagLeaf LIMS CoA URL."""

        # FIXME: Keep session alive when possible.
        # Get the HTML.
        if keys is None:
            keys = self.keys
        if headers is None:
            headers = self.headers
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the date tested.
        el = soup.find('p', attrs={'class': 'produced-statement'})
        date_tested = pd.to_datetime(el.text.split(': ')[-1]).isoformat()
        sample['date_tested'] = date_tested

        # Get lab details.
        el = soup.find('section', attrs={'class': 'header-container'})
        img = el.find('img')
        pars = el.find_all('p')
        details = [strip_whitespace(x) for x in pars[0].text.split('//')]
        address = details[1]
        sample['lab'] = details[0]
        sample['lab_address'] = address
        sample['lab_image_url'] = img.attrs['src']
        sample['lab_phone'] = details[2].replace('PH: ', '')

        # Get data from headings.
        headings = soup.find_all('p', attrs={'class': 'h5'}, limit=2)
        parts = strip_whitespace(headings[0].text.split('//')[0]).split(' (')
        product_name = parts[0]
        sample['product_name'] = product_name
        sample['product_type'] = parts[1].replace(')', '')
        sample['status'] = strip_whitespace(headings[1].text.split(':')[-1]).lower()

        # Get cannabinoid totals.
        el = soup.find('div', attrs={'class': 'cannabinoid-overview'})
        rows = el.find_all('div', attrs={'class': 'row'})
        for row in rows:
            pars = row.find_all('p')
            key = snake_case(strip_whitespace(pars[1].text))
            value = strip_whitespace(pars[0].text)
            sample[key] = value

        # Get cultivator and distributor details.
        els = soup.find_all('div', attrs={'class': 'license'})
        values = [x.text for x in els[0].find_all('p')]
        producer = values[1]
        sample['producer'] = producer
        sample['license_number'] = values[3]
        sample['license_type'] = values[5]
        values = [x.text for x in els[1].find_all('p')]
        sample['distributor'] = values[1]
        sample['distributor_license_number'] = values[3]
        sample['distributor_license_type'] = values[5]

        # Get the sample image.
        el = soup.find('div', attrs={'class': 'sample-photo'})
        img = el.find('img')
        image_url = img['src']
        filename = image_url.split('/')[-1]
        sample['images'] = [{'url': image_url, 'filename': filename}]

        # Get the sample details
        el = soup.find('div', attrs={'class': 'sample-info'})
        pars = el.find_all('p')
        for par in pars:
            key = snake_case(par.find('span').text)
            key = keys.get(key, key) # Get preferred key.
            value = ''.join([x for x in par.contents if type(x) == NavigableString])
            value = strip_whitespace(value)
            print(key, value)

        # Get the lab ID and metrc ID.
        sample['lab_id'] = sample['sample_id']
        sample['metrc_ids'] = [sample['source_metrc_uid']]

        # Format `date_collected` and `date_received` dates.
        sample['date_collected'] = pd.to_datetime(sample['date_collected']).isoformat()
        sample['date_received'] = pd.to_datetime(sample['date_received']).isoformat()

        # Get the analyses and `{analysis}_status`.
        analyses = []
        el = soup.find('div', attrs={'class': 'tests-overview'})
        blocks = strip_whitespace(el.text)
        blocks = [x for x in blocks.split('    ') if x]
        for i, value in enumerate(blocks):
            if i % 2:
                analysis = analyses[-1]
                if value != '\xa0':
                    sample[f'{analysis}_status'] = value.lower()
            else:
                analysis = snake_case(value)
                analysis = keys.get(analysis, analysis) # Get preferred key.
                analyses.append(analysis)
        sample['analyses'] = analyses

        # Get `{analysis}_method`s.
        els = soup.find_all('div', attrs={'class': 'table-header'})
        for el in els:
            analysis = el.attrs['id'].replace('_test', '')
            analysis = keys.get(analysis, analysis) # Get preferred key.
            heading = el.find('h3')
            title = ''.join([x for x in heading.contents if type(x) == NavigableString])
            sample[f'{analysis}_method'] = strip_whitespace(title)

        # Get the `results`.
        tables = soup.find_all('table')
        for table in tables:

            # Get the columns, noting that `value` is repeated for `mg_g`.
            headers = table.find_all('th')
            columns = [keys[strip_whitespace(x.text)] for x in headers]
            rows = table.find_all('tr')[1:]
            for row in rows:
                mg_g = False
                result = {}
                cells = row.find_all('td')
                for i, cell in enumerate(cells):
                    key = columns[i]
                    if key == 'value' and mg_g:
                        key = 'mg_g'
                    if key == 'value':
                        mg_g = True
                    result[key] = strip_whitespace(cell.text)
                sample['results'].append(result)

        # Return the sample with a freshly minted sample ID.
        sample['sample_id'] = create_sample_id(
            private_key=producer,
            public_key=product_name,
            salt=date_tested,
        )
        return sample


    def save(self, data=None):
        """Save all CoA data."""
        # TODO: Implement.
        raise NotImplementedError

    
    def standardize(self, data=None) -> Any:
        """Standardize (and normalize) given data."""
        # TODO: Implement.
        raise NotImplementedError


#-----------------------------------------------------------------------
# === Standardize and normalize the data ===
# Clean, standardize, and normalize all of the data
# and then return the curated data to the user.
#-----------------------------------------------------------------------

# TODO: Calculate totals if missing:
# - `total_cannabinoids`
# - `total_terpenes`
# - `total_thc`
# - `total_cbd`
# - `total_cbg`
# - `total_thcv`


# TODO: Standardize terpenes:
# Calculate `ocimene` as the sum of: `ocimene`, `beta_ocimene`, `trans_ocimene`.
# Calculate `nerolidol` as the sum of: `trans_nerolidol`, `cis_nerolidol`
# Calculate `terpinenes` as the sum of: `alpha_terpinene``,
#   `gamma_terpinene`, `terpinolene`, `terpinene`


# TODO: Remove and keep units from results `value`.


# TODO: Use `DECODINGS` to normalize `results`.


# TODO: Try to parse a `strain_name` from `product_name`.


# TODO: Augment the latitude and longitude
# Get address parts for TagLeaf LIMS:
# - lab_street
# - lab_city
# - lab_county
# - lab_state
# - lab_zipcode
# - lab_latitude
# - lab_longitude


# Optional: Calculate any meaningful statistics (perhaps `percentile`s?)


# TODO: Archive the lab results if they are public.



#-----------------------------------------------------------------------
# TESTS
#-----------------------------------------------------------------------

# === Test: Get the CoAs ===

if __name__ == '__main__':

    # Initialize the CoA parser.
    parser = CoAParser()

    # # Parse a given directory.
    # data = parser.parse(DATA_DIR)

    # # Get all PDFs in a given directory.
    # dr = os.listdir(DATA_DIR)
    # pdfs = [f for f in dr if os.path.isfile(os.path.join(DATA_DIR, f)) and f.endswith('pdf')]
    # data = parser.parse(pdfs)

    # # Parse a list of CoA URLs.
    # urls = [x['lab_result_url'] for x in data]
    # data = parser.parse(urls)

    # Parse a Confident Cannabis CoA.

    # Parse a TagLeaf LIMS CoA.

    # Future work: Parse a custom CoA.


#-----------------------------------------------------------------------
# === Test: Parse the CoAs ===
# Parse all of the data from the CoAs (did someone call a plumber!).
#-----------------------------------------------------------------------

# if __name__ == '__main__':

# Initialize the CoA parser.
parser = CoAParser()

# Get all PDFs in a given folder.
dr = os.listdir(DATA_DIR)
pdfs = [f for f in dr if os.path.isfile(os.path.join(DATA_DIR, f)) and f.endswith('pdf')]

# Read a PDF.
filename = os.path.join(DATA_DIR, pdfs[4]) # Test file x.
pdf = pdfplumber.open(filename)

# Begin aggregating sample details.
sample = {
    'analyses': [],
    'date_tested': parser.get_pdf_creation_date(pdf),
    'lab_results_url': '',
    'results': [],
}

# Find out if the CoA is generated by one of the common LIMS.
front_page = pdf.pages[0]
known_lims = parser.identify_lims(front_page)
sample['lims'] = known_lims


#-----------------------------------------------------------------------
# --- TagLeaf LIMS Parsing ---
# Get as much data from the web before parsing the PDF! Data points:
# ✓ analyses
# - {analysis}_method
# ✓ {analysis}_status
# - classification
# - coa_urls
# ✓ date_tested
# - date_received
# ✓ distributor
# ✓ distributor_license_number
# ✓ distributor_license_type
# - distributor_latitude (augmented)
# - distributor_longitude (augmented)
# ✓ images
# ✓ lab_results_url
# ✓ producer
# - producer_latitude (augmented)
# - producer_longitude (augmented)
# ✓ product_name
# ✓ product_type
# ✓ results
# - sample_weight
# ✓ status
# ✓ total_cannabinoids
# ✓ total_thc
# ✓ total_cbd
# - total_terpenes (calculated)
# ✓ sample_id (generated)
# - strain_name (predict later)
# - lab_id
# ✓ lab
# ✓ lab_image_url
# ✓ lab_license_number
# ✓ lab_address
# - lab_city
# - lab_county (augmented)
# - lab_state
# - lab_zipcode
# ✓ lab_phone
# - lab_email
# - lab_latitude (augmented)
# - lab_longitude (augmented)
#-----------------------------------------------------------------------
# if known_lims == 'TagLeaf LIMS':

# Find the QR code to public lab results.
qr_code_index = LIMS['TagLeaf LIMS']['qr_code_index']
lab_results_url = parser.find_pdf_qr_code(front_page, image_index=None)
# height = front_page.height
# img = front_page.images[qr_code_index]
# bbox = (img['x0'], height - img['y1'], img['x1'], height - img['y0'])
# cropped_page = front_page.crop(bbox)
# image_obj = cropped_page.to_image(resolution=400)
# image_data = decode(image_obj.original)
# lab_results_url = image_data[0].data.decode('utf-8')

# Get the HTML!
response = requests.get(lab_results_url, headers=HEADERS)
soup = BeautifulSoup(response.content, 'html.parser')

# Get the date tested.
el = soup.find('p', attrs={'class': 'produced-statement'})
date_tested = pd.to_datetime(el.text.split(': ')[-1]).isoformat()
sample['date_tested'] = date_tested

# Get lab details.
el = soup.find('section', attrs={'class': 'header-container'})
img = el.find('img')
pars = el.find_all('p')
details = [strip_whitespace(x) for x in pars[0].text.split('//')]
address = details[1]
sample['lab'] = details[0]
sample['lab_address'] = address
sample['lab_image_url'] = img.attrs['src']
sample['lab_phone'] = details[2].replace('PH: ', '')

# Get data from headings.
headings = soup.find_all('p', attrs={'class': 'h5'}, limit=2)
parts = strip_whitespace(headings[0].text.split('//')[0]).split(' (')
product_name = parts[0]
sample['product_name'] = product_name
sample['product_type'] = parts[1].replace(')', '')
sample['status'] = strip_whitespace(headings[1].text.split(':')[-1]).lower()

# Get cannabinoid totals.
el = soup.find('div', attrs={'class': 'cannabinoid-overview'})
rows = el.find_all('div', attrs={'class': 'row'})
for row in rows:
    pars = row.find_all('p')
    key = snake_case(strip_whitespace(pars[1].text))
    value = strip_whitespace(pars[0].text)
    sample[key] = value

# Get cultivator and distributor details.
els = soup.find_all('div', attrs={'class': 'license'})
values = [x.text for x in els[0].find_all('p')]
producer = values[1]
sample['producer'] = producer
sample['license_number'] = values[3]
sample['license_type'] = values[5]
values = [x.text for x in els[1].find_all('p')]
sample['distributor'] = values[1]
sample['distributor_license_number'] = values[3]
sample['distributor_license_type'] = values[5]

# Get the sample image.
el = soup.find('div', attrs={'class': 'sample-photo'})
img = el.find('img')
image_url = img['src']
filename = image_url.split('/')[-1]
sample['images'] = [{'url': image_url, 'filename': filename}]

# Get the sample details
el = soup.find('div', attrs={'class': 'sample-info'})
pars = el.find_all('p')
for par in pars:
    key = snake_case(par.find('span').text)
    key = KEYS.get(key, key) # Get preferred key.
    value = ''.join([x for x in par.contents if type(x) == NavigableString])
    value = strip_whitespace(value)
    print(key, value)

# Get the lab ID and metrc ID.
sample['lab_id'] = sample['sample_id']
sample['metrc_ids'] = [sample['source_metrc_uid']]

# Format `date_collected` and `date_received` dates.
sample['date_collected'] = pd.to_datetime(sample['date_collected']).isoformat()
sample['date_received'] = pd.to_datetime(sample['date_received']).isoformat()

# Get the analyses and `{analysis}_status`.
analyses = []
el = soup.find('div', attrs={'class': 'tests-overview'})
blocks = strip_whitespace(el.text)
blocks = [x for x in blocks.split('    ') if x]
for i, value in enumerate(blocks):
    if i % 2:
        analysis = analyses[-1]
        if value != '\xa0':
            sample[f'{analysis}_status'] = value.lower()
    else:
        analysis = snake_case(value)
        analysis = KEYS.get(analysis, analysis) # Get preferred key.
        analyses.append(analysis)
sample['analyses'] = analyses

# Get `{analysis}_method`s.
els = soup.find_all('div', attrs={'class': 'table-header'})
for el in els:
    analysis = el.attrs['id'].replace('_test', '')
    analysis = KEYS.get(analysis, analysis) # Get preferred key.
    heading = el.find('h3')
    title = ''.join([x for x in heading.contents if type(x) == NavigableString])
    sample[f'{analysis}_method'] = strip_whitespace(title)

# Get the `results`.
tables = soup.find_all('table')
for table in tables:

    # Get the columns, noting that `value` is repeated for `mg_g`.
    headers = table.find_all('th')
    columns = [KEYS[strip_whitespace(x.text)] for x in headers]
    rows = table.find_all('tr')[1:]
    for row in rows:
        mg_g = False
        result = {}
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            key = columns[i]
            if key == 'value' and mg_g:
                key = 'mg_g'
            if key == 'value':
                mg_g = True
            result[key] = strip_whitespace(cell.text)
        sample['results'].append(result)

# At this stage, create a sample ID.
sample['sample_id'] = create_sample_id(
    private_key=producer,
    public_key=product_name,
    salt=date_tested,
)


#-----------------------------------------------------------------------
# --- Confident Cannabis Parsing ---
# Get as much data from the web before parsing the PDF! Data points:
# ✓ analyses
# - {analysis}_method
# ✓ {analysis}_status
# ✓ classification
# ✓ coa_urls
# ✓ date_tested
# - date_received
# ✓ images
# ✓ lab_results_url
# ✓ producer
# ✓ product_name
# ✓ product_type
# ✓ predicted_aromas
# ✓ results
# - sample_weight
# - total_cannabinoids (calculated)
# ✓ total_thc
# ✓ total_cbd
# - total_terpenes (calculated)
# ✓ sample_id (generated)
# ✓ strain_name
# ✓ lab_id
# ✓ lab
# ✓ lab_image_url
# - lab_license_number
# ✓ lab_address
# ✓ lab_city
# - lab_county (augmented)
# ✓ lab_state
# ✓ lab_zipcode
# ✓ lab_phone
# ✓ lab_email
# - lab_latitude (augmented)
# - lab_longitude (augmented)
#-----------------------------------------------------------------------
# if known_lims == 'Confident Cannabis':

# Get the `lab_results_url` from the QR code on the first page.
qr_code_index = LIMS['Confident Cannabis']['qr_code_index']
lab_results_url = parser.find_pdf_qr_code(front_page, image_index=None)
# height = front_page.height
# img = front_page.images[qr_code_index]
# bbox = (img['x0'], height - img['y1'], img['x1'], height - img['y0'])
# cropped_page = front_page.crop(bbox)
# image_obj = cropped_page.to_image(resolution=400)
# image_data = decode(image_obj.original)
# lab_results_url = image_data[0].data.decode('utf-8')

# Load the lab results with Selenium.
service = Service()
options = Options()
options.headless = False
options.add_argument('--window-size=1920,1200')
driver = webdriver.Chrome(options=options, service=service)
driver.get(lab_results_url)

# Wait for the results to load.
max_delay = 7
try:
    detect = EC.presence_of_element_located((By.CLASS_NAME, 'product-box-cc'))
    WebDriverWait(driver, max_delay).until(detect)
except TimeoutException:
    print('Failed to load page within %i seconds.' % max_delay)

# Find the sample image.
element = driver.find_element(by=By.CLASS_NAME, value='product-box-cc')
img = element.find_element(by=By.TAG_NAME, value='img')
image_url = img.get_attribute('src')
filename = image_url.split('/')[-1]
sample['images'] = [{'url': image_url, 'filename': filename}]

# Try to get sample details.
el = driver.find_element(by=By.CLASS_NAME, value='product-desc')
block = el.text.split('\n')
sample['product_name'] = block[0]
sample['lab_id'] = block[1]
sample['classification'] = block[2]
sample['strain_name'], sample['product_type'] = tuple(block[3].split(', '))

# Get the date tested.
el = driver.find_element(by=By.CLASS_NAME, value='report')
span = el.find_element(by=By.TAG_NAME, value='span')
tooltip = span.get_attribute('uib-tooltip')
tested_at = tooltip.split(': ')[-1]
sample['date_tested'] = pd.to_datetime('10/20/21 5:07 PM').isoformat()

# Get the CoA URL.
button = el.find_element(by=By.TAG_NAME, value='button')
href = button.get_attribute('href')
base = lab_results_url.split('/report')[0]
coa_url = base.replace('/#!', '') + href
filename = image_url.split('/')[-1].split('?')[0] + '.pdf'
sample['coa_urls'] = [{'url': coa_url, 'filename': filename}]

# Find the analyses and results.
els = driver.find_elements(by=By.CLASS_NAME, value='ibox')
for i, el in enumerate(els):
    try:
        title = el.find_element(by=By.TAG_NAME, value='h5').text.lower()
    except:
        continue

    # Try to get cannabinoids data.
    if title == 'cannabinoids':
        totals = el.find_elements(by=By.TAG_NAME, value='compound-box')
        for total in totals:
            value = total.find_element(by=By.CLASS_NAME, value='value').text
            units = total.find_element(by=By.CLASS_NAME, value='unit').text
            name = total.find_element(by=By.CLASS_NAME, value='name').text
            key = snake_case(name)
            sample[key] = value
            sample[f'{key}_units'] = units.replace('%', 'percent')

        # Get the cannabinoids totals.
        columns = ['name', 'value', 'mg_g']
        table = el.find_element(by=By.TAG_NAME, value='table')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        for row in rows[1:]:
            result = {}
            cells = row.find_elements(by=By.TAG_NAME, value='td')
            for i, cell in enumerate(cells):
                key = columns[i]
                result[key] = cell.get_attribute('textContent').strip()
            sample['results'].append(result)

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
                result[key] = cell.get_attribute('textContent').strip()
            sample['results'].append(result)

        # Try to get predicted aromas.
        container = el.find_element(by=By.CLASS_NAME, value='row')
        aromas = container.text.split('\n')
        sample['predicted_aromas'] = [snake_case(x) for x in aromas]

    # Ty to get screening data.
    if title == 'safety':
        sample['status'] = el.find_element(by=By.CLASS_NAME, value='sample-status').text
        table = el.find_element(by=By.TAG_NAME, value='table')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        for row in rows[1:]:
            cells = row.find_elements(by=By.TAG_NAME, value='td')
            status = cells[1].get_attribute('textContent').strip()
            if status == 'Not Tested':
                continue
            analysis = snake_case(cells[0].get_attribute('textContent'))
            sample[f'{analysis}_status'] = status.lower()
            sample['analyses'].append(analysis)

            # Click the row. and get all of the results from the modal!
            columns = ['compound', 'status', 'value', 'limit', 'loq']
            if row.get_attribute('class') == 'clickable-content':
                row.click()
                modal = driver.find_element(by=By.ID, value='safety-modal-table')
                modal_table = modal.find_element(by=By.TAG_NAME, value='tbody')
                modal_rows = modal_table.find_elements(by=By.TAG_NAME, value='tr')
                headers = modal.find_elements(by=By.TAG_NAME, value='th')
                units = headers[-1].text.split('(')[-1].replace(')', '')
                for modal_row in modal_rows:
                    result = {'units': units}
                    modal_cells = modal_row.find_elements(by=By.TAG_NAME, value='td')
                    for i, cell in enumerate(cells):
                        key = columns[i]
                        result[key] = cell.get_attribute('textContent').strip()
                    sample['results'].append(result)     

    # Try to get lab data.
    if title == 'order info':
        img = el.find_element(by=By.TAG_NAME, value='img')
        block = el.find_element(by=By.TAG_NAME, value='confident-address').text.split('\n')
        street = block[1]
        address = tuple(block[2].split(', '))
        sample['lab'] = block[0]
        sample['lab_address'] = f'{street} {address}'
        sample['lab_image_url'] = img.get_attribute('src')
        sample['lab_street'] = street
        sample['lab_city'] = address[0]
        sample['lab_state'], sample['lab_zipcode'] = tuple(address.split(' '))
        sample['lab_phone'] = block[-2].split(': ')[-1]
        sample['lab_email'] = block[-1]
        sample['producer'] = el.find_element(by=By.CLASS_NAME, value='public-name').text

# At this stage, create a sample ID.
sample['sample_id'] = create_sample_id(
    private_key=sample['producer'],
    public_key=sample['product_name'],
    salt=sample['date_tested'],
)

# Close the Chrome driver once all PDFs have been parsed.
driver.quit()


#-----------------------------------------------------------------------
# DEV: Confident Cannabis CoA PDF Parsing
#-----------------------------------------------------------------------

# TODO: If it is a custom CoA without a QR code, then continue to
# parse to the best of our abilities.
# if lab_results_url:
#     sample['lab_results_url'] = lab_results_url
#     public = True
# else:
#     sample['lab_results_url'] = ''

# sample['results'] = []

# Future work: Explore toggling settings to get a better read of the tables.
# {
#     "vertical_strategy": "lines", 
#     "horizontal_strategy": "lines",
#     "explicit_vertical_lines": [],
#     "explicit_horizontal_lines": [],
#     "snap_tolerance": 3,
#     "snap_x_tolerance": 3,
#     "snap_y_tolerance": 3,
#     "join_tolerance": 3,
#     "join_x_tolerance": 3,
#     "join_y_tolerance": 3,
#     "edge_min_length": 3,
#     "min_words_vertical": 3,
#     "min_words_horizontal": 1,
#     "keep_blank_chars": False,
#     "text_tolerance": 3,
#     "text_x_tolerance": 3,
#     "text_y_tolerance": 3,
#     "intersection_tolerance": 3,
#     "intersection_x_tolerance": 3,
#     "intersection_y_tolerance": 3,
# }

# # Try to get cannabinoids data.
# el = els[2]
# totals = el.find_elements(by=By.TAG_NAME, value='compound-box')
# for total in totals:
#     value = total.find_element(by=By.CLASS_NAME, value='value').text
#     units = total.find_element(by=By.CLASS_NAME, value='unit').text
#     name = total.find_element(by=By.CLASS_NAME, value='name').text
#     key = snake_case(name)
#     sample[key] = value
#     sample[f'{key}_units'] = units.replace('%', 'percent')

# # Get the cannabinoids results.
# columns = ['name', 'value', 'mg_g']
# table = el.find_element(by=By.TAG_NAME, value='table')
# rows = table.find_elements(by=By.TAG_NAME, value='tr')
# for row in rows[1:]:
#     result = {}
#     cells = row.find_elements(by=By.TAG_NAME, value='td')
#     for i, cell in enumerate(cells):
#         key = columns[i]
#         result[key] = cell.get_attribute('textContent').strip()
#     sample['results'].append(result)

# # Try to get terpene data.
# el = els[4]
# columns = ['name', 'value', 'mg_g']
# table = el.find_element(by=By.TAG_NAME, value='table')
# rows = table.find_elements(by=By.TAG_NAME, value='tr')
# for row in rows[1:]:
#     result = {}
#     cells = row.find_elements(by=By.TAG_NAME, value='td')
#     for i, cell in enumerate(cells):
#         key = columns[i]
#         result[key] = cell.get_attribute('textContent').strip()
#     sample['results'].append(result)

# # Try to get predicted aromas.
# container = el.find_element(by=By.CLASS_NAME, value='row')
# aromas = container.text.split('\n')
# sample['predicted_aromas'] = [snake_case(x) for x in aromas]

# # Ty to get screening data.
# el = els[3]
# sample['status'] = el.find_element(by=By.CLASS_NAME, value='sample-status').text
# table = el.find_element(by=By.TAG_NAME, value='table')
# rows = table.find_elements(by=By.TAG_NAME, value='tr')
# for row in rows[1:]:
#     cells = row.find_elements(by=By.TAG_NAME, value='td')
#     status = cells[1].get_attribute('textContent').strip()
#     if status == 'Not Tested':
#         continue
#     analysis = snake_case(cells[0].get_attribute('textContent'))
#     sample[f'{analysis}_status'] = status.lower()
#     sample['analyses'].append(analysis)

#     # Click the row. and get all of the results from the modal!
#     columns = ['compound', 'status', 'value', 'limit', 'loq']
#     if row.get_attribute('class') == 'clickable-content':
#         row.click()
#         modal = driver.find_element(by=By.ID, value='safety-modal-table')
#         modal_table = modal.find_element(by=By.TAG_NAME, value='tbody')
#         modal_rows = modal_table.find_elements(by=By.TAG_NAME, value='tr')
#         headers = modal.find_elements(by=By.TAG_NAME, value='th')
#         units = headers[-1].text.split('(')[-1].replace(')', '')
#         for modal_row in modal_rows:
#             result = {'units': units}
#             modal_cells = modal_row.find_elements(by=By.TAG_NAME, value='td')
#             for i, cell in enumerate(cells):
#                 key = columns[i]
#                 result[key] = cell.get_attribute('textContent').strip()
#             sample['results'].append(result)            

# # Try to get lab data.
# el = els[6]
# img = el.find_element(by=By.TAG_NAME, value='img')
# block = el.find_element(by=By.TAG_NAME, value='confident-address').text.split('\n')
# address = tuple(block[2].split(', '))
# sample['lab'] = block[0]
# sample['lab_image_url'] = img.get_attribute('src')
# sample['lab_street'] = block[1]
# sample['lab_city'] = address[0]
# sample['lab_state'], sample['lab_zipcode'] = tuple(address.split(' '))
# sample['lab_phone'] = block[-2].split(': ')[-1]
# sample['lab_email'] = block[-1]
# sample['producer'] = el.find_element(by=By.CLASS_NAME, value='public-name').text

# # FIXME: Get the lab's data.
# # if values[0] == 'Regulatory Compliance Testing'
# lab_info = table_data[0][0].split('/n')

# # Get the sample name and details.
# sample_info = table_data[1][0].split('\n')
# sample_name = sample_info[0]
# for entry in sample_info:
#     if ':' in entry:
#         parts = entry.split(': ')
#         key = snake_case(parts[0])
#         value = parts[1].split(';')[0]
#         value = value.replace(' Produced', '')
#         value = value.replace(' Collected', '')
#         value = value.replace(' Received', '')
#         value = value.replace(' Completed', '')
#         sample[key] = value

# # TODO: Parse the cannabinoids.
# # if 'thca' in text:
# columns = ['name', 'lod', 'loq', 'value', 'mg_g', 'mg_unit', 'mg_serving']
# values = table_data[3][0].split('\n')


# # Optional: Parse the method.
# # table_data[4][0].split('\n')


# # Optional: Parse the notes.
# # if values[0] == 'Con\x00dent Cannabis'
# # table_data[5][0].split('\n')


# # TODO: Parse the terpenes.
# # if 'pinene' in  text:
# columns = ['name', 'lod', 'loq', 'value', 'mg_g']
# table_data[11][0].split('\n')


# # Optional: Parse the aromas.
# # table_data[12][0].split('\n')
# # table_data[13][0].split('\n')


# # TODO: Parse the pesticides.
# # if 'pesticides' in text:
# units = 'ug/g'
# columns = ['name', 'lod', 'loq', 'limit', 'value', 'status',
#            'name', 'lod', 'loq', 'limit', 'value', 'status',]
# values = table_data[26][0].split('\n')


# # TODO: Parse the residual solvents.
# # if 'butane' in text:
# columns = ['name', 'lod', 'loq', 'limit', 'value', 'status']
# values = table_data[31][0].split('\n')


# # TODO: Parse microbes.
# # if 'aerobic' in text or 'salmonella' in text or 'yeast' in text:
# values = table_data[37][0].split('\n')


# # TODO: Parse mycotoxins.
# # if 'ochratoxin' in text:
# values = table_data[39][0].split('\n')


# # TODO: Parse heavy metals
# # if 'arsenic' in text:
# values = table_data[41][0].split('\n')


# Get all of the table data.
# table_data = []
# for page in pdf.pages:
#     table = page.extract_table()
#     table_data += table


#-----------------------------------------------------------------------
# --- Future work: Custom CoA PDF Parsing ---
#-----------------------------------------------------------------------

# Parse the PDF when data can't be scraped from the web.

# # Get all table data.
# table_data = []
# for page in pdf.pages:
#     tables = page.find_tables()
#     for table in tables:
#         data = table.extract()
#         table_data += data

# # Optional: Replace '\x00' with 'fl' or 'fi'?
# # See: <https://github.com/pdfminer/pdfminer.six/issues/35>
# # table_data = [x[0].replace('\x00', 'fl') for x in table_data]

# # Iterate over all of the tables, collecting known tables.
# lab = None
# notes = None
# sample_name = None
# sample = {}
# for table in table_data:

#     # Get the text of the table, keeping lowercase text
#     # to help identify tables.
#     text = table[0]
#     values = text.split('\n')
#     text = text.lower()

#     # Skip empty tables.
#     if not values[0]:
#         continue

#     # Get lab details.
#     if lab and values[0] == 'Regulatory Compliance Testing':
#         continue

#     # Get sample details.
#     if sample_name and values[0] == sample_name:
#         continue

#     # Get notes.
#     if notes and values[0] == 'Con\x00dent Cannabis':
#         continue

#     # Get all of the results!
