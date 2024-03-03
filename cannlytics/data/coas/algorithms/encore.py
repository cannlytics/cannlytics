"""
Parse Encore Labs COAs
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/2/2024
Updated: 3/2/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Data points:

    - analyses
    - methods
    - results
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_terpenes
    ✓ batch_number
    ✓ metrc_batch_label
    ✓ metrc_sample_label
    ✓ lab_id
    ✓ strain_name
    ✓ strain_type
    ✓ product_name
    ✓ product_category
    ✓ product_type
    x date_produced
    ✓ date_collected
    ✓ date_received
    ✓ date_tested
    ✓ sample_size
    ✓ batch_size
    ✓ distributor
    ✓ distributor_license_number
    ✓ distributor_address
    ✓ distributor_street
    ✓ distributor_city
    ✓ distributor_state
    ✓ distributor_zipcode
    ✓ producer
    ✓ producer_license_number
    ✓ producer_address
    ✓ producer_street
    ✓ producer_city
    ✓ producer_state
    ✓ producer_zipcode
"""
# Standard imports:
from collections import OrderedDict

# External imports:
import pdfplumber

def list_between_values(lst, start_value, end_value):
    """
    Returns a sublist of lst that starts with the element after start_value
    and ends with the element before end_value.
    """
    start_index = lst.index(start_value) + 1 if start_value in lst else None
    end_index = lst.index(end_value) if end_value in lst else None
    if start_index is not None and end_index is not None and start_index < end_index:
        return lst[start_index:end_index]
    else:
        return []


# === Tests ===

# doc = 'D:/data/california/lab_results/pdfs/flower-company/c7701ae4e337d10f769e40071e0381f2623029af21d09bc0b342c34be4a12c5d.pdf'
doc = r'D:/data/california/lab_results/pdfs/flower-company/bbd406b8a6f3f0683006bc2d366c75d9f400a4794513db10ca2e2c0b618fe62f.pdf'

# Open the PDF.
report = pdfplumber.open(doc)
front_page_text = report.pages[0].extract_text()
text = ''
for page in report.pages:
    text += page.extract_text()
lines = text.split('\n')
unique_lines = list(OrderedDict.fromkeys(lines))

# Get metadata.
obs = {}
for line in unique_lines:
    if 'metrc batch' in line.lower():
        obs['metrc_batch_label'] = line.split(':')[-1].strip()
    elif 'metrc sample' in line.lower():
        obs['metrc_sample_label'] = line.split(':')[-1].strip().split(' ')[0]
    if 'Completed:' in line:
        obs['date_tested'] = line.split('Completed:')[1].strip().split(' ')[0]
    elif 'Received:' in line:
        obs['date_received'] = line.split('Received:')[1].strip().split(' ')[0]
    elif 'Collected:' in line:
        obs['date_collected'] = line.split('Collected:')[1].strip().split(' ')[0]
    if 'Matrix:' in line:
        obs['product_category'] = line.split(':')[1].strip().split('Completed')[0].strip()
    if 'Batch#:' in line:
        obs['batch_number'] = line.split('Batch#:')[1].strip().split(' ')[0]
    if 'Sample Size:' in line:
        obs['sample_size'] = line.split('Sample Size:')[1].strip().split(' ')[0]
    if 'Batch:' in line and 'METRC' not in line:
        obs['batch_size'] = line.split('Batch:')[1].strip().split(' ')[0]

# Get the producer details.
front_page = report.pages[0]
area = (
    page.width * 0.8,
    page.height * 0.1,
    page.width * 1,
    page.height * 0.25,
)
crop = front_page.within_bbox(area)
details = crop.extract_text()
producer_lines = details.split('\n')
obs['producer'] = producer_lines[1]
obs['producer_license_number'] = producer_lines[2].split('#')[-1].strip()
obs['producer_street'] = producer_lines[3]
obs['producer_city'] = producer_lines[4].split(',')[0].strip()
obs['producer_state'] = producer_lines[4].split(',')[1].strip().split(' ')[0]
obs['producer_zipcode'] = producer_lines[4].split(' ')[-1].strip()

# Get the distributor details.
area = (
    page.width * 0.65,
    page.height * 0.1,
    page.width * 0.8,
    page.height * 0.25,
)
crop = front_page.within_bbox(area)
details = crop.extract_text()
producer_lines = details.split('\n')
obs['distributor'] = producer_lines[1]
obs['distributor_license_number'] = producer_lines[2].split('#')[-1].strip()
obs['distributor_street'] = producer_lines[3]
obs['distributor_city'] = producer_lines[4].split(',')[0].strip()
obs['distributor_state'] = producer_lines[4].split(',')[1].strip().split(' ')[0]
obs['distributor_zipcode'] = producer_lines[4].split(' ')[-1].strip()

# TODO: Get analyses and methods.
analyses = []
methods = []

# TODO: Get results.
results = []

# TODO: Get cannabinoids.
# - total_cannabinoids
# - total_thc
# - total_cbd


# TODO: pesticides


# TODO: mycotoxins


# TODO: residual_solvents


# TODO: microbes


# TODO: heavy_metals


# TODO: Get terpenes.
sublist = list_between_values(unique_lines, "Terpenes", "Primary Aromas")
for line in sublist:
    if 'LOQ =' in line or 'Date Tested' in line:
        continue
    elif 'Method' in line:
        methods.append(line.split('Method:')[1].strip())
    elif 'Total' in line:
        obs['total_terpenes'] = line.split('Total')[1].strip().split(' ')[0]


