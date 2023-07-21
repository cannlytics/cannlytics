"""
Cannabis Tests
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/10/2022
Updated: 6/9/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
import json
import datasets
import pandas as pd
import urllib.request


# Constants.
_ALGORITHM = 'cannabis_tests.py'
_VERSION = '1.1.0'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_tests'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Cannabis results (https://cannlytics.com/data/results) is a
dataset of curated cannabis lab test results.
"""
_CITATION = """\
@inproceedings{cannlytics2023cannabis_tests,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Tests: Aggregated Cannabis Lab Test Results},
  booktitle = {Cannabis Data Science},
  month     = {June},
  year      = {2023},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Read subsets from local source.
try:
    with open('cannabis_results.json', 'r') as f:
        SUBSETS = json.loads(f.read())

# Otherwise, read subsets from Hugging Face.
except:
    with urllib.request.urlopen('https://huggingface.co/datasets/cannlytics/cannabis_tests/raw/main/cannabis_results.json') as url:
        SUBSETS = json.load(url)

# Lab result model.
_FEATURES = datasets.Features({
    'sample_hash': datasets.Value(dtype='string'),
    'results_hash': datasets.Value(dtype='string'),
    'sample_id': datasets.Value(dtype='string'),
    'product_name': datasets.Value(dtype='string'),
    'producer': datasets.Value(dtype='string'),
    'product_type': datasets.Value(dtype='string'),
    'product_subtype': datasets.Value(dtype='string'),
    'date_tested': datasets.Value(dtype='string'),
    'analyses': datasets.Value(dtype='string'),
    'batch_number': datasets.Value(dtype='string'),
    'batch_size': datasets.Value(dtype='string'),
    'batch_units': datasets.Value(dtype='string'),
    'cannabinoids_method': datasets.Value(dtype='string'),
    'cannabinoids_status': datasets.Value(dtype='string'),
    'coa_algorithm': datasets.Value(dtype='string'),
    'coa_algorithm_entry_point': datasets.Value(dtype='string'),
    'coa_parsed_at': datasets.Value(dtype='string'),
    'coa_pdf': datasets.Value(dtype='string'),
    'coa_urls': datasets.Value(dtype='string'),
    'date_collected': datasets.Value(dtype='string'),
    'date_produced': datasets.Value(dtype='string'),
    'date_received': datasets.Value(dtype='string'),
    'date_retail': datasets.Value(dtype='string'),
    'delta_9_thc_per_unit': datasets.Value(dtype='string'),
    'distributor': datasets.Value(dtype='string'),
    'distributor_address': datasets.Value(dtype='string'),
    'distributor_city': datasets.Value(dtype='string'),
    'distributor_license_number': datasets.Value(dtype='string'),
    'distributor_state': datasets.Value(dtype='string'),
    'distributor_street': datasets.Value(dtype='string'),
    'distributor_zipcode': datasets.Value(dtype='float64'),
    'foreign_matter_method': datasets.Value(dtype='string'),
    'foreign_matter_status': datasets.Value(dtype='string'),
    'heavy_metals_method': datasets.Value(dtype='string'),
    'heavy_metals_status': datasets.Value(dtype='string'),
    'images': datasets.Value(dtype='string'),
    'lab': datasets.Value(dtype='string'),
    'lab_address': datasets.Value(dtype='string'),
    'lab_city': datasets.Value(dtype='string'),
    'lab_county': datasets.Value(dtype='string'),
    'lab_email': datasets.Value(dtype='string'),
    'lab_id': datasets.Value(dtype='string'),
    'lab_image_url': datasets.Value(dtype='string'),
    'lab_latitude': datasets.Value(dtype='float64'),
    'lab_license_number': datasets.Value(dtype='string'),
    'lab_longitude': datasets.Value(dtype='float64'),
    'lab_phone': datasets.Value(dtype='string'),
    'lab_results_url': datasets.Value(dtype='string'),
    'lab_state': datasets.Value(dtype='string'),
    'lab_street': datasets.Value(dtype='string'),
    'lab_website': datasets.Value(dtype='string'),
    'lab_zipcode': datasets.Value(dtype='int64'),
    'lims': datasets.Value(dtype='string'),
    'metrc_ids': datasets.Value(dtype='string'),
    'metrc_lab_id': datasets.Value(dtype='string'),
    'metrc_source_id': datasets.Value(dtype='string'),
    'microbes_method': datasets.Value(dtype='string'),
    'microbes_status': datasets.Value(dtype='string'),
    'moisture_content': datasets.Value(dtype='string'),
    'moisture_method': datasets.Value(dtype='string'),
    'mycotoxins_method': datasets.Value(dtype='string'),
    'mycotoxins_status': datasets.Value(dtype='string'),
    'notes': datasets.Value(dtype='string'),
    'pesticides_method': datasets.Value(dtype='string'),
    'pesticides_status': datasets.Value(dtype='string'),
    'producer_address': datasets.Value(dtype='string'),
    'producer_city': datasets.Value(dtype='string'),
    'producer_image_url': datasets.Value(dtype='string'),
    'producer_license_number': datasets.Value(dtype='string'),
    'producer_state': datasets.Value(dtype='string'),
    'producer_street': datasets.Value(dtype='string'),
    'producer_url': datasets.Value(dtype='string'),
    'producer_zipcode': datasets.Value(dtype='float64'),
    'product_size': datasets.Value(dtype='string'),
    'public': datasets.Value(dtype='float64'),
    'residual_solvents_method': datasets.Value(dtype='string'),
    'residual_solvents_status': datasets.Value(dtype='string'),
    'results': datasets.Value(dtype='string'),
    'sample_number': datasets.Value(dtype='float64'),
    'sample_size': datasets.Value(dtype='string'),
    'sampling_method': datasets.Value(dtype='string'),
    'serving_size': datasets.Value(dtype='string'),
    'status': datasets.Value(dtype='string'),
    'sum_of_cannabinoids': datasets.Value(dtype='float64'),
    'terpenes_method': datasets.Value(dtype='string'),
    'terpenes_status': datasets.Value(dtype='string'),
    'total_cannabinoids': datasets.Value(dtype='float64'),
    'total_cbc': datasets.Value(dtype='float64'),
    'total_cbd': datasets.Value(dtype='float64'),
    'total_cbdv': datasets.Value(dtype='float64'),
    'total_cbg': datasets.Value(dtype='float64'),
    'total_terpenes': datasets.Value(dtype='float64'),
    'total_terpenes_mg_g': datasets.Value(dtype='float64'),
    'total_thc': datasets.Value(dtype='float64'),
    'total_thcv': datasets.Value(dtype='float64'),
    'url': datasets.Value(dtype='string'),
    'water_activity_method': datasets.Value(dtype='string'),
    'water_activity_status': datasets.Value(dtype='string')
})


class CannabisTestsConfig(datasets.BuilderConfig):
    """BuilderConfig for Cannabis Tests."""

    def __init__(self, name, **kwargs):
        """BuilderConfig for Cannabis Tests."""
        description = _DESCRIPTION
        description += f'This configuration is for the `{name}` subset.'
        super().__init__(name=name, description=description, **kwargs)

class CannabisTests(datasets.GeneratorBasedBuilder):
    """The Cannabis Tests dataset."""

    # Parameters.
    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = CannabisTestsConfig
    BUILDER_CONFIGS = [CannabisTestsConfig(s) for s in SUBSETS.keys()]
    DEFAULT_CONFIG_NAME = 'all'

    def _info(self):
        """Returns the dataset metadata."""
        return datasets.DatasetInfo(
            features=_FEATURES,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
            description=_DESCRIPTION,
            license=_LICENSE,
            version=_VERSION,
        )
    
    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        config_name = self.config.name
        data_url = SUBSETS[config_name]['data_url']
        urls = {config_name: data_url}
        downloaded_files = dl_manager.download_and_extract(urls)
        filepath = downloaded_files[config_name]
        params = {'filepath': filepath}
        return [datasets.SplitGenerator(name='data', gen_kwargs=params)]
    
    def _generate_examples(self, filepath):
        """Returns the examples in raw text form."""
        with open(filepath) as f:
            df = pd.read_csv(filepath)
            for index, row in df.iterrows():
                obs = row.to_dict()
                yield index, obs


# === Tests ===
if __name__ == '__main__':

    from datasets import load_dataset

    # Define all of the dataset subsets.
    subsets = list(SUBSETS.keys())

    # Load each dataset subset.
    aggregate = {}
    for subset in subsets:
        print('Loading subset:', subset)
        dataset = load_dataset(_ALGORITHM, subset)
        data = dataset['data']
        assert len(data) > 0
        print('Read %i %s data points.' % (len(data), subset))
        aggregate[subset] = data