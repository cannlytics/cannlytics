---
annotations_creators:
  - expert-generated
language_creators:
  - expert-generated
license:
  - cc-by-4.0
pretty_name: cannabis_tests
size_categories:
  - 1K<n<10K
source_datasets:
  - original
tags:
  - cannabis
  - lab results
  - tests
---

# Cannabis Tests, Curated by Cannlytics

<div style="margin-top:1rem; margin-bottom: 1rem;">
  <img width="240px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fdatasets%2Fcannabis_tests%2Fcannabis_tests_curated_by_cannlytics.png?alt=media&token=22e4d1da-6b30-4c3f-9ff7-1954ac2739b2">
</div>

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Dataset Description](#dataset-description)
  - [Dataset Summary](#dataset-summary)
- [Dataset Structure](#dataset-structure)
  - [Data Instances](#data-instances)
  - [Data Fields](#data-fields)
  - [Data Splits](#data-splits)
- [Dataset Creation](#dataset-creation)
  - [Curation Rationale](#curation-rationale)
  - [Source Data](#source-data)
  - [Data Collection and Normalization](#data-collection-and-normalization)
  - [Personal and Sensitive Information](#personal-and-sensitive-information)
- [Considerations for Using the Data](#considerations-for-using-the-data)
  - [Social Impact of Dataset](#social-impact-of-dataset)
  - [Discussion of Biases](#discussion-of-biases)
  - [Other Known Limitations](#other-known-limitations)
- [Additional Information](#additional-information)
  - [Dataset Curators](#dataset-curators)
  - [License](#license)
  - [Citation](#citation)
  - [Contributions](#contributions)

## Dataset Description

- **Homepage:** <https://github.com/cannlytics/cannlytics>
- **Repository:** <https://huggingface.co/datasets/cannlytics/cannabis_tests>
- **Point of Contact:** <dev@cannlytics.com>

### Dataset Summary

This dataset is a collection of public cannabis lab test results parsed by [`CoADoc`](https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/coas), a certificate of analysis (COA) parsing tool.

## Dataset Structure

The dataset is partitioned into the various sources of lab results.

| Subset | Source | Observations |
|--------|--------|--------------|
| `rawgarden` | Raw Gardens | 2,667 |
| `mcrlabs` | MCR Labs | Coming soon! |
| `psilabs` | PSI Labs | Coming soon! |
| `sclabs` | SC Labs | Coming soon! |
| `washington` | Washington State | Coming soon! |

### Data Instances

You can load the `details` for each of the dataset files. For example:

```py
from datasets import load_dataset

# Download Raw Garden lab result details.
dataset = load_dataset('cannlytics/cannabis_tests', 'rawgarden')
details = dataset['details']
assert len(details) > 0
print('Downloaded %i observations.' % len(details))
```

> Note: Configurations for `results` and `values` are planned. For now, you can create these data with `CoADoc().save(details, out_file)`.

### Data Fields

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect encounter in the parsed COA data.

| Field | Example| Description |
|-------|-----|-------------|
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
<!-- | `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. | -->

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

### Data Splits

The data is split into `details`, `results`, and `values` data. Configurations for `results` and `values` are planned. For now, you can create these data with:

```py
from cannlytics.data.coas import CoADoc
from datasets import load_dataset
import pandas as pd

# Download Raw Garden lab result details.
repo = 'cannlytics/cannabis_tests'
dataset = load_dataset(repo, 'rawgarden')
details = dataset['details']

# Save the data locally with "Details", "Results", and "Values" worksheets.
outfile = 'details.xlsx'
parser = CoADoc()
parser.save(details.to_pandas(), outfile)

# Read the values.
values = pd.read_excel(outfile, sheet_name='Values')

# Read the results.
results = pd.read_excel(outfile, sheet_name='Results')
```

<!-- Training data is used for training your models. Validation data is used for evaluating your trained models, to help you determine a final model. Test data is used to evaluate your final model. -->

## Dataset Creation

### Curation Rationale

Certificates of analysis (CoAs) are abundant for cannabis cultivators, processors, retailers, and consumers too, but the data is often locked away. Rich, valuable laboratory data so close, yet so far away! CoADoc puts these vital data points in your hands by parsing PDFs and URLs, finding all the data, standardizing the data, and cleanly returning the data to you.

### Source Data

| Data Source | URL |
|-------------|-----|
| MCR Labs Test Results | <https://reports.mcrlabs.com> |
| PSI Labs Test Results | <https://results.psilabs.org/test-results/> |
| Raw Garden Test Results | <https://rawgarden.farm/lab-results/> |
| SC Labs Test Results | <https://client.sclabs.com/> |
| Washington State Lab Test Results | <https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd> |

#### Data Collection and Normalization

You can recreate the dataset using the open source algorithms in the repository. First clone the repository:

```
git clone https://huggingface.co/datasets/cannlytics/cannabis_tests
```

You can then install the algorithm Python (3.9+) requirements:

```
cd cannabis_tests
pip install -r requirements.txt
```

Then you can run all of the data-collection algorithms:

```
python algorithms/main.py
```

Or you can run each algorithm individually. For example:

```
python algorithms/get_results_mcrlabs.py
```

In the `algorithms` directory, you can find the data collection scripts described in the table below.

| Algorithm |  Organization | Description | 
|-----------|---------------|-------------|
| `get_results_mcrlabs.py` | MCR Labs | Get lab results published by MCR Labs. |
| `get_results_psilabs.py` | PSI Labs | Get historic lab results published by MCR Labs. |
| `get_results_rawgarden.py` | Raw Garden | Get lab results Raw Garden publishes for their products. |
| `get_results_sclabs.py` | SC Labs | Get lab results published by SC Labs. |
| `get_results_washington.py` | Washington State | Get historic lab results obtained through a FOIA request in Washington State. |

### Personal and Sensitive Information

The dataset includes public addresses and contact information for related cannabis licensees. It is important to take care to use these data points in a legal manner.

## Considerations for Using the Data

### Social Impact of Dataset

Arguably, there is substantial social impact that could result from the study of cannabis, therefore, researchers and data consumers alike should take the utmost care in the use of this dataset.

### Discussion of Biases

Cannlytics is a for-profit data and analytics company that primarily serves cannabis businesses. The data are not randomly collected and thus sampling bias should be taken into consideration.

### Other Known Limitations

The data represents only a subset of the population of cannabis lab results. Non-standard values are coded as follows.

| Actual | Coding |
|--------|--------|
| `'ND'` | `0.000000001` |
| `'No detection in 1 gram'` | `0.000000001` |
| `'Negative/1g'` | `0.000000001` |
| '`PASS'` | `0.000000001` |
| `'<LOD'` | `0.00000001` |
| `'< LOD'` | `0.00000001` |
| `'<LOQ'` | `0.0000001` |
| `'< LOQ'` | `0.0000001` |
| `'<LLOQ'` | `0.0000001` |
| `'≥ LOD'` | `10001` |
| `'NR'` | `None` |
| `'N/A'` | `None` |
| `'na'` | `None` |
| `'NT'` | `None` |

## Additional Information

### Dataset Curators

Curated by [🔥Cannlytics](https://cannlytics.com)<br>
<dev@cannlytics.com>

### License

```
Copyright (c) 2022 Cannlytics and the Cannabis Data Science Team

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

### Citation

Please cite the following if you use the code examples in your research:

```bibtex
@misc{cannlytics2022,
  title={Cannabis Data Science},
  author={Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  journal={https://github.com/cannlytics/cannabis-data-science},
  year={2022}
}
```

### Contributions

Thanks to [🔥Cannlytics](https://cannlytics.com), [@candy-o](https://github.com/candy-o), [@hcadeaux](https://huggingface.co/hcadeaux), [@keeganskeate](https://github.com/keeganskeate), [The CESC](https://thecesc.org), and the entire [Cannabis Data Science Team](https://meetup.com/cannabis-data-science/members) for their contributions.
