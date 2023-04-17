"""
Cannabis Tests
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/10/2022
Updated: 9/16/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
import datasets
import pandas as pd


# === Constants. ===

_VERSION = '1.0.2'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_tests'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Cannabis lab test results (https://cannlytics.com/data/results) is a
dataset of curated cannabis lab test results.
"""
_CITATION = """\
@inproceedings{cannlytics2022cannabis_tests,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Tests: Curated Cannabis Lab Test Results},
  booktitle = {Cannabis Data Science},
  month     = {September},
  year      = {2022},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Raw Garden constants.
RAWGARDEN_URL = 'https://github.com/cannlytics/cannlytics/tree/main/ai/curation/get_rawgarden_data'
RAWGARDEN_DATA_URLS = {
    'rawgarden': 'https://cannlytics.page.link/?link=https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/data%252Flab_results%252Frawgarden%252Fdetails.csv?alt%3Dmedia%26token%3De5b5273a-049a-4092-98d7-90a62ef399a3',
    # 'rawgarden_details': 'https://cannlytics.page.link/?link=https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/data%252Flab_results%252Frawgarden%252Fdetails.csv?alt%3Dmedia%26token%3De5b5273a-049a-4092-98d7-90a62ef399a3',
    # 'rawgarden_results': 'https://cannlytics.page.link/?link=https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/data%252Flab_results%252Frawgarden%252Fresults.csv?alt%3Dmedia%26token%3Ddd868e72-edde-4278-9725-b33368a35d54',
    # 'rawgarden_values': 'https://cannlytics.page.link/?link=https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/data%252Flab_results%252Frawgarden%252Fvalues.csv?alt%3Dmedia%26token%3D5d427468-c33e-4e45-ae40-efd10fdca644',
}
RAWGARDEN_DESCRIPTION = """\
Raw Garden lab test results (https://cannlytics.com/data/tests) is a
dataset of curated cannabis lab test results from Raw Garden, a large
cannabis processor in California.
"""
RAWGARDEN_DETAILS = datasets.Features({
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
# RAWGARDEN_RESULTS = datasets.Features({
#     'sample_hash': datasets.Value(dtype='string'),
#     'results_hash': datasets.Value(dtype='string'),
#     'sample_id': datasets.Value(dtype='string'),
#     'product_name': datasets.Value(dtype='string'),
#     'producer': datasets.Value(dtype='string'),
#     'product_type': datasets.Value(dtype='string'),
#     'product_subtype': datasets.Value(dtype='string'),
#     'date_tested': datasets.Value(dtype='string'),
#     'analysis': datasets.Value(dtype='string'),
#     'key': datasets.Value(dtype='string'),
#     'limit': datasets.Value(dtype='double'),
#     'lod': datasets.Value(dtype='double'),
#     'lodloq': datasets.Value(dtype='double'),
#     'loq': datasets.Value(dtype='double'),
#     'margin_of_error': datasets.Value(dtype='double'),
#     'mg_g': datasets.Value(dtype='double'),
#     'name': datasets.Value(dtype='string'),
#     'status': datasets.Value(dtype='string'),
#     'units': datasets.Value(dtype='string'),
#     'value': datasets.Value(dtype='double'),
# })
# TODO: Determine standard values?
# RAWGARDEN_VALUES = datasets.Features({})


class CannabisTestsConfig(datasets.BuilderConfig):
    """BuilderConfig for Cannabis Tests."""

    def __init__(
            self,
            name,
            description,
            features,
            **kwargs
        ):
        """BuilderConfig for Cannabis Tests.
        Args:
            name (str): Configuration name that determines setup.
            description (str): A description for the configuration.
            **kwargs: Keyword arguments forwarded to super.
        """
        self.features = features
        super().__init__(
            name=name,
            description=description,
            **kwargs,
        )

class CannabisTests(datasets.GeneratorBasedBuilder):
    """The Cannabis Tests dataset."""

    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = CannabisTestsConfig
    DEFAULT_CONFIG_NAME = 'rawgarden'
    BUILDER_CONFIGS = [
        CannabisTestsConfig(
            name='rawgarden',
            description=RAWGARDEN_DESCRIPTION,
            features=RAWGARDEN_DETAILS,
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            features=self.config.features,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
            description=_DESCRIPTION,
            license=_LICENSE,
            version=_VERSION,
        )
    
    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # Future work: Make `urls` source-dynamic based on config,
        # i.e. allow for MCR Labs, SC Labs, etc.
        config_name = self.config.name
        urls = {config_name: RAWGARDEN_DATA_URLS[config_name]}
        downloaded_files = dl_manager.download_and_extract(urls)
        filepath = downloaded_files[config_name]
        return [
            datasets.SplitGenerator(
                name='details',
                gen_kwargs={'filepath': filepath},
            ),
            # Future work: Also return `results` and `values`?
        ]
    
    def _generate_examples(self, filepath):
        """This function returns the examples in the raw (text) form."""
        with open(filepath) as f:
            df = pd.read_csv(filepath)
            for index, row in df.iterrows():
                if self.config.name.endswith('results'):
                    _id = index
                else:
                    _id = row['sample_hash']
                obs = row.to_dict()
                yield _id, obs


# === Test ===
if __name__ == '__main__':

    from datasets import load_dataset

    # Download details.
    dataset = load_dataset('cannabis_tests.py', 'rawgarden')
    details = dataset['details']
    assert len(details) > 0
    print('Downloaded %i observations.' % len(details))
