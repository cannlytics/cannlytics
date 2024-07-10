---
pretty_name: cannabis_results
license:
  - cc-by-4.0
tags:
  - cannabis
  - lab
  - tests
  - results
configs:
  - config_name: all
    data_files: "data/all/all-results-latest.csv"
  - config_name: ak
    data_files: "data/ak/ak-results-latest.csv"
  - config_name: ca
    data_files: "data/ca/ca-results-latest.csv"
  - config_name: ct
    data_files: "data/ct/ct-results-latest.csv"
  - config_name: fl
    data_files: "data/fl/fl-results-latest.csv"
  - config_name: ma
    data_files: "data/ma/ma-results-latest.csv"
  - config_name: md
    data_files: "data/md/md-results-latest.csv"
  - config_name: mi
    data_files: "data/mi/mi-results-latest.csv"
  - config_name: nv
    data_files: "data/nv/nv-results-latest.csv"
  - config_name: ny
    data_files: "data/ny/ny-results-latest.csv"
  - config_name: or
    data_files: "data/or/or-results-latest.csv"
  - config_name: ri
    data_files: "data/ri/ri-results-latest.csv"
  - config_name: ut
    data_files: "data/ut/ut-results-latest.csv"
  - config_name: wa
    data_files: "data/wa/wa-results-latest.csv"
---

# Cannabis Results

This is a repository of public cannabis lab test results obtained through public records requests and certificates of analysis (COAs) available online. Lab results are useful for cannabis cultivators, processors, retailers, consumers, and everyone else interested in cannabis. The repository contains raw data and curated datafiles for states with permitted cannabis markets where data is available. The curated datafiles are cleaned and standardized for ease of use, but may contain errors. The raw data is provided for transparency, reproducibility, and for you to improve upon.

> Notes: Any data of individuals and/or their contact information may not be used for commercial purposes. The data represents only a subset of the population of cannabis lab results, and the non-random nature of data collection should be taken into consideration.

> Curated by [🔥Cannlytics](https://cannlytics.com), a for-profit cannabis data and analytics company.

## Datasets

The data is split into datasets for each state where data is available.

<!-- Automated Table -->
| Dataset | State | Sources | Observations |
|--------|------|---------|--------------|
| `ak` | AK |  |  |
| `ca-flower-co` | CA |  | 12915 |
| `ca-glass-house` | CA | [Glass House Farms Strains](https://glasshousefarms.org/strains/) | 12915 |
| `ca-rawgarden` | CA |  | 12915 |
| `ca-sc-labs` | CA |  | 12915 |
| `ct` | CT |  | 21622 |
| `fl-flowery` | FL | [The Flowery](https://support.theflowery.co) | 17993 |
| `fl-jungleboys` | FL | [Jungle Boys Florida](https://jungleboysflorida.com) | 17993 |
| `fl-kaycha` | FL | [Florida Labs](https://knowthefactsmmj.com/cmtl/), [Florida Licenses](https://knowthefactsmmj.com/mmtc/), [Kaycha Labs](https://yourcoa.com) | 17993 |
| `fl-medical` | FL |  | 17993 |
| `fl-terplife` | FL | [TerpLife Labs](https://www.terplifelabs.com) | 17993 |
| `ma` | MA | [MCR Labs Test Results](https://reports.mcrlabs.com) | 7554 |
| `md` | MD | Public records request from the Maryland Medical Cannabis Commission (MMCC). | 95738 |
| `mi` | MI |  | 45637 |
| `nv` | NV |  |  |
| `ny` | NY |  |  |
| `or` | OR |  |  |
| `psi-labs` | PSI | PSI Labs Test Results, ChromeDriver, Automation Cartoon, Efficiency Cartoon, SHA in Python, Split / Explode a column of dictionaries into separate columns with pandas, Tidyverse: Wide and Long Data Tables, Web Scraping using Selenium and Python |  |
| `ri` | RI |  |  |
| `wa` | WA | [February 2023 CCRS Traceability Report](https://lcb.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml), [March 2023 CCRS Traceability Report](https://lcb.box.com/s/lg50ow8qx2xki2d4lr6raj0c2r22v711), [April 2023 CCRS Traceability Report](https://lcb.box.com/s/bj3g5inm77n8mrf7gk0h07f1o13dkfc7), [May 2023 CCRS Traceability Report](https://lcb.box.com/s/dzlcx9uzt3t1td8enzbtbgknw6oh9bzw), [June 2023 CCRS Traceability Report](https://lcb.box.com/s/d0g3mhtdyohhi4ic3zucekpnz017fy9o), [July 2023 CCRS Traceability Report](https://lcb.box.com/s/plb3dr2fvsuvgixb38g10tbwqos73biz), [August 2023 CCRS Traceability Report](https://lcb.box.com/s/59jw6qdt7sbg36g0xa2vw0ysr8us8cpo), [September 2023 CCRS Traceability Report](), [October 2023 monthly CCRS traceability data report](https://lcb.box.com/s/qt9xd2oqp2wqqz4xuppzuphhjvwfm67j), [November 2023 CCRS Traceability Report](https://lcb.box.com/s/pr8razl8bs3lu74ayk1d8a7iq8padhy1), [December 2023 CCRS Traceability Report](https://lcb.app.box.com/s/4vweufdqsmg41t2zadr56r4dcwqmvlit), [January 2024 CCRS Traceability Report](https://lcb.box.com/s/rb6di0vxgsycns134wq7i329m6d0qoin), [February and March 2024 CCRS Traceability Report](https://lcb.box.com/s/hqcfxcbkh4w8ixucatz43awbq6zw8b0z), [April 2024 CCRS Traceability Report](https://lcb.box.com/s/12kocnn0pvdejybb24x7mhf9n7sbc7hi), [WSLCB Guidance Sheets](https://lcb.box.com/s/n5f1eyybvjxfs8w49y4ztlqyzgd4842d) | 69400 |
| `wa-inventory` | WA |  | 69400 |

## Data Points

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect encounter in the parsed COA data.

| Field | Example| Description |
|-------|--------|-------------|
| `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
| `{analysis}_method` | "HPLC" | The method used for each analysis. |
| `{analysis}_status` | "pass" | The pass, fail, or N/A status for pass / fail analyses.   |
| `coa_urls` | [{"url": "", "filename": ""}] | A list of certificate of analysis (CoA) URLs. |
| `date_collected` | 2022-04-20T04:20 | An ISO-formatted time when the sample was collected. |
| `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
| `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
| `distributor` | "Your Favorite Dispo" | The name of the product distributor, if applicable. |
| `distributor_address` | "Under the Bridge, SF, CA 55555" | The distributor address, if applicable. |
| `distributor_street` | "Under the Bridge" | The distributor street, if applicable. |
| `distributor_city` | "SF" | The distributor city, if applicable. |
| `distributor_state` | "CA" | The distributor state, if applicable. |
| `distributor_zipcode` | "55555" | The distributor zip code, if applicable. |
| `distributor_license_number` | "L2Stat" | The distributor license number, if applicable. |
| `images` | [{"url": "", "filename": ""}] | A list of image URLs for the sample. |
| `lab_results_url` | "https://cannlytics.com/results" | A URL to the sample results online. |
| `producer` | "Grow Tent" | The producer of the sampled product. |
| `producer_address` | "3rd & Army, SF, CA 55555" | The producer's address. |
| `producer_street` | "3rd & Army" | The producer's street. |
| `producer_city` | "SF" | The producer's city. |
| `producer_state` | "CA" | The producer's state. |
| `producer_zipcode` | "55555" | The producer's zipcode. |
| `producer_license_number` | "L2Calc" | The producer's license number. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `lab_id` | "Sample-0001" | A lab-specific ID for the sample. |
| `product_type` | "flower" | The type of product. |
| `batch_number` | "Order-0001" | A batch number for the sample or product. |
| `metrc_ids` | ["1A4060300002199000003445"] | A list of relevant Metrc IDs. |
| `metrc_lab_id` | "1A4060300002199000003445" | The Metrc ID associated with the lab sample. |
| `metrc_source_id` | "1A4060300002199000003445" | The Metrc ID associated with the sampled product. |
| `product_size` | 2000 | The size of the product in milligrams. |
| `serving_size` | 1000 | An estimated serving size in milligrams. |
| `servings_per_package` | 2 | The number of servings per package. |
| `sample_weight` | 1 | The weight of the product sample in grams. |
| `results` | [{...},...] | A list of results, see below for result-specific fields. |
| `status` | "pass" | The overall pass / fail status for all contaminant screening analyses. |
| `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
| `total_thc` | 14.00 | The analytical total of THC and THCA. |
| `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
| `total_terpenes` | 0.42 | The sum of all terpenes measured. |
| `results_hash` | "{sha256-hash}" | An HMAC of the sample's `results` JSON signed with Cannlytics' public key, `"cannlytics.eth"`. |
| `sample_id` | "{sha256-hash}" | A generated ID to uniquely identify the `producer`, `product_name`, and `results`. |
| `sample_hash` | "{sha256-hash}" | An HMAC of the entire sample JSON signed with Cannlytics' public key, `"cannlytics.eth"`. |
| `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. |

Each result can contain the following fields.

| Field | Example| Description |
|-------|--------|-------------|
| `analysis` | "pesticides" | The analysis used to obtain the result. |
| `key` | "pyrethrins" | A standardized key for the result analyte. |
| `name` | "Pyrethrins" | The lab's internal name for the result analyte |
| `value` | 0.42 | The value of the result. |
| `mg_g` | 0.00000042 | The value of the result in milligrams per gram. |
| `units` | "ug/g" | The units for the result `value`, `limit`, `lod`, and `loq`. |
| `limit` | 0.5 | A pass / fail threshold for contaminant screening analyses. |
| `lod` | 0.01 | The limit of detection for the result analyte. Values below the `lod` are typically reported as `ND`. |
| `loq` | 0.1 | The limit of quantification for the result analyte. Values above the `lod` but below the `loq` are typically reported as `<LOQ`. |
| `status` | "pass" | The pass / fail status for contaminant screening analyses. |

## Using the Data

You can use [`datasets`](https://pypi.org/project/datasets/) to download the data.

```py
from datasets import load_dataset

# Download CA results.
dataset = load_dataset('cannlytics/cannabis_results', 'ca')
data = dataset['data']
assert len(data) > 0
print('Downloaded %i observations.' % len(data))
```

## Contributors

Thanks to [🔥Cannlytics](https://cannlytics.com), [@candy-o](https://github.com/candy-o), [@hcadeaux](https://huggingface.co/hcadeaux), [@keeganskeate](https://github.com/keeganskeate), [The CESC](https://thecesc.org), and the entire [Cannabis Data Science Team](https://meetup.com/cannabis-data-science/members) for their contributions.

## License

```
Copyright (c) 2022-2024 Cannlytics

The files associated with this dataset are licensed under a 
Creative Commons Attribution 4.0 International license.

You can share, copy and modify this dataset so long as you give
appropriate credit, provide a link to the CC BY license, and
indicate if changes were made, but you may not do so in a way
that suggests the rights holder has endorsed you or your use of
the dataset. Note that further permission may be required for
any content within the dataset that is identified as belonging
to a third party.
```
