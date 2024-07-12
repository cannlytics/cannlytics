"""
COA Parsing Tools
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/14/2024
Updated: 6/14/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import ast
import json
import os
from typing import Any, List, Optional

# External imports:
from ..cache import Bogart
from .coas import CoADoc

def get_coa_files(
        pdf_dir,
        min_file_size: Optional[int] = 21_000,
        ext: Optional[Any] = '.pdf',
    ) -> list:
    """Get all of the COAs in the nested directory."""
    filenames = []
    if isinstance(ext, str): ext = [ext]
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension in ext:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size >= min_file_size:
                    filenames.append(file_path)
    return filenames

def parse_coa_pdfs(
        pdfs: List[str],
        parser: Optional[CoADoc] = None,
        cache: Optional[Bogart] = None,
        reverse: Optional[bool] = False,
        verbose: Optional[bool] = True,
        key: Optional[str] = 'coa_pdf',
    ) -> list:
    """Parse corresponding COAs from a DataFrame in a PDF directory."""
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
            coa_data[key] = os.path.basename(pdf)
            all_results.append(coa_data)
            if cache is not None: cache.set(pdf_hash, coa_data)
            if verbose: print(f'Parsed PDF: {pdf}')
        except Exception as e:
            parser.quit()
            if verbose:
                print(f'Failed to parse PDF: {pdf}')
                print(e)
                cache.set(pdf_hash, {'coa_pdf': os.path.basename(pdf), 'error': str(e)})
    return all_results


def find_unique_analytes(df, analyses = [], key='key'):
    """Find unique analytes in a list of results."""
    analytes = set()
    for _, row in df.iterrows():
        results = row['results']
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except:
                try:
                    results = ast.literal_eval(results)
                except:
                    continue
        elif isinstance(results, float):
            continue
        for result in results:
            if analyses:
                if result.get('analysis') in analyses:
                    analytes.add(result[key])
            else:
                analytes.add(result[key])
    return analytes
