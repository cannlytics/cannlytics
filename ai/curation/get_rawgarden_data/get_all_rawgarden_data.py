"""
Get All of Raw Garden Test Result Data
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 8/23/2022
Updated: 9/4/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect all of Raw Garden's published lab results.

Data Sources:

    - Raw Garden Lab Results
    URL: <https://rawgarden.farm/lab-results/>

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep

# External imports.
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Internal imports.
from cannlytics.data.coas import CoADoc
from cannlytics.utils.constants import DEFAULT_HEADERS

# Specify where your data lives.
DATA_DIR = '../../../.datasets'
COA_DATA_DIR = f'{DATA_DIR}/lab_results/raw_garden'
COA_PDF_DIR = f'{COA_DATA_DIR}/pdfs'

# Create directories if they don't already exist.
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(COA_DATA_DIR): os.makedirs(COA_DATA_DIR)
if not os.path.exists(COA_PDF_DIR): os.makedirs(COA_PDF_DIR)


#-----------------------------------------------------------------------
# Get the data!
# URL: <https://rawgarden.farm/lab-results/>
#-----------------------------------------------------------------------

# Get Raw Garden's lab results page.
base = 'https://rawgarden.farm/lab-results/'
response = requests.get(base, headers=DEFAULT_HEADERS)
soup = BeautifulSoup(response.content, 'html.parser')

# Get all of the product categories.
# Match `product_subtype` to the `coa_pdf` filename.
subtypes = []
categories = soup.find_all('div', attrs={'class': 'category-content'})
for category in categories:
    subtype = category.find('h3').text
    for i, link in enumerate(category.findAll('a')):
        try:
            href = link.get('href')
            if href.endswith('.pdf'):
                subtypes.append({
                    'coa_pdf': href.split('/')[-1],
                    'lab_results_url': href,
                    'product_subtype': subtype
                })
        except AttributeError:
            continue

# Save `product_subtype` to `coa_pdf` match.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
subtype_outfile = f'{COA_DATA_DIR}/rawgarden-coa-subtypes-{timestamp}.xlsx'
pd.DataFrame(subtypes).to_excel(subtype_outfile)

# Get all of the PDF URLs.
urls = []
for i, link in enumerate(soup.findAll('a')):
    try:
        href = link.get('href')
        if href.endswith('.pdf'):
            urls.append(href)
    except AttributeError:
        continue

# Download all of the PDFs.
pause = 0.24 # Pause to respect the server serving the PDFs.
total = len(urls)
print('Downloading PDFs, ETA > %.2fs' % (total * pause))
start = datetime.now()
for i, url in enumerate(urls):
    name = url.split('/')[-1]
    outfile = os.path.join(COA_PDF_DIR, name)
    response = requests.get(url, headers=DEFAULT_HEADERS)
    with open(outfile, 'wb') as pdf:
        pdf.write(response.content)
    print('Downloaded %i / %i' % (i +  1, total))
    sleep(pause)
end = datetime.now()

# Count the number of PDFs downloaded.
files = [x for x in os.listdir(COA_PDF_DIR)]
print('Downloaded %i PDFs.' % len(files), 'Time:', end - start)

#-----------------------------------------------------------------------
# Parse and standardize the data with CoADoc
#-----------------------------------------------------------------------

# Parse lab results with CoADoc.
parser = CoADoc()

# Iterate over PDF directory.
all_data = []
unidentified = []
for path, subdirs, files in os.walk(COA_PDF_DIR):
    for name in files:
        file_name = os.path.join(path, name)

        # Only parse PDFs.
        if not name.endswith('.pdf'):
            continue

        # See if we can identify each LIMS.
        try:
            lab = parser.identify_lims(file_name)
        except:
            unidentified.append({'coa_pdf': name, 'lab': None})
            continue

        # Parse CoA PDFs one by one.
        try:
            coa_data  = parser.parse(file_name, lims=lab)
            all_data.extend(coa_data)
            print('Parsed:', name)
        except:
            print('Error:', name)
            unidentified.append({'coa_pdf': name, 'lab': lab})
            pass

# Save any unidentified COAs.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
outfile = f'{COA_DATA_DIR}/rawgarden-unidentified-coas-{timestamp}.xlsx'
pd.DataFrame(unidentified).to_excel(outfile)

# Save the parsed CoA data.
timestamp = datetime.now().isoformat()[:19].replace(':', '-')
coa_data_outfile = f'{COA_DATA_DIR}/rawgarden-coa-data-{timestamp}.xlsx'
coa_data = parser.save(all_data, coa_data_outfile)

# DEV:
coa_data_outfile = r'../../../.datasets\tests\rawgarden-coa-data-2022-08-31T14-05-09.xlsx'
subtype_outfile = r'../../../.datasets\tests\rawgarden-coa-subtypes-2022-09-03T12-40-38.xlsx'

from openpyxl import load_workbook

# FIXME: Add `product_subtype` data to each worksheet after `product_type`.
sheets = ['Details'] # 'Values', 'Results'
subtype_data = pd.read_excel(subtype_outfile, index_col=0)
for sheet in sheets:
    coa_values = pd.read_excel(coa_data_outfile, sheet_name=sheet)
    # loc = coa_values.columns.get_loc('product_type')
    # coa_values.insert(loc, 'product_subtype', )
    
    # TODO: Merge on `coa_pdf`. How to add to 'Values' and 'Results'?

    # TODO: Move `product_subtype` to after `product_type`.

    # FIXME: Save the worksheet. Test that the below works and doesn't overwrite!
    # with pd.ExcelWriter(coa_data_outfile, engine='openpyxl', mode='a') as writer:
    #     coa_values.to_excel(writer, sheet_name=sheet, index=0)
    excelBook = load_workbook(coa_data_outfile)
    with pd.ExcelWriter(coa_data_outfile, engine='xlsxwriter') as writer:
        writer.book = excelBook
        writer.sheets = dict((ws.title, ws) for ws in excelBook.worksheets)
        coa_values.to_excel(writer, sheet_name=sheet, index=0)
        writer.save()
