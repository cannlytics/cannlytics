"""
Tesseract Development
"""

import pdfplumber

# Specify where your test CoA lives.
DATA_DIR = '../../../.datasets/coas'
coa_pdf = f'{DATA_DIR}/Veda Scientific Sample COA.pdf'

# Read the PDF.
if isinstance(coa_pdf, str):
    report = pdfplumber.open(coa_pdf)
else:
    report = coa_pdf
front_page = report.pages[0]
