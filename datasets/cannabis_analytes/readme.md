---
pretty_name: cannabis_analytes
license:
  - cc-by-4.0
---

# Cannabis Analytes

This dataset consists of analyte data for various analytes that are regularly tested for in cannabis. The dataset consists of sub-datasets for each type of test, as well as a sub-dataset that includes all analytes.

## Dataset Structure

The dataset is partitioned into 18 subsets for each state and the aggregate.

| State | Code | Status |
|  [All](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/analytes.json) |  `all` | ✅ |
|  [Cannabinoids](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/cannabinoids.json) |  `cannabinoids` | ✅ |
|  [Terpenes](https://huggingface.co/datasets/cannlytics/cannabis_licenses/tree/main/data/terpenes.json) |  `terpenes` | ✅ |
|  Pesticides |  `pesticides` | ⏳ Coming soon |
|  Microbes |  `microbes` | ⏳ Coming soon |
|  Heavy metals |  `heavy_metals` | ⏳ Coming soon |
|  Residual solvents |  `residual_solvents` | ⏳ Coming soon |
|  Other |  `other` | ⏳ Coming soon |

## Using the Dataset

You can load all the analytes, or the analytes for a specific test. For example:

```py
from datasets import load_dataset

# Get all of the analytes
dataset = load_dataset('cannlytics/cannabis_licenses', 'all')
analytes = dataset['data']

# Get the cannabinoids.
dataset = load_dataset('cannlytics/cannabis_licenses', 'cannabinoids')
terpenes = dataset['data']

# Get the terpenes.
dataset = load_dataset('cannlytics/cannabis_licenses', 'terpenes')
terpenes = dataset['data']
```

## Data Fields

Below is a non-exhaustive list of fields, used to standardize the various data that are encountered, that you may expect to find for each observation.

## Data Fields

Below is a non-exhaustive list of fields used to standardize the various data that are encountered. You may expect to find the following for each observation:

| Field                        | Example                                      | Description                                                                                          |
|------------------------------|----------------------------------------------|------------------------------------------------------------------------------------------------------|
| `key`                        | `"thca"`                                     | A unique ID for each analyte.                                                                        |
| `description`                | `"Δ-9-Tetrahydrocannabinol is a cannabinoid..."` | A brief description or summary about the analyte.                                                    |
| `name`                       | `"THC"`                                      | Common name of the analyte.                                                                          |
| `scientific_name`            | `"\u0394-9-Tetrahydrocannabinol"`            | The scientific name or IUPAC name of the analyte.                                                    |
| `type`                       | `"cannabinoid"`                              | The type or classification of the analyte (e.g., terpene, cannabinoid).                              |
| `wikipedia_url`              | `"https://en.wikipedia.org/wiki/Tetrahydrocannabinol"` | The Wikipedia URL where more detailed information can be found about the analyte.                    |
| `degrades_to`                | `["cannabinol"]`                             | A list of chemicals or substances the analyte degrades to.                                           |
| `precursors`                 | `["thca"]`                                   | A list of precursor chemicals or substances related to the analyte.                                  |
| `subtype`                    | `"psychoactive"`                             | A sub-classification or additional details about the type of the analyte.                            |
| `cas_number`                 | `"1972-08-3"`                                | The Chemical Abstracts Service (CAS) registry number, which is a unique identifier for chemical substances.|
| `chemical_formula`           | `"C21H30O2"`                                 | The chemical formula of the analyte.                                                                 |
| `molar_mass`                 | `"314.5 g/mol"`                              | The molar mass of the analyte.                                                                       |
| `density`                    | `"1.0±0.1 g/cm3"`                            | The density of the analyte.                                                                          |
| `boiling_point`              | `"383.5±42.0 °C"`                            | The boiling point of the analyte.                                                                    |
| `image_url`                  | `"https://example.com/image.jpg"`            | URL of an image representing the analyte.                                                            |
| `chemical_formula_image_url` | `"https://example.com/formula_image.jpg"`    | URL of an image representing the chemical formula of the analyte.                                    |

