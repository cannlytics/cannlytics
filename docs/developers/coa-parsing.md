<!-- | Cannlytics SOP-0002 |  |
|---------------------|--|
| Title | Certificate of Analysis (COA) Parsing |
| Version | 0.0.2 |
| Created At | 2022-09-22 |
| Updated At | 2022-11-27 |
| Review Period | Annual |
| Last Review | 2023-07-18 |
| Author | Keegan Skeate, Founder |
| Approved by | Keegan Skeate, Founder |
| Status | Active | -->

## Introduction

**Certificate of Analysis (COA) Parsing**, SOP-0002, defines how Cannlytics creates COA parsing algorithms.

## Purpose

Creating COA parsing algorithms requires much custom coding, however, having a structured approach is helpful in the development process. Creating custom COA parsing algorithms is time-consuming, but arguably provides much value. Therefore, writing custom COA parsing algorithms is usually a high value-added procedure and having a standard operating procedure for approaching the task is important. This SOP outlines steps that you can take to make writing COA parsing algorithms easier.

## Procedure

First, check if you can identify the LIMS that produced the COA with:

```py
from cannlytics.data.coas import CoADoc

doc = 'coa.pdf'
parser = CoADoc()
lims = parser.identify_lims(doc)
if lims is None:
    print('New COA parsing routine needed.')
```

If the LIMS cannot be identified, then a new COA parsing algorithm is likely needed. You can define a constant for the lab or LIMS, e.g. `LAB_X`, and add parameters such as `lab`, `lims`, and `url` that are used in `CoADoc`'s `identify_lims` method. You can test identification with:

```py
LAB_X = {
    'coa_algorithm': 'labx.py',
    'coa_algorithm_entry_point': 'parse_labx_coa',
    'lims': 'Lab X',
    'url': 'https://console.cannlytics.com',
    'lab': 'Lab X',
    'lab_website': 'https://cannlytics.com',
    'lab_license_number': '',
    'lab_image_url': '',
    'lab_address': '',
    'lab_street': '',
    'lab_city': '',
    'lab_county': '',
    'lab_state': '',
    'lab_zipcode': '',
    'lab_latitude': 0.0,
    'lab_longitude': 0.0,
    'lab_phone': '',
    'lab_email': '',
}

lims = parser.identify_lims(doc, lims={'Lab X': LAB_X})
assert lims == 'Lab X'
```

Once you have identified the lab or LIMS, then you are ready to extract the data. A good starting point for extracting data is to read the PDF with `pdfplumber`.

```py
report = pdfplumber.open(doc)
```

If you can extract table data, then that is a good place to start extracting data:

```py
for page in report.pages:
    print(page.extract_tables())
```

If you can't find any table data or not all of the data are in tables, then you can extract all of the text and parse to the best of your abilities:

```py
print('Parse data with custom logic:')
for page in report.pages:
    text = page.extract_text()
    lines = text.split('\n')
    for line in lines:
        print(line)
```

You can also:

- Set lab-specific and COA-specific constants to help parse data as needed.
- Outline the core pieces of data that you'll collect:
  * Producer details;
  * Sample details;
  * Analyses;
  * Methods;
  * Results.

It will likely take a fair amount of custom logic to parse the above data points. Afterwards, you can standardize the results and create a hash to serve as a unique ID for data that was collected.

```py
# Turn dates to ISO format.
date_columns = [x for x in obs.keys() if x.startswith('date')]
for date_column in date_columns:
    try:
        obs[date_column] = pd.to_datetime(obs[date_column]).isoformat()
    except:
        pass

# Finish data collection with a freshly minted sample ID.
obs = {**LAB_X, **obs}
obs['analyses'] = json.dumps(analyses)
obs['coa_algorithm_version'] = __version__
obs['coa_parsed_at'] = datetime.now().isoformat()
obs['methods'] = json.dumps(methods)
obs['results'] = results
obs['results_hash'] = create_hash(results)
obs['sample_id'] = create_sample_id(
    private_key=json.dumps(results),
    public_key=obs['product_name'],
    salt=obs.get('producer', obs.get('date_tested', 'cannlytics.eth')),
)
obs['sample_hash'] = create_hash(obs)
```

Finally, you can import your algorithm and include it in the `LIMS` constant in `cannlytics.data.coas.coas.py`. Once included, then you have successfully added a new COA parsing algorithm that can help unlock rich laboratory data from hopefully many certificates.

## Training

You should ensure that your COA parsing algorithm passes tests and that other Cannabis Data Scientists can use the algorithm to parse test COAs.

## History

- 0.0.1 - Initial draft.
- 0.0.2 - Instructions written in full.
