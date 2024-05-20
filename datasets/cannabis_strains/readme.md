
# Cannabis Strains

This is a collection of cannabis strains curated by [Cannlytics](https://cannlytics.com).

## About the data

The dataset is partitioned into `all` strains and strains by state for states with available public lab results.

| State | Code | Status |
|-------|------|--------|
| [All](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/all) |  `all` | ✅ |
| [California](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/ca) | `ca`  | ✅ |
| [Colorado](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/co) | `co`  | ✅ |
| [Connecticut](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/ct) | `ct`  | ✅ |
| [Massachusetts](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/ma) | `ma`  | ✅ |
| [Washington](https://huggingface.co/datasets/cannlytics/cannabis_strains/tree/main/data/wa) | `wa`  | ✅ |

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect encounter in the parsed COA data.

| Field | Example | Description |
|-------|---------|-------------|
| `strain_id` | `"blue-dream"` | A unique identifier for the strain. |
| `strain_name` | `"Blue Dream"` | The name of the strain. |
| `avg_total_thc` | `18%` | Average total THC concentration observed. |
| `avg_total_cbd` | `1.5%` | Average total CBD concentration observed |
| `indica_percentage` | `40%` | Estimated percentage of Indica genetics. |
| `sativa_percentage` | `60%` | Estimated percentage of Sativa genetics. |
| `image_url` | `"http://example.com/image.jpg"` | URL to the main image of the strain. |
| `images` | `[{"url": "http://example.com/image1.jpg", "caption": "Side view"}]` | A list of images URLs related to the strain. |
| `description` | `"A popular strain for sativa lovers."` | Description of the strain. |
| `aliases` | `["BD", "Blueberry Haze"]` | Known aliases or other names for the strain. |
| `origin` | `["California", "USA"]` | The origin of the strain. |
| `breeder` | `"DJ Short"` | The breeder or creator of the strain. |
| `chemotype` | `"Type I"` | The chemotype classification of the strain. |
| `first_cultivation` | `"1990"` | The year when the strain was first cultivated. |
| `folklore` | `"Created during the 70s hippie movement."` | Folklore or stories associated with the strain. |
| `etymology` | `"Named after its dreamy effects."` | The etymology or origin of the strain's name. |
| `seed_availability` | `"Available"` | Availability status of seeds for the strain. |
| `first_tested_at` | `"CannaLab"` | The first laboratory where the strain was tested. |
| `history` | `"Developed in the 70s in California."` | History of the strain. |
| `references` | `[{"title": "Strain Encyclopedia", "url": "http://example.com"}]` | References or sources for information about the strain. |
| `awards` | `[{"name": "Cannabis Cup", "year": 2015}]` | Awards won by the strain. |
| `avg_price_per_gram` | `$10` | Average price per gram. |
| `created_at` | `"2024-01-01T00:00:00Z"` | The creation date of the strain entry. |
| `updated_at` | `"2024-01-02T00:00:00Z"` | The last update date of the strain entry. |


## Using the data

The data is split into subsets by state. You can retrieve all licenses by requesting the `all` subset.

```py
from datasets import load_dataset

# Get all data.
dataset = load_dataset('cannlytics/cannabis_strains', 'all')
data = dataset['data']
```

You can load the licenses for each state. For example:

```py
from datasets import load_dataset

# Get the data for a specific state.
dataset = load_dataset('cannlytics/cannabis_strains', 'ca')
data = dataset['data']
```


## Data Sources

| State | Data Source URL |
|-------|-----------------|
| California | <https://search.cannabis.ca.gov/> |
| Colorado | <https://sbg.colorado.gov/med/licensed-facilities> |
| Connecticut | <https://portal.ct.gov/DCP/Medical-Marijuana-Program/Connecticut-Medical-Marijuana-Dispensary-Facilities> |
| Massachusetts | <https://masscannabiscontrol.com/open-data/data-catalog/> |
| Washington | <https://lcb.wa.gov/records/frequently-requested-lists> |

## Data Collection

In the `algorithms` directory, you can find the algorithms used for data collection. You can use these algorithms to recreate the dataset. First, you will need to clone the repository:

```bash
git clone https://huggingface.co/datasets/cannlytics/cannabis_strains
```

You can then install the algorithm Python (3.9+) requirements:

```bash
cd cannabis_strains
pip install -r requirements.txt
```

Then you can run all of the data-collection algorithms:

```bash
python algorithms/main.py
```

Or you can run each algorithm individually. For example:

```bash
python algorithms/get_strains_ca.py
```

## License

```
Copyright (c) 2024 Cannlytics

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
