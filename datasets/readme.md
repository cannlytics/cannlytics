# Cannlytics Datasets

Cannlytics Datasets is a collection of cannabis data from around the world. The data is archived locally, stored in a [cloud database](https://firebase.google.com/docs/firestore), and available for download from [Hugging Face](https://huggingface.co/datasets/cannlytics).

## Datasets

| Dataset | Description |
|-----------|-------------|
| [`cannabis_licenses`](https://huggingface.co/datasets/cannlytics/cannabis_licenses) | Cannabis license data for each state with permitted adult-use cannabis. |
| [`cannabis_tests`](https://huggingface.co/datasets/cannlytics/cannabis_tests) | Public cannabis lab test results. |
<!-- | [`cannabis_patents`](https://huggingface.co/datasets/cannlytics/cannabis_patents) | Cannabis patent data for each observed cannabis or hemp plant patent. |
| [`cannabis_sales`](https://huggingface.co/datasets/cannlytics/cannabis_sales) | Cannabis sales data for each state with permitted adult-use cannabis. |
| [`cannabis_strains`](https://huggingface.co/datasets/cannlytics/cannabis_strains) | Cannabis strain data for each observed strain. | -->

## Data Tools

| Tool | Description |
|------|-------------|
| `cannabis_licenses/upload_licenses.py` | Upload cannabis license data to Firestore. |
| `cannabis_tests/upload_results.py` | Upload cannabis test result data to Firestore. |
<!-- | `cannabis_patents/upload_patents.py` | Upload cannabis patent data to Firestore. |
| `cannabis_sales/upload_sales.py` | Upload cannabis sales data to Firestore. |
| `cannabis_strains/upload_strains.py` | Upload cannabis strain data to Firestore. | -->
