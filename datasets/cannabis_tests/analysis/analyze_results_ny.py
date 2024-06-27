"""
Analyze Results | New York
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/26/2024
Updated: 6/26/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
import base64
from datetime import datetime
import json
import os
import shutil
import tempfile
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import get_coa_files, parse_coa_pdfs
from cannlytics.firebase import initialize_firebase
from cannlytics.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import pandas as pd
import pdfplumber


#-----------------------------------------------------------------------
# Find all COA PDFs.
#-----------------------------------------------------------------------

# Constants:
pdf_dir = 'D://data/new-york'

# Get all of the PDFs.
pdfs = get_coa_files(pdf_dir)
print('Found %i PDFs.' % len(pdfs))

# Sort the PDFs by modified date
pdfs.sort(key=os.path.getmtime)


#-----------------------------------------------------------------------
# TODO: Parse the COAs!
#-----------------------------------------------------------------------

def encode_image(image_path):
        """Encode an image as a base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


# === DEV: Identify all labs ===

# Extract text from all PDFs.
extracted_data = []
for pdf_file in pdfs:
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text() + '\n'
            extracted_data.append({'file': pdf_file, 'text': full_text})
    except:
        pass

# Find all COAs from a specific lab.
coas = {}
unidentified_coas = []
labs = [
    'Phyto-farma Labs',
    'Phyto-Farma Labs',
    'Kaycha Labs',
    'Keystone State Testing',
    'Green Analytics',
]
for data in extracted_data:
    for lab in labs:
        if lab in data['text']:
            lab_coas = coas.get(lab, [])
            lab_coas.append(data['file'])
            coas[lab] = lab_coas
            break
    else:
        unidentified_coas.append(data['file'])
print('Number of unidentified COAs:', len(unidentified_coas))

# DEV: Look at the first page of a PDF.
if unidentified_coas:
    pdf = pdfplumber.open(unidentified_coas[0])
    page = pdf.pages[0]
    im = page.to_image(resolution=300)
    im.debug_tablefinder()

# Count COAs per lab.
for lab, lab_coas in coas.items():
    print(lab, len(lab_coas))


#-----------------------------------------------------------------------
# Parse Kaycha Labs COAs.
#-----------------------------------------------------------------------

from cannlytics.data.coas import CoADoc
from cannlytics.data.coas.algorithms.kaycha import parse_kaycha_coa

all_data = []
parser = CoADoc()
lab_coas = coas['Kaycha Labs']
for doc in lab_coas:
    try:
        coa_data = parse_kaycha_coa(parser, doc)
        all_data.append(coa_data)
        print('Parsed:', doc)
    except:
        print('Error:', doc)


#-----------------------------------------------------------------------
# TODO: Parse Phyto-farma Labs COAs.
#-----------------------------------------------------------------------

# New version: Phyto-Farma Labs


# Old version: Phyto-farma Labs



#-----------------------------------------------------------------------
# TODO: Parse Keystone State Testing COAs.
#-----------------------------------------------------------------------

from .keystone import parse_keystone_coa

lab_coas = coas['Keystone State Testing']
for doc in lab_coas:
    try:
        coa_data = parse_keystone_coa(parser, doc)
        all_data.append(coa_data)
        print('Parsed:', doc)
    except:
        print('Error:', doc)



#-----------------------------------------------------------------------
# TODO: Parse Green Analytics COAs.
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# TODO: Analyze results.
#-----------------------------------------------------------------------

results = pd.DataFrame(all_data)

# TODO: Look at values of any terpenes not yet observed.
