# Cannlytics Data Archive

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
