"""
CoADoc | A Certificate of Analysis (CoA) Parser
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/15/2022
Updated: 8/2/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Certificates of analysis (CoAs) are abundant for cultivators,
    processors, retailers, and consumers too, but the data is often
    locked away. Rich, valuable laboratory data so close, yet so far
    away! CoADoc puts these vital data points in your hands by
    parsing PDFs and URLs, finding all the data, standardizing the data,
    and cleanly returning the data to you.

Note:
    
    Custom CoA parsing is still under development. If you want a
    specific lab or LIMS CoA parsed, then please contact the team!
    Email: <dev@cannlytics.com>

Supported Labs:

    - Anresco Laboratories
    - Cannalysis
    ✓ Green Leaf Lab
    ✓ MCR Labs
    ✓ SC Labs
    - Sonoma Lab Works
    - Veda Scientific

Supported LIMS:

    ✓ Confident Cannabis
        - CB Labs (FIXME)
    ✓ TagLeaf LIMS
        - BelCosta Labs (FIXME)
        - California AG Labs (FIXME)

Future work:

    The roadmap for CoADoc is to continue adding labs and LIMS CoA
    parsing routines until a general CoA parsing routine can be created.
    In order to implement a good custom CoA parsing algorithm, we will
    need to handle:

        - PDF properties, such as the fonts used, glyph sizes, etc.
        - Handle non-font parameters and page scaling.
        - Detect words, lines, columns, white-space, etc.

"""
# Standard imports.
import base64
import importlib
from io import BytesIO
from typing import Any, Optional
from wand.image import Image as wi

# External imports.
import pdfplumber
from pyzbar.pyzbar import decode

# Internal imports.
from cannlytics.utils import (
    get_directory_files,
    sandwich_list,
    unzip_files,
)
from cannlytics.utils.constants import (
    ANALYSES,
    ANALYTES,
    DECARB,
    DEFAULT_HEADERS,
)

# Lab and LIMS CoA parsing algorithms.
from cannlytics.data.coas.confidentcannabis import CONFIDENT_CANNABIS
from cannlytics.data.coas.greenleaflab import GREEN_LEAF_LAB
from cannlytics.data.coas.mcrlabs import MCR_LABS
from cannlytics.data.coas.sclabs import SC_LABS
from cannlytics.data.coas.tagleaf import TAGLEAF
from cannlytics.data.coas.veda import VEDA_SCIENTIFIC


# Labs and LIMS that CoADoc can parse.
LIMS = {
    'Confident Cannabis': CONFIDENT_CANNABIS,
    'Green Leaf Lab': GREEN_LEAF_LAB,
    'MCR Labs': MCR_LABS,
    'SC Labs': SC_LABS,
    'TagLeaf LIMS': TAGLEAF,
    'Veda Scientific': VEDA_SCIENTIFIC,
}

# General decodings to use for normalization of results.
DECODINGS = {
    '<LOQ': 0,
    '<LOD': 0,
    # '≥ LOD': 0,
    'ND': 0,
    'NR': None,
    'N/A': None,
    'na': None,
}

# General keys to use for standardization of fields.
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
            init_all: Optional[bool] = True,
        ) -> None:
        """Initialize CoA parser.
        Args:
            analyses (dict): A dictionary of analyses for standardization.
            analytes (dict): A dictionary of analytes for standardization.
            decodings (dict): A dictionary of decodings for standardization.
            headers (dict): Headers for HTTP requests.
            keys (dict): A dictionary of keys for standardization.
            lims (str or dict): Specific LIMS to parse CoAs.
            init_all (bool): Initialize all of the parsing routines.
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
            self.headers = DEFAULT_HEADERS

        # Define keys.
        self.keys = keys
        if keys is None:
            self.keys = KEYS

        # Define LIMS.
        self.lims = lims
        if lims is None:
            self.lims = LIMS
        
        # Assign all of the parsing routines.
        if init_all:
            for values in self.lims.values():
                name = values['coa_algorithm'].replace('.py', '')
                self[name] = importlib.import_module(f'cannlytics.data.coas.{name}')

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
            page_index: Optional[int] = 0,
        ) -> str:
        """Find the QR code given a CoA PDF or page.
        If no `image_index` is provided, then all images are tried to be
        decoded until a QR code is found. If no QR code is found, then a
        `IndexError` is raised.
        Args:
            doc (PDF or Page): A pdfplumber PDF or Page.
            image_index (int): A known image index for the QR code.
            page_index (int): The page to search, 0 by default (optional).
        Returns:
            (str): The QR code URL.
        """
        image_data = None
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
            page = pdf_file.pages[page_index]
        elif isinstance(pdf, pdfplumber.pdf.PDF):
            page = pdf.pages[page_index]
        else:
            page = pdf
        if image_index:
            img = page.images[image_index]
            decoded_image = self.decode_pdf_qr_code(page, img)
            image_data = decoded_image[0].data.decode('utf-8')
        else:
            # Cycle from start to end to the middle.
            image_range = sandwich_list(page.images)
            for img in image_range:
                # img = page.images[index]
                try:
                    decoded_image = self.decode_pdf_qr_code(page, img)
                    image_data = decoded_image[0].data.decode('utf-8')
                    if image_data:
                        break
                except:
                    continue
        return image_data

    def find_metrc_id(self, pdf: Any) -> str:
        """Find any Metrc ID that may be in a given CoA PDF."""
        # TODO: Implement!
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
        else:
            pdf_file = pdf
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
    
    def get_page_rows(self, page: Any, **kwargs) -> list:
        """Get the rows a given page.
        Args:
            page (Page): A pdfplumber page containing rows to extract.
        Returns:
            (list): A list of text.
        """
        txt = page.extract_text(**kwargs)
        txt = txt.replace('\xa0\xa0', '\n').replace('\xa0', ',')
        return txt.split('\n')

    def get_pdf_creation_date(self, pdf: Any) -> str:
        """Get the creation date of a PDF in ISO format.
        Args:
            pdf (PDF): A pdfplumber PDF.
        Returns:
            (str): An ISO formatted date.
        """
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
        else:
            pdf_file = pdf
        try:
            date = pdf_file.metadata['CreationDate'].split('D:')[-1]
        except KeyError:
            return None
        isoformat = f'{date[0:4]}-{date[4:6]}-{date[6:8]}'
        isoformat += f'T{date[8:10]}:{date[10:12]}:{date[12:14]}'
        return isoformat
    
    def get_pdf_image_data(
            self,
            page: Any,
            image_index: Optional[int] = 0, 
            resolution: Optional[int] = 300,
        ) -> str:
        """Get the image data for a given PDF page image.
        Args:
            page (Page): A pdfplumber Page.
            image_index (int): The index of the image.
            resolution (int): The resolution for the image.
        Returns:
            (str): The image data.
        """
        y = page.height
        img = page.images[image_index]
        bbox = (img['x0'], y - img['y1'], img['x1'], y - img['y0'])
        crop = page.crop(bbox)
        obj = crop.to_image(resolution=resolution)
        buffered = BytesIO()
        obj.save(buffered, format='JPEG')
        img_str = base64.b64encode(buffered.getvalue())
        return img_str.decode('utf-8')

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
        # Search all of the text of the LIMS name or URL.
        # TODO: See if `.search(pattern, regex=True, case=True, **kwargs)` is faster.
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
                url = values.get('url')
                if url and url in text:
                    known = key
                    break
                lab = values.get('lims')
                if lab and lab in text:
                    known = key
                    break

        # Try to get a QR code to identify the LIMS.
        if not known:
            qr_code_url = self.find_pdf_qr_code_url(doc)
            if qr_code_url:
                for key, values in lims.items():
                    url = values.get('url')
                    if url and url in qr_code_url:
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
        coas, docs = [], []

        # Parse a URL, PDF, .zip, or directory.
        if isinstance(data, str):

            # Parse a URL.
            if 'https' in data:
                coa_data = self.parse_url(
                    data,
                    headers=headers,
                    lims=lims,
                    max_delay=max_delay,
                    persist=persist,
                )
                coas.append(coa_data)

            # Parse a PDF.
            elif '.pdf' in data:
                coa_data = self.parse_pdf(
                    data,
                    headers=headers,
                    lims=lims,
                    max_delay=max_delay,
                    persist=persist,
                )
                coas.append(coa_data)

            # Parse a ZIP.
            elif '.zip' in data:
                doc_dir = unzip_files(data)
                docs = get_directory_files(doc_dir)

            # Parse a directory.
            else:
                docs = get_directory_files(data)
        
        # Handle a list of URLs, PDFs, and/or ZIPs.
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
                        max_delay=max_delay,
                        persist=persist,
                    )
                    coas.append(coa_data)
            elif '.pdf' in doc and kind != 'url':
                coa_data = self.parse_pdf(
                    doc,
                    lims=lims,
                    max_delay=max_delay,
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

        # Read the PDF.
        if isinstance(pdf, str):
            pdf_file = pdfplumber.open(pdf)
        elif isinstance(pdf, pdfplumber.pdf.PDF):
            pdf_file = pdf
        else:
            with open(wi(file=pdf, resolution=300)) as temp_file:
                temp_file.save('/tmp/coa.pdf')
            pdf_file = pdfplumber.open('/tmp/coa.pdf')
        
        # TODO: Try to read a Metrc ID from the PDF and use the Metrc ID
        # to query the Cannlytics API.
        # metrc_id = self.find_metrc_id(pdf_file)
        # if metrc_id:
        #     data = self.get_metrc_results(metrc_id)
        #     if data is not None:
        #         return data

        # Identify any known LIMS.
        known_lims = self.identify_lims(pdf_file, lims=lims)

        # Get the time the CoA was created, if known.
        date_tested = self.get_pdf_creation_date(pdf_file)

        # Attempt to use an URL from any QR code on the PDF.
        url = None
        try:
            qr_code_index = self.lims[known_lims].get('qr_code_index')
            url = self.find_pdf_qr_code_url(pdf_file, qr_code_index)
            if url is None and qr_code_index is not None:
                url = self.find_pdf_qr_code_url(pdf_file)
        except IndexError:
            url = self.find_pdf_qr_code_url(pdf_file)

        # Get the LIMS parsing routine.
        algorithm_name = LIMS[known_lims]['coa_algorithm_entry_point']
        algorithm = getattr(self, algorithm_name)
        
        # Use the URL if found, then try the PDF if the URL fails or is missing.
        if url:
            try:
                data = self.parse_url(
                    url,
                    headers=headers,
                    lims=known_lims,
                    max_delay=max_delay,
                    persist=persist,
                )
            except:
                data = algorithm(
                    self,
                    pdf_file,
                    headers=headers,
                    max_delay=max_delay,
                    persist=persist,
                )
        else:
            data = algorithm(
                self,
                pdf_file,
                headers=headers,
                max_delay=max_delay,
                persist=persist,
            )

        sample = {
            'date_tested': date_tested,
            'lab_results_url': url,
            'lims': known_lims,
        }
        return {**sample, **data}

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
        
        # Identify the LIMS.
        known_lims = self.identify_lims(url, lims=lims)
        
        # TODO: Parse custom CoAs.
        if known_lims is None:
            raise NotImplementedError
        
        # Get the LIMS parsing routine.
        algorithm_name = LIMS[known_lims]['coa_algorithm_entry_point']
        algorithm = getattr(self, algorithm_name)
        data = algorithm(
            self,
            url,
            headers=headers,
            max_delay=max_delay,
            persist=persist,
        )
        return data

    def save(self, data=None):
        """Save all CoA data, flattening results, images, etc."""

        # TODO: Archive the lab results if they are public.

        raise NotImplementedError

    def standardize(self, data=None) -> Any:
        """Standardize (and normalize) given data."""

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

        # TODO: Standardize `units`, `product_type`, etc.

        # TODO: Try to parse a `strain_name` from `product_name`.

        # TODO: Augment any missing latitude and longitude or address field.
        # E.g. Get missing address fields for TagLeaf LIMS:
        # - lab_street
        # - lab_city
        # - lab_county
        # - lab_state
        # - lab_zipcode
        # - lab_latitude
        # - lab_longitude

        # Optional: Calculate any meaningful statistics (perhaps `percentiles`s?)

        # Optional: Drop helper fields: 
        # - coa_qr_code_index
        # - coa_image_index

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


if __name__ == '__main__':

    # === Tests ===

    # Initialize the CoA parser.
    # Future work: Test the parser with different configurations.
    parser = CoADoc()

    # Specify where your data lives for testing.
    DATA_DIR = '../../../.datasets/coas'
    cc_coa_pdf = f'{DATA_DIR}/Classic Jack.pdf'
    cc_coa_url = 'https://share.confidentcannabis.com/samples/public/share/4ee67b54-be74-44e4-bb94-4f44d8294062'
    tagleaf_coa_pdf = f'{DATA_DIR}/Sunbeam.pdf'
    tagleaf_coa_url = 'https://lims.tagleaf.com/coas/F6LHqs9rk9vsvuILcNuH6je4VWCiFzdhgWlV7kAEanIP24qlHS'
    tagleaf_coa_short_url = 'https://lims.tagleaf.com/coa_/F6LHqs9rk9'

    # [✓] TEST: `decode_pdf_qr_code` via `find_pdf_qr_code_url`.
    # qr_code_url = parser.find_pdf_qr_code_url(cc_coa_pdf)
    # assert qr_code_url.startswith('https')
    # qr_code_url = parser.find_pdf_qr_code_url(tagleaf_coa_pdf)
    # assert qr_code_url.startswith('https')

    # [✓] TEST: `get_pdf_creation_date`.
    # from datetime import datetime
    # creation_date = parser.get_pdf_creation_date(cc_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)
    # creation_date = parser.get_pdf_creation_date(tagleaf_coa_pdf)
    # assert isinstance(pd.to_datetime(creation_date), datetime)

    # [✓] TEST: `identify_lims`.
    # identified_lims = parser.identify_lims(cc_coa_pdf)
    # assert identified_lims == 'Confident Cannabis'
    # identified_lims = parser.identify_lims(tagleaf_coa_pdf)
    # assert identified_lims == 'TagLeaf LIMS'

    # [✓] TEST: Parse a PDF.
    # data = parser.parse_pdf(cc_coa_pdf)

    # [✓] TEST: Parse a URL.
    # data = parser.parse_url(cc_coa_url)

    # [✓] TEST: Parse a Confident Cannabis CoA.
    # data = parser.parse(cc_coa_pdf)
    # sleep(3)
    # data = parser.parse(cc_coa_url)

    # [✓] TEST: Parse a TagLeaf LIMS CoA.
    # data = parser.parse(tagleaf_coa_pdf)
    # sleep(3)
    # data = parser.parse(tagleaf_coa_url)
    # sleep(3)
    # data = parser.parse(tagleaf_coa_short_url)

    # [✓] TEST: Parse a list of CoA URLs.
    # urls = [cc_coa_url, tagleaf_coa_url]
    # data = parser.parse(urls)

    # [✓] TEST: Parse a list of CoA PDFs.
    # files = [cc_coa_pdf, tagleaf_coa_pdf]
    # data = parser.parse(files)

    # [✓] TEST: Parse all CoAs in a given directory.
    # data = parser.parse(DATA_DIR)

    # [ ] TEST: Parse all CoAs in a zipped folder!
    zip_folder = '../../../.datasets/tests/coas.zip'
    # data = parser.parse(zip_folder)
    # assert data is not None

    # [✓] TEST: Green Leaf Lab CoA parsing algorithm.
    # green_leaf_lab_coa_pdf = f'{DATA_DIR}/Raspberry Parfait.pdf'
    # data = parser.parse(green_leaf_lab_coa_pdf)
    # assert data is not None

    # [ ] TEST: Parse a Veda Scientific CoA.
    veda_coa_pdf = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'
    # lab = parser.identify_lims(veda_coa_pdf)
    # assert lab == 'Veda Scientific'
    # data = parser.parse(veda_coa_pdf)
    # assert data is not None

    # [ ] TEST: Parse a MCR Labs URL.
    mcr_labs_coa_url = 'https://reports.mcrlabs.com/reports/critical-kush_24'
    lab = parser.identify_lims(mcr_labs_coa_url)
    assert lab == 'MCR Labs'
    data = parser.parse(mcr_labs_coa_url)
    assert data is not None

    # [ ] TEST: Parse a SC Labs sample URL.
    # sc_labs_coa_url = 'https://client.sclabs.com/sample/796684/'
    # lab = parser.identify_lims(sc_labs_coa_url)
    # assert lab == 'SC Labs'
    # data = parser.parse(sc_labs_coa_url)
    # assert data is not None

    # [ ] TEST: Parse a SC Labs CoA.
    sc_labs_coa_pdf = f'{DATA_DIR}/SC Labs Test CoA.pdf'
    # lab = parser.identify_lims(sc_labs_coa_pdf)
    # assert lab == 'SC Labs'
    # data = parser.parse(sc_labs_coa_pdf)
    # assert data is not None

    # [ ] TEST: Find results by known metrc IDs.
    metrc_ids = [
        '1A4060300002A3B000000053', # Green Leaf Lab
        '1A4060300017A85000001289', # Green Leaf Lab
        '1A4060300002459000017049', # SC Labs
    ]
    # sample = parser.parse(metrc_ids[0])
    # assert sample is not None
    # data = parser.parse(metrc_ids)
    # assert data is not None

    # [✓] TEST: Parse a custom CoA (accept an error for now).
    try:
        parser.parse('https://cannlytics.page.link/partial-equilibrium-notes')
    except NotImplementedError:
        pass
   
    # [✓] TEST: Close the parser.
    parser.quit()

    print('All CoADoc tests finished.')
