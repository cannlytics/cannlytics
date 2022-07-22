"""
CoADoc | A Certificate of Analysis Parser
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/15/2022
Updated: 7/21/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Certificates of analysis (CoAs) are abundant for cultivators,
    processors, retailers, and consumers too, but the data is often
    locked away. Rich, valuable laboratory data so close, yet so far
    away! Cannlytics puts these vital data points in your hands by
    parsing PDFs and URLs, finding all the data, standardizing the data,
    and cleanly returning the data to you.

Note:
    
    Custom CoA parsing is still under development.
    If you know of a specific LIMS or lab CoA that you want parsed,
    then please get in contact with the team: <dev@cannlytics.com>
"""
# Standard imports.
from typing import Any, Optional
from wand.image import Image as wi

# External imports.
import pdfplumber
from pyzbar.pyzbar import decode

# Internal imports.
from cannlytics.utils import (
    get_directory_files,
    unzip_files,
)
from cannlytics.utils.constants import (
    ANALYSES,
    ANALYTES,
    DECARB,
)

# Custom lab and LIMS CoA parsing algorithms.
from cannlytics.data.coas.parse_cc_coa import (
    parse_cc_pdf,
    parse_cc_url,
)
from cannlytics.data.coas.parse_tagleaf_coa import (
    parse_tagleaf_pdf,
    parse_tagleaf_url,
)
from cannlytics.data.coas.parse_veda_coa import parse_veda_pdf

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
    
    # Common LIMS
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

    # Labs
    # TODO: Add SC Labs and MCR Labs.
    'Veda Scientific': {
        'algorithm': 'parse_veda_pdf',
        'key': 'veda scientific',
        'qr_code_index': None,
        'url': ' vedascientific.co',
    },

    # Dream: Implement an algorithm to parse any custom CoA.
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

        # Attach parsing routines.
        self.parse_cc_pdf = parse_cc_pdf
        self.parse_cc_url = parse_cc_url
        self.parse_tagleaf_pdf = parse_tagleaf_pdf
        self.parse_tagleaf_url = parse_tagleaf_url
        self.parse_veda_pdf = parse_veda_pdf
        # TODO: Incorporate MCR Labs and SC Labs `ai` data collection
        # routines by simply using `get_metrc_results`.

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

    def find_metrc_id(self, doc: Any) -> str:
        """Find any Metrc ID that may be in a given CoA PDF."""
        # TODO: Implement!
        if isinstance(doc, str):
            pdf_file = pdfplumber.open(doc)
        else:
            pdf_file = doc
        raise NotImplementedError
    
    def get_metrc_results(self, metrc_id: str) -> dict:
        """Get Metrc lab results that have been archived
        in the Cannlytics library via the Cannlytics API.
        Args:
            metrc_id (str): A Metrc UID.
        Returns:
            (dict): The sample data.
        """
        # TODO: Implement!
        # return None or data!
        raise NotImplementedError

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
            try:
                if self.lims[lims]['url'] in text:
                    known = lims
            except KeyError:
                if lims.lower() in text.lower():
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
        # metrc_id = self.find_metrc_id(pdf_file)
        # if metrc_id:
        #     data = self.get_metrc_results(metrc_id)
        #     if data is not None:
        #         return data
        
        # Identify any known LIMS.
        known_lims = self.identify_lims(front_page, lims=lims)

        # Get the time the CoA was created.
        date_tested = self.get_pdf_creation_date(pdf_file)
        
        if known_lims:
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
            # Dream: Parse custom CoAs.
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

    def save(self, data=None):
        """Save all CoA data, flattening results, images, etc."""
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
# TODO: Standardize and normalize the data.
#-----------------------------------------------------------------------

# TODO: Calculate totals if missing:
# - `total_cannabinoids`
# - `total_terpenes`
# - `total_thc`
# - `total_cbd`
# - `total_cbg`
# - `total_thcv`


# TODO: Standardize terpenes:
# - Calculate `ocimene` as the sum of: `ocimene`, `beta_ocimene`, `trans_ocimene`.
# - Calculate `nerolidol` as the sum of: `trans_nerolidol`, `cis_nerolidol`
# - Calculate `terpinenes` as the sum of: `alpha_terpinene``,
#   `gamma_terpinene`, `terpinolene`, `terpinene`


# TODO: Normalize the `results`:
# - Remove and keep `units` from `value`.
# - Map `DECODINGS` with `value` and `mg_g`.


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
# ✓ decode_pdf_qr_code
# ✓ find_pdf_qr_code_url
# ✓ get_pdf_creation_date
# ✓ identify_lims
# ✓ parse
# ✓ parse_pdf
# ✓ parse_url
# ✓ parse_cc_pdf
# ✓ parse_cc_url
# ✓ parse_tagleaf_pdf
# ✓ parse_tagleaf_url
# - save (not implemented yet)
# - standardize (not implemented yet)
# ✓ quit
#-----------------------------------------------------------------------

if __name__ == '__main__':

    # Initialize the CoA parser.
    # Future work: Test the parser with different configurations.
    parser = CoADoc()

    # Specify where your data lives for testing.
    DATA_DIR = '../../.datasets/coas'

    # Test Confident Cannabis CoAs.
    cc_coa_pdf = f'{DATA_DIR}/Classic Jack.pdf'
    cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/4ee67b54-be74-44e4-bb94-4f44d8294062'

    # Test TagLeaf LIMS CoAs.
    tagleaf_coa_pdf = f'{DATA_DIR}/Sunbeam.pdf'
    tagleaf_coa_url = 'https://lims.tagleaf.com/coas/F6LHqs9rk9vsvuILcNuH6je4VWCiFzdhgWlV7kAEanIP24qlHS'
    tagleaf_coa_short_url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'

    # TODO: Test Veda Scientific CoA.
    veda_coa_pdf = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'

    # Optional: Add GreenLeaf Labs CoA!

    # TODO: Test get MCR Labs results by metrc ID.

    # TODO: Test get SC Labs results by metrc ID.

    # ✓ Test `decode_pdf_qr_code` via `find_pdf_qr_code_url`.
    # qr_code_url = parser.find_pdf_qr_code_url(cc_coa_pdf)
    # assert qr_code_url.startswith('https')
    # qr_code_url = parser.find_pdf_qr_code_url(tagleaf_coa_pdf)
    # assert qr_code_url.startswith('https')

    # ✓ Test `get_pdf_creation_date`.
    # from datetime import datetime
    # creation_date = parser.get_pdf_creation_date(cc_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)
    # creation_date = parser.get_pdf_creation_date(tagleaf_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)

    # ✓ Test `identify_lims`.
    # identified_lims = parser.identify_lims(cc_coa_pdf)
    # assert identified_lims == 'Confident Cannabis'
    # identified_lims = parser.identify_lims(tagleaf_coa_pdf)
    # assert identified_lims == 'TagLeaf LIMS'

    # ✓ Parse a PDF.
    # data = parser.parse_pdf(cc_coa_pdf)

    # ✓ Parse a URL.
    # data = parser.parse_pdf(cc_coa_url)

    # # ✓ Parse a Confident Cannabis CoA.
    # data = parser.parse_cc_pdf(cc_coa_pdf)
    # sleep(3)
    # data = parser.parse_cc_url(cc_coa_url)

    # ✓ Parse a TagLeaf LIMS CoA.
    # data = parser.parse_tagleaf_pdf(tagleaf_coa_pdf)
    # sleep(3)
    # data = parser.parse_tagleaf_url(tagleaf_coa_url)
    # sleep(3)
    # data = parser.parse_tagleaf_url(tagleaf_coa_short_url)

    # ✓ Parse a list of CoA URLs.
    # urls = [cc_coa_url, tagleaf_coa_url]
    # data = parser.parse(urls)

    # ✓ Parse a list of CoA PDFs.
    # files = [cc_coa_pdf, tagleaf_coa_pdf]
    # data = parser.parse(files)

    # ✓ Parse all CoAs in a given directory.
    # data = parser.parse(DATA_DIR)

    # TODO: Test parsing all CoAs in a zipped file!

    # Close the parser.
    parser.quit()

    # Future work: Parse a custom CoA.

    print('✓ All tests finished.')
