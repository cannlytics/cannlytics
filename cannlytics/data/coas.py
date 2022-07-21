"""
CoA Doc | A Certificate of Analysis Parser
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/20/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Certificates of analysis (CoAs) are abundant for cultivators,
    processors, retailers, and consumers too, but the data is often
    locked away. Rich, valuable laboratory data so close, yet so far
    away! Cannlytics puts these vital data points in your hands by
    parsing PDFs and URLs, finding all the data, standardizing the data,
    and cleanly returning the data to you.

    Confident Cannabis data points:

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

    TagLeaf LIMS data points:

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
    
    Custom CoA parsing is still under development.
    If you know of a specific LIMS or lab CoA that you want parsed,
    then please get in contact with the team: <dev@cannlytics.com>
"""
# Standard imports.
from ast import Import
import os
from typing import Any, Optional
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from wand.image import Image as wi

# External imports.
import pandas as pd
import pdfplumber
from pyzbar.pyzbar import decode
from requests import Session
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
from cannlytics.utils import (
    get_directory_files,
    strip_whitespace,
    snake_case,
    unzip_files,
)

# TODO: Incorporate MCR Labs and SC Labs data collection routines.

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
    '3-Carene': 'carene',
    'Δ3-Carene': 'carene',
    'trans-Nerolidol': 'trans_nerolidol',
    'α-Terpinene': 'alpha_terpinene',
    'γ-Terpinene': 'gamma_terpinene',
    'Terpinen-4-ol': 'terpineol',
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
        'algorithm': 'parse_cc_url',
        'key': 'Con\x00dent Cannabis',
        'qr_code_index': 3,
        'url': 'https://orders.confidentcannabis.com',
    },
    'TagLeaf LIMS': {
        'algorithm': 'parse_tagleaf_url',
        'key': 'lims.tagleaf',
        'qr_code_index': 2,
        'url': 'https://lims.tagleaf.com',
    },
    # TODO: Implement an algorithm to parse any custom CoA.
    'custom': {
        'algorithm': '',
        'key': 'custom',
        'qr_code_index': -1,
        'url': 'https://cannlytics.com',
    }
}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}


class CoADoc:
    """Parse data from certificate of analysis (CoA) PDFs or URLs."""

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
        # Setup.
        self.driver = None
        self.options = None
        self.session = None
        self.service = None

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

    def decode_pdf_qr_code(
            self,
            page: Any,
            img: Any,
            resolution: Optional[int] = 300,
        ) -> list:
        """Decode a PDF QR Code from a given image.
        Args:
            page (Page): A pdfplumber Page containing the image.
            img (Image): A pdfplumber Image.
            resolution (int): The resolution to render the QR code,
                `300` by default (optional).
        Returns:
            (list): The QR code data.
        """
        y = page.height
        bbox = (img['x0'], y - img['y1'], img['x1'], y - img['y0'])
        crop = page.crop(bbox)
        obj = crop.to_image(resolution=resolution)
        return decode(obj.original)

    def find_pdf_qr_code_url(
            self,
            pdf: Any,
            image_index: Optional[int] = None,
        ) -> str:
        """Find the QR code given a CoA PDF or page.
        If no `image_index` is provided, then all images are tried to be
        decoded until a QR code is found. If no QR code is found, then a
        `IndexError` is raised.
        Args:
            doc (PDF or Page): A pdfplumber PDF or Page.
            image_index (int): A known image index for the QR code.
        Returns:
            (str): The QR code URL.
        """
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
            page = pdf_file.pages[0]
        elif isinstance(pdf, pdfplumber.pdf.PDF):
            page = pdf.pages[0]
        else:
            page = pdf
        if image_index:
            img = page.images[image_index]
            image_data = self.decode_pdf_qr_code(page, img)
        else:
            for img in page.images:
                try:
                    image_data = self.decode_pdf_qr_code(page, img)
                    if image_data:
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
        if isinstance(doc, str):
            pdf_file = pdfplumber.open(doc)
        else:
            pdf_file = doc
        date = pdf_file.metadata['CreationDate'].split('D:')[-1]
        isoformat = f'{date[0:4]}-{date[4:6]}-{date[6:8]}'
        isoformat += f'T{date[8:10]}:{date[10:12]}:{date[12:14]}'
        return isoformat

    def identify_lims(
            self,
            doc: Any,
            lims: Optional[Any] = None,
        ) -> str:
        """Identify if a CoA was created by a common LIMS.
        Args:
            doc (str, PDF or Page): A URL or a pdfplumber PDF or Page.
            lims (str or dict): The name of a specific LIMS or a
                dictionary of known LIMS.
        Returns:
            (str): Returns LIMS name if found, otherwise returns `None`.
        """
        known = None
        if isinstance(doc, str):
            try:
                pdf_file = pdfplumber.open(doc)
                text = pdf_file.pages[0].extract_text()
            except (FileNotFoundError, OSError):
                text = doc
        else:
            if isinstance(doc, pdfplumber.pdf.PDF):
                page = doc.pages[0]
            else:
                page = doc
            text = page.extract_text()
        if lims is None:
            lims = LIMS
        if isinstance(lims, str):
            if self.lims[lims]['url'] in text:
                known = lims
        else:
            for key, values in lims.items():
                if values['key'] in text or values['url'] in text:
                    known = key
                    break
        return known

    def parse(
            self,
            data: Any,
            headers: Optional[dict] = {},
            kind: Optional[str] = 'url',
            lims: Optional[Any] = None,
            max_delay: Optional[float] = 7,
            persist: Optional[bool] = True,
        ) -> list:
        """Parse all CoAs given a directory, a list of files,
        or a list of URLs.
        Args:
            data (str or list): A directory (str) or a list
                of PDF file paths or a list of CoA URLs.
            headers (dict): Headers for HTTP requests (optional).
            kind (str): The kind of CoA input, PDF or URL, `url`
                by default (optional).
            lims (str or dict): Specific LIMS to parse CoAs (optional).
            max_delay (float): The maximum number of seconds to wait
                for the page to load (optional).
            persist (bool): Whether to persist the driver
                and / or session between CoA parses, the
                default is `True`, with any driver and session
                being closed at the end (optional).
        Returns:
            (list): Returns a list of all of the PDFs.
        """
        coas = []
        if isinstance(data, str):
            if '.zip' in data:
                doc_dir = unzip_files(data)
            else:
                doc_dir = data
            docs = get_directory_files(data)
        else:
            docs = data
        for doc in docs:
            # FIXME: Somehow find unzipped files.
            if '.zip' in doc and kind != 'url':
                doc_dir = unzip_files(doc)
                pdf_files = get_directory_files(doc_dir)
                for pdf_file in pdf_files:
                    coa_data = self.parse_pdf(
                        pdf_file,
                        lims=lims,
                        persist=persist,
                    )
                    coas.append(coa_data)
            elif '.pdf' in doc and kind != 'url':
                coa_data = self.parse_pdf(
                    doc,
                    lims=lims,
                    persist=persist,
                )
            else:
                coa_data = self.parse_url(
                    doc,
                    headers=headers,
                    lims=lims,
                    max_delay=max_delay,
                    persist=persist,
                )
            coas.append(coa_data)
        if persist:
            self.quit()
        return coas

    def parse_pdf(
            self,
            pdf: Any,
            headers: Optional[dict] = {},
            lims: Optional[Any] = None,
            max_delay: Optional[float] = 7,
            persist: Optional[bool] = False,
        ) -> dict:
        """Parse a CoA PDF. Searches the best guess image, then all
        images, for a QR code URL to find results online.
        Args:
            pdf (PDF): A file path to a PDF or a pdfplumber PDF.
            headers (dict): Headers for HTTP requests.
            lims (str or dict): Specific LIMS to parse CoAs.
            max_delay (float): The maximum number of seconds to wait
                for the page to load.
        Returns:
            (dict): The sample data.
        """
        if lims is None:
            lims = self.lims
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
        elif isinstance(pdf, pdfplumber.pdf.PDF):
            pdf_file = pdf
        else:
            with open(wi(file=pdf, resolution=300)) as temp_file:
                temp_file.save('/tmp/coa.pdf')
            pdf_file = pdfplumber.open('/tmp/coa.pdf')
        front_page = pdf_file.pages[0]

        # TODO: Try to read a Metrc ID from the PDF and use the Metrc ID
        # to query the Cannlytics API.
        
        known_lims = self.identify_lims(front_page, lims=lims)
        if known_lims:
            date_tested = self.get_pdf_creation_date(pdf_file)
            try:
                qr_code_index = self.lims[known_lims]['qr_code_index']
                url = self.find_pdf_qr_code_url(pdf_file, qr_code_index)
            except IndexError:
                url = self.find_pdf_qr_code_url(pdf_file)
            # Future work: This is double-checking the `known_lims` twice!
            # but it does re-use the code, which is nice.
            data = self.parse_url(
                url,
                headers=headers,
                lims=known_lims,
                max_delay=max_delay,
                persist=persist,
            )
            sample = {
                'date_tested': date_tested,
                'lab_results_url': url,
                'lims': known_lims,
            }
            return {**sample, **data}
        else:
            # Future work: Parse custom CoAs.
            raise NotImplementedError

    def parse_url(
            self,
            url: str,
            lims: Optional[Any] = None,
            headers: Optional[dict] = {},
            max_delay: Optional[float] = 7,
            persist: Optional[bool] = False,
        ) -> dict:
        """Parse a CoA URL.
        Args:
            url (str): The CoA URL.
            lims (str or dict): Specific LIMS to parse CoAs.
            headers (Any): Optional headers for standardization.
            max_delay (float): The maximum number of seconds to wait
                for the page to load.
            persist (bool): Whether to persist the session.
                The default is `False`. If you do persist
                the driver, then make sure to call `quit`
                when you are finished.
        Returns:
            (dict): The sample data.
        """
        if lims is None:
            lims = self.lims
        known_lims = self.identify_lims(url, lims=lims)
        if known_lims is None:
            # Future work: Parse custom CoAs.
            # E.g. if `known_lims = 'custom'`.`
            raise NotImplementedError
        algorithm_name = LIMS[known_lims]['algorithm']
        algorithm = getattr(self, algorithm_name)
        data = algorithm(
            url,
            headers=headers,
            max_delay=max_delay,
            persist=persist,
        )
        return data

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
            self.options.headless = False
            # FIXME: Uncomment for production!!!
            # self.options.add_argument('--headless')
            # self.options.add_argument('--disable-gpu')
            # self.options.add_argument('--no-sandbox')
        if self.driver is None:
            self.driver = webdriver.Chrome(
                options=self.options,
                service=self.service,
            )
        print('Getting URL:', url)
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

        # Get the lab ID and metrc ID.
        obs['lab_id'] = obs['sample_id']
        obs['metrc_ids'] = [obs['source_metrc_uid']]

        # Format `date_collected` and `date_received` dates.
        obs['date_collected'] = pd.to_datetime(obs['date_collected']).isoformat()
        obs['date_received'] = pd.to_datetime(obs['date_received']).isoformat()

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

    def save(self, data=None):
        """Save all CoA data."""
        # TODO: Implement.
        raise NotImplementedError

    def standardize(self, data=None) -> Any:
        """Standardize (and normalize) given data."""
        # TODO: Implement.
        raise NotImplementedError
    
    def quit(self):
        """Close any driver, end any session, and reset the parameters."""
        try:
            self.driver.quit()
        except:
            pass
        try:
            self.session.close()
        except:
            pass
        self.driver = None
        self.options = None
        self.session = None
        self.service = None


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

    from time import sleep

    # Initialize the CoA parser.
    # Future work: Test the parser with different configurations.
    parser = CoADoc()

    # Specify where your data lives for testing.
    DATA_DIR = '../../.datasets/coas'

    # TODO: Test all functionality:
    # ✓ decode_pdf_qr_code
    # ✓ find_pdf_qr_code_url
    # ✓ get_pdf_creation_date
    # ✓ identify_lims
    # ✓ parse
    # - parse_cc_pdf
    # - parse_cc_url
    # ✓ parse_pdf
    # - parse_tagleaf_pdf
    # - parse_tagleaf_url
    # ✓ parse_url
    # - save (not implemented yet)
    # - standardize (not implemented yet)
    # ✓ quit

    # TODO: Test specific use cases.

    # Test Confident Cannabis CoAs.
    cc_coa_pdf = f'{DATA_DIR}/Classic Jack.pdf'
    cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/4ee67b54-be74-44e4-bb94-4f44d8294062'

    # Test TagLeaf LIMS CoAs.
    tagleaf_coa_pdf = f'{DATA_DIR}/Sunbeam.pdf'
    tagleaf_coa_url = 'https://lims.tagleaf.com/coas/F6LHqs9rk9vsvuILcNuH6je4VWCiFzdhgWlV7kAEanIP24qlHS'
    tagleaf_coa_short_url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'

    # # Test `decode_pdf_qr_code` via `find_pdf_qr_code_url`.
    # qr_code_url = parser.find_pdf_qr_code_url(cc_coa_pdf)
    # assert qr_code_url.startswith('https')
    # qr_code_url = parser.find_pdf_qr_code_url(tagleaf_coa_pdf)
    # assert qr_code_url.startswith('https')

    # # Test `get_pdf_creation_date`.
    # from datetime import datetime
    # creation_date = parser.get_pdf_creation_date(cc_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)
    # creation_date = parser.get_pdf_creation_date(tagleaf_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)

    # Test `identify_lims`.
    # identified_lims = parser.identify_lims(cc_coa_pdf)
    # assert identified_lims == 'Confident Cannabis'
    # identified_lims = parser.identify_lims(tagleaf_coa_pdf)
    # assert identified_lims == 'TagLeaf LIMS'

    # Parse a PDF.
    # data = parser.parse_pdf(cc_coa_pdf)

    # Parse a URL.

    # # FIXME: Parse a Confident Cannabis CoA.
    # data = parser.parse_cc_pdf(cc_coa_pdf)
    # sleep(3)
    # data = parser.parse_cc_url(cc_coa_url)

    # # Parse a TagLeaf LIMS CoA.
    # data = parser.parse_tagleaf_pdf(tagleaf_coa_pdf)
    # sleep(3)
    # data = parser.parse_tagleaf_url(tagleaf_coa_url)
    # sleep(3)
    # data = parser.parse_tagleaf_url(tagleaf_coa_short_url)

    # # Parse a list of CoA URLs.
    # urls = [cc_coa_url, tagleaf_coa_url]
    # data = parser.parse(urls)

    # # Parse a list of CoA PDFs.
    # files = [cc_coa_pdf, tagleaf_coa_pdf]
    # data = parser.parse(files)

    # # Parse all CoAs in a given directory.
    # data = parser.parse(DATA_DIR)

    # TODO: Test parsing all CoAs in a zipped file!

    # Close the parser.
    parser.quit()

    # Future work: Parse a custom CoA.

    print('✓ All tests finished.')
