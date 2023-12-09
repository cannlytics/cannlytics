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
    'lab': 'Northeast Laboratories',
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

# TODO: Identify all the labs in CT.
for index, row in results.iterrows():
    lab = row['lab']
    if lab not in NE_LABS_CT:
        print(lab)
        continue
    pdf_file = pdf_files[row['id']]
    report = pdfplumber.open(pdf_file)
    front_page_text = report.pages[0].extract_text()
    print(front_page_text)
    break
