# Standard imports:
import os

# External importS:
import pandas as pd
import pdfplumber


# Specify where your data lives.
DATA_DIR = 'D:/data/connecticut/lab_results'
PDF_DIR = 'D:/data/connecticut/lab_results/pdfs'
stats_dir = '../data/ct'


# Read in CT results.
datafile = '../data/ct/ct-lab-results-latest.csv'
results = pd.read_csv(datafile)


NE_LABS_CT = {
    'coa_algorithm': 'mcrlabs.py',
    'coa_algorithm_entry_point': 'parse_ne_labs_coa',
    'lims': 'NE Labs',
    'url': 'www.nelabsct.com',
    'lab': 'Northeast Laboratories',
    'lab_website': 'www.nelabsct.com',
    'lab_license_number': 'CTM0000001',
    'lab_image_url': 'https://www.nelabsct.com/images/Northeast-Laboratories.svg',
    'lab_address': '129 Mill Street, Berlin, CT 06037',
    'lab_street': '129 Mill Street',
    'lab_city': 'Berlin',
    'lab_county': 'Hartford',
    'lab_state': 'CT',
    'lab_zipcode': '06037',
    'lab_latitude': '41.626190',
    'lab_longitude': '-72.748250',
    'lab_phone': '860-828-9787',
    'lab_email': '',
}


# TODO: Find the COA for each sample.
missing = 0
pdf_files = {}
for index, row in results.iterrows():
    pdf_file = os.path.join(PDF_DIR, row['id'] + '.pdf')
    if not os.path.exists(pdf_file):
        pdf_file = os.path.join(PDF_DIR, row['lab_id'] + '.pdf')
        if not os.path.exists(pdf_file):
            missing += 1
            continue
    pdf_files[row['id']] = pdf_file

# TODO: Read each PDF and identify the lab.
pdf_file = os.path.join(PDF_DIR, '00000000-0000-0000-1DC3-6B71DEA40F03.pdf')
report = pdfplumber.open(pdf_file)
front_page_text = report.pages[0].extract_text()


from cannlytics.data.coas import CoADoc


# FIXME:
# parser = CoADoc(lims={'NE Labs': NE_LABS_CT})
# parser.identify_lims(front_page_text)


# TODO: Identify all the labs in CT.
for key, value in pdf_files.items():
    report = pdfplumber.open(pdf_file)
    front_page_text = report.pages[0].extract_text()
    if NE_LABS_CT['url'] in front_page_text:
        print('Identified NE LABS COA:', value)
        continue
    else:
        print('Unidentified lab:', value)
