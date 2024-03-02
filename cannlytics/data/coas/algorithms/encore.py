from collections import OrderedDict
import pdfplumber

doc = 'D:/data/california/lab_results/pdfs/flower-company/c7701ae4e337d10f769e40071e0381f2623029af21d09bc0b342c34be4a12c5d.pdf'

report = pdfplumber.open(doc)
front_page_text = report.pages[0].extract_text()
text = ''
for page in report.pages:
    text += page.extract_text()
lines = text.split('\n')
unique_lines = list(OrderedDict.fromkeys(lines))

# TODO: Get metadata:
# batch_number
# traceability_ids
# lab_id
# strain_name
# product_type
# product_subtype
# date_produced
# date_collected
# date_received
# date_tested
# sample_size
# batch_size
# distributor
# distributor_license_number
# distributor_address
# distributor_street
# distributor_city
# distributor_state
# distributor_zipcode
# producer
# producer_license_number
# producer_address
# producer_street
# producer_city
# producer_state
# producer_zipcode

# TODO: Get totals.
# - total_cannabinoids
# - total_thc
# - total_cbd

# TODO: Get additional details.
# - lab_results_url
# - images

# TODO: Get analyses and methods.
analyses = []
methods = []

# TODO: Get results.
# - cannabinoids
# - pesticides
# - mycotoxins
# - residual_solvents
# - microbes
# - heavy_metals
# - terpenes? (unobserved)




