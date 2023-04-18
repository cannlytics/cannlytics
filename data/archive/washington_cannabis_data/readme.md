---
annotations_creators:
  - expert-generated
language_creators:
  - expert-generated
license:
  - cc-by-4.0
pretty_name: cannabis_sales
size_categories:
  - 10K<n<100K
source_datasets:
  - original
tags:
  - cannabis
  - sales
  - washington
---

# Cannabis Sales

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
- **Repository:** <https://huggingface.co/datasets/cannlytics/cannabis_sales>
- **Point of Contact:** <dev@cannlytics.com>

### Dataset Summary

This dataset is a collection of Washington State cannabis traceability data that is in the public domain.

## Dataset Structure

The dataset is partitioned as follows.

| Subset | Description | Number of Observations |
|--------|--------|--------------|
| `washington-2023-01` | Cannabis sales items in Washington State in January of 2023. | 81,768 |

### Data Instances

You can load the `data` for each of the dataset files. For example:

```py
from datasets import load_dataset

# Download sales data for January 2023.
dataset = load_dataset('cannlytics/cannabis_sales', 'washington-2023-01')
data = dataset['data']
assert len(data) > 0
print('Downloaded %i observations.' % len(data))
```

> Note: Data is requested through [a public records](https://lcb.wa.gov/records/make-public-records-request) request on the 21st of each month. Data is typically through the first week of the month. Data processing can take up to 1 week. Therefore, the latest month's data is likely incomplete until the end of the following month and data processing has occurred.

### Data Fields

Below are the standardized sales items fields:

| Field | Example| Description |
|-------|-----|-------------|
| `strain_name` | "Blue Rhino" | A strain name, if specified. |
<!-- | `analyses` | ["cannabinoids"] | A list of analyses performed on a given sample. |
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
| `sample_hash` | "{sha256-hash}" | An HMAC of the entire sample JSON signed with Cannlytics' public key, `"cannlytics.eth"`. | -->

### Data Splits

The data is split by state and month, e.g. `washington-2023-01`. 

## Dataset Creation

### Curation Rationale

Cannabis sales data is of interest to many parties and having a public repository of cannabis sales data could help data scientist in their endeavors.

### Source Data

| Data Source | URL |
|-------------|-----|
| WSLCB PRR 2023-03-06 | <https://lcb.app.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml> |
| WSLCB PRR 2023-01-27 | <https://lcb.box.com/s/wzfoqysl4v9aqljwc0pi0g5ea6bch759> |

#### Data Collection and Normalization

You can recreate the dataset using the open source algorithms in the repository. First clone the repository:

```
git clone https://huggingface.co/datasets/cannlytics/cannabis_sales
```

You can then install the requirements:

```
cd cannabis_sales
pip install -r requirements.txt
```

Then you can run all of the data collection algorithms:

```
python algorithms/main.py
```

Or you can run each algorithm individually. For example:

```
python algorithms/washington_sales.py
```

In the `algorithms` directory, you can find the data collection scripts described in the table below.

| Algorithm |  State | Description | 
|-----------|---------------|-------------|
| `washington_sales.py` | WA | Curate Washington State cannabis sales items. |

<!-- | Tool | Description |
|------|-------------|
| `ccrs_sales_by_licensee.py` | Calculate `total_price`, `total_discount`, `total_sales_tax`, and `total_other_tax` by `licensee_id` by `date`. |
| `upload_ccrs_stats.py` | Calculate CCRS statistics and upload the statistics to Firestore (*Under development*). | -->

### Personal and Sensitive Information

The dataset includes public addresses and contact information for related cannabis licensees. It is important to take care to use these data points in a legal manner.

## Considerations for Using the Data

### Social Impact of Dataset

Arguably, there is substantial social impact that could result from the study of cannabis, therefore, researchers and data consumers alike should take the utmost care in the use of this dataset.

### Discussion of Biases

Cannlytics is a for-profit data and analytics company that primarily serves cannabis businesses. The data are not randomly collected and thus sampling bias should be taken into consideration.

### Other Known Limitations

The dataset presumably has missing data and errors.

## Additional Information

### Dataset Curators

Curated by [🔥Cannlytics](https://cannlytics.com)<br>
<dev@cannlytics.com>

### License

```
Copyright (c) 2023 Cannlytics and the Cannabis Data Science Team

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
@misc{cannlytics2023,
  title={Cannabis Data Science},
  author={Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  journal={https://github.com/cannlytics/cannlytics},
  year={2023}
}
```

### Contributions

Thanks to [🔥Cannlytics](https://cannlytics.com), [@candy-o](https://github.com/candy-o), [@keeganskeate](https://github.com/keeganskeate), and the entire [Cannabis Data Science Team](https://meetup.com/cannabis-data-science/members) for their contributions.
