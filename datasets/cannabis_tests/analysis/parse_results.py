# Standard imports:
import os
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import CoADoc

def get_pdf_files(
        pdf_dir,
        min_file_size: Optional[int] = 21_000,
    ) -> list:
    """Get all of the PDFs in the nested directory."""
    pdfs = []
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size >= min_file_size:
                    pdfs.append(file_path)
    return pdfs

def parse_coa_pdfs(
        pdfs: List[str],
        parser: Optional[CoADoc] = None,
        cache: Optional[Bogart] = None,
        reverse: Optional[bool] = False,
        verbose: Optional[bool] = True,
    ) -> list:
    """Parse corresponding COAs from a DataFrame in a PDF directory.
    The `id_key` is used to match the PDF filename to the DataFrame.
    """
    all_results = []
    if parser is None: parser = CoADoc()
    if verbose: print(f'Parsing {len(pdfs)} PDFs...')
    if reverse: pdfs = pdfs[::-1]
    for pdf in pdfs:
        if not os.path.exists(pdf):
            if verbose: print(f'PDF not found: {pdf}')
            continue
        pdf_hash = cache.hash_file(pdf)
        if cache is not None:
            if cache.get(pdf_hash):
                if verbose: print('Cached:', pdf)
                all_results.append(cache.get(pdf_hash))
                continue
        try:
            coa_data = parser.parse_pdf(pdf, verbose=verbose)
            if isinstance(coa_data, list): coa_data = coa_data[0]
            coa_data['coa_pdf'] = os.path.basename(pdf)
            all_results.append(coa_data)
            if cache is not None: cache.set(pdf_hash, coa_data)
            if verbose: print(f'Parsed PDF: {pdf}')
        except Exception as e:
            parser.quit()
            if verbose:
                print(f'Failed to parse PDF: {pdf}')
                print(e)
    return all_results
