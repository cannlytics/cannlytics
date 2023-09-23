---
pretty_name: cannabis_licenses
annotations_creators:
  - expert-generated
language_creators:
  - expert-generated
license:
  - cc-by-4.0
tags:
  - cannabis
  - licenses
---

# Cannabis Licenses

<!-- FIXME:
<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img style="max-height:365px;width:100%;max-width:720px;" alt="" src="analysis/figures/cannabis-licenses-map.png">
</div> -->

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
- **Repository:** <https://huggingface.co/datasets/cannlytics/cannabis_licenses>
- **Point of Contact:** <dev@cannlytics.com>

### Dataset Summary

**Cannabis Licenses** is a collection of cannabis license data for each state with permitted adult-use cannabis. The dataset also includes a sub-dataset, `all`, that includes all licenses.

## Dataset Structure

The dataset is partitioned into 18 subsets for each state and the aggregate.

| State | Code | Status |
|-------|------|--------|
|  [All](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/all) |  `all` | ✅ |
|  [Alaska](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ak) |  `ak` | ✅ |
|  [Arizona](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/az) | `az` | ✅ |
|  [California](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ca) | `ca`  | ✅ |
|  [Colorado](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/co) | `co`  | ✅ |
|  [Connecticut](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ct) | `ct`  | ✅ |
| [Delaware](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/de) | `md` | ✅ |
|  [Illinois](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/il) | `il`  | ✅ |
|  [Maine](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/me) | `me`  | ✅ |
| [Maryland](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/md) | `md` | ⚠️ Under development |
|  [Massachusetts](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ma) | `ma`  | ✅ |
|  [Michigan](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/mi) | `mi`  | ✅ |
| [Missouri](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/mo) | `mo` | ✅ |
|  [Montana](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/mt) | `mt`  | ✅ |
|  [Nevada](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/nv) | `nv`  | ✅ |
|  [New Jersey](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/nj) | `nj`  | ✅ |
|  [New Mexico](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/nm) | `nm`  | ✅ |
| [New York](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ny) | `ny` | ⚠️ Under development |
|  [Oregon](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/or) | `or`  | ✅  |
|  [Rhode Island](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/ri) | `ri`  | ✅ |
|  [Vermont](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/vt) | `vt`  | ✅ |
| Virginia | `va` | ⏳ Expected 2024 |
|  [Washington](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/wa) | `wa`  | ✅ |

The following states have issued medical cannabis licenses, but are not (yet) included in the dataset:

- Alabama
- Arkansas
- District of Columbia (D.C.)
- Florida
- Kentucky (2024)
- Louisiana
- Minnesota
- Mississippi
- New Hampshire
- North Dakota
- Ohio
- Oklahoma
- Pennsylvania
- South Dakota
- Utah
- West Virginia

### Data Instances

You can load the licenses for each state. For example:

```py
from datasets import load_dataset

# Get the licenses for a specific state.
dataset = load_dataset('cannlytics/cannabis_licenses', 'all')
data = dataset['data']
```

### Data Fields

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect to find for each observation.

| Field | Example | Description |
|-------|-----|-------------|
| `id` | `"1046"` | A state-unique ID for the license. |
| `license_number` | `"C10-0000423-LIC"` | A unique license number. |
| `license_status` | `"Active"` | The status of the license. Only licenses that are active are included. |
| `license_status_date` | `"2022-04-20T00:00"` | The date the status was assigned, an ISO-formatted date if present. |
| `license_term` | `"Provisional"` | The term for the license. |
| `license_type` | `"Commercial - Retailer"` | The type of business license. |
| `license_designation` | `"Adult-Use and Medicinal"` | A state-specific classification for the license. |
| `issue_date` | `"2019-07-15T00:00:00"` | An issue date for the license, an ISO-formatted date if present. |
| `expiration_date` | `"2023-07-14T00:00:00"` | An expiration date for the license, an ISO-formatted date if present. |
| `licensing_authority_id` | `"BCC"` | A unique ID for the state licensing authority. |
| `licensing_authority` | `"Bureau of Cannabis Control (BCC)"` | The state licensing authority. |
| `business_legal_name` | `"Movocan"` | The legal name of the business that owns the license. |
| `business_dba_name` | `"Movocan"` | The name the license is doing business as. |
| `business_owner_name` | `"redacted"` | The name of the owner of the license. |
| `business_structure` | `"Corporation"` | The structure of the business that owns the license. |
| `activity` | `"Pending Inspection"` | Any relevant license activity. |
| `premise_street_address` | `"1632 Gateway Rd"` | The street address of the business. |
| `premise_city` | `"Calexico"` | The city of the business. |
| `premise_state` | `"CA"` | The state abbreviation of the business. |
| `premise_county` | `"Imperial"` | The county of the business. |
| `premise_zip_code` | `"92231"` | The zip code of the business. |
| `business_email` | `"redacted@gmail.com"` | The business email of the license. |
| `business_phone` | `"(555) 555-5555"` | The business phone of the license. |
| `business_website` | `"cannlytics.com"` | The business website of the license. |
| `parcel_number` | `"A42"` | An ID for the business location. |
| `premise_latitude` | `32.69035693` | The latitude of the business. |
| `premise_longitude` | `-115.38987552` | The longitude of the business. |
| `data_refreshed_date` | `"2022-09-21T12:16:33.3866667"` | An ISO-formatted time when the license data was updated. |

### Data Splits

The data is split into subsets by state. You can retrieve all licenses by requesting the `all` subset.

```py
from datasets import load_dataset

# Get all cannabis licenses.
dataset = load_dataset('cannlytics/cannabis_licenses', 'all')
data = dataset['data']
```

## Dataset Creation

### Curation Rationale

Data about organizations operating in the cannabis industry for each state is valuable for research.

### Source Data

| State | Data Source URL |
|-------|-----------------|
|  Alaska | <https://www.commerce.alaska.gov/abc/marijuana/Home/licensesearch> |
|  Arizona | <https://azcarecheck.azdhs.gov/s/?licenseType=null> |
|  California | <https://search.cannabis.ca.gov/> |
|  Colorado | <https://sbg.colorado.gov/med/licensed-facilities> |
|  Connecticut | <https://portal.ct.gov/DCP/Medical-Marijuana-Program/Connecticut-Medical-Marijuana-Dispensary-Facilities> |
|  Delaware | <https://dhss.delaware.gov/dhss/dph/hsp/medmarcc.html> |
|  Illinois | <https://www.idfpr.com/LicenseLookup/AdultUseDispensaries.pdf> |
|  Maine | <https://www.maine.gov/dafs/ocp/open-data/adult-use> |
|  Maryland | <https://mmcc.maryland.gov/Pages/Dispensaries.aspx> |
|  Massachusetts | <https://masscannabiscontrol.com/open-data/data-catalog/> |
|  Michigan | <https://michigan.maps.arcgis.com/apps/webappviewer/index.html?id=cd5a1a76daaf470b823a382691c0ff60> |
|  Missouri | <https://health.mo.gov/safety/cannabis/licensed-facilities.php> |
|  Montana | <https://mtrevenue.gov/cannabis/#CannabisLicenses> |
|  Nevada | <https://ccb.nv.gov/list-of-licensees/> |
|  New Jersey | <https://data.nj.gov/stories/s/ggm4-mprw> |
|  New Mexico | <https://nmrldlpi.force.com/bcd/s/public-search-license?division=CCD&language=en_US> |
|  New York | <https://cannabis.ny.gov/licensing> |
|  Oregon | <https://www.oregon.gov/olcc/marijuana/pages/recreational-marijuana-licensing.aspx> |
|  Rhode Island | <https://dbr.ri.gov/office-cannabis-regulation/compassion-centers/licensed-compassion-centers> |
|  Vermont | <https://ccb.vermont.gov/licenses> |
|  Washington | <https://lcb.wa.gov/records/frequently-requested-lists> |

### Data Collection and Normalization

In the `algorithms` directory, you can find the algorithms used for data collection. You can use these algorithms to recreate the dataset. First, you will need to clone the repository:

```
git clone https://huggingface.co/datasets/cannlytics/cannabis_licenses
```

You can then install the algorithm Python (3.9+) requirements:

```
cd cannabis_licenses
pip install -r requirements.txt
```

Then you can run all of the data-collection algorithms:

```
python algorithms/main.py
```

Or you can run each algorithm individually. For example:

```
python algorithms/get_licenses_ny.py
```

### Personal and Sensitive Information

This dataset includes names of individuals, public addresses, and contact information for cannabis licensees. It is important to take care to use these data points in a legal manner.

## Considerations for Using the Data

### Social Impact of Dataset

Arguably, there is substantial social impact that could result from the study of permitted adult-use cannabis, therefore, researchers and data consumers alike should take the utmost care in the use of this dataset.

### Discussion of Biases

Cannlytics is a for-profit data and analytics company that primarily serves cannabis businesses. The data are not randomly collected and thus sampling bias should be taken into consideration.

### Other Known Limitations

The data is for adult-use cannabis licenses. It would be valuable to include medical cannabis licenses too.

## Additional Information

### Dataset Curators

Curated by [🔥Cannlytics](https://cannlytics.com)<br>
<contact@cannlytics.com>

### License

```
Copyright (c) 2022-2023 Cannlytics and the Cannabis Data Science Team

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
  journal={https://github.com/cannlytics/cannabis-data-science},
  year={2023}
}
```

### Contributions

Thanks to [🔥Cannlytics](https://cannlytics.com), [@candy-o](https://github.com/candy-o), [@hcadeaux](https://huggingface.co/hcadeaux), [@keeganskeate](https://github.com/keeganskeate), and the entire [Cannabis Data Science Team](https://meetup.com/cannabis-data-science/members) for their contributions.
