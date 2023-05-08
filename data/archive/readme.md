# Cannlytics Data Archive

The Cannlytics Data Archive is a collection of cannabis data from around the world. The data is archived locally, stored in a [cloud database](https://firebase.google.com/docs/firestore), and available for download from [Hugging Face](https://huggingface.co/datasets/cannlytics).

*United States*

| State | Licensees | Lab Results | Sales | Size |
|-------|-----------|-------------|-------|------|
| Alaska | ? | ? | ? | ? |
| Arizona | ? | ? | ? | ? |
| California | 10,000+ | 4,000+ | ❌ | 1.25+ GB |
| Colorado | ? | ? | ? | ? |
| Connecticut | 1-10,000 | 16,000+ | ❌ | 4.35+ GB |
| Illinois | ? | ? | ? | ? |
| Massachusetts | 1-10,000 | 7,000+ | ✅ | < 1 GB |
| Maryland | ? | ? | ? | ? |
| Maine | ? | ? | ? | ? |
| Michigan | ? | ? | ? | ? |
| Montana | ? | ? | ? | ? |
| New Jersey | ? | ? | ? | ? |
| New Mexico | ? | ? | ? | ? |
| New York | ? | ? | ? | ? |
| Nevada | ? | ? | ? | ? |
| Oregon | ? | ? | ? | ? |
| Rhode Island | ? | ? | ? | ? |
| Vermont | ? | ? | ? | ? |
| Washington | 1-10,000 | 60,000+ | ✅ | 61+ GB |

*International*

| Country | Licensees | Lab Results | Sales | Size |
|-------|-----------|-------------|-------|------|
| [Canada](https://www.canada.ca/en/health-canada/services/drugs-medication/cannabis/industry-licensees-applicants/licensed-cultivators-processors-sellers.html) | ? | ? | ? | ? |
| [Malta](https://medicinesauthority.gov.mt/cannabisformedicinalandresearchpurposes?l=1) | ? | ? | ? | ? |
| [South Africa](https://www.sahpra.org.za/approved-licences/) | ? | ? | ? | ? |
| [Thailand](https://plookganja.fda.moph.go.th/) | ? | ? | ? | ? |
| Uruguay | ? | ? | ? | ? |


<!-- ```bash
├── D:\\data
  ├── california
  │   └── lab_results
  ├── connecticut
  │   └── lab_results
  ├── massachusetts
  │   └── lab_results
  └── washington
      └── lab_results
  
``` -->

## Datasets

| Dataset | Description |
|-----------|-------------|
| `cannabis_licenses` | Cannabis license data for each state with permitted adult-use cannabis. |
| `cannabis_patents` | Cannabis patent data for each observed cannabis or hemp plant patent. |
| `cannabis_sales` | Cannabis sales data for each state with permitted adult-use cannabis. |
| `cannabis_strains` | Cannabis strain data for each observed strain. |
| `cannabis_tests` | Public cannabis lab test results. |
| `washington_cannabis_data` | Curated Washington Sate cannabis data. |

## Data Tools

| Tool | Description |
|------|-------------|
| `upload_licenses.py` | Get [cannabis license data from Hugging Face](https://huggingface.co/datasets/cannlytics/cannabis_licenses) and upload the data to Firestore. |
<!-- TODO:
  upload_results.py
  upload_washington.py
-->


## Licensees Data

[Cannabis Licenses](./cannabis_licenses/README.md) is a collection of cannabis license data for each state with permitted adult-use cannabis. The dataset also includes a sub-dataset, `all`, that includes all licenses.

## Cannabis Tests

[Cannabis Tests](./cannabis_tests/README.md) is a collection of public cannabis lab test results parsed by [`CoADoc`](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/coas), a certificate of analysis (COA) parsing tool.


## Washington State Cannabis Data

[Washington Cannabis Data](./washington_cannabis_data/README.md) is a dataset of curated Washington Sate cannabis data. The dataset consists of sub-datasets for each main type of cannabis data, segmented by time.
