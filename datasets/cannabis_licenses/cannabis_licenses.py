"""
Cannabis Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/8/2022
License: <https://huggingface.co/datasets/cannlytics/cannabis_licenses/blob/main/LICENSE>
"""
# Standard imports.
import json

# External imports.
import datasets
import pandas as pd


# Constants.
_SCRIPT = 'cannabis_licenses.py'
_VERSION = '1.0.0'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_licenses'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Cannabis Licenses (https://cannlytics.com/data/licenses) is a
dataset of curated cannabis license data. The dataset consists of 18
sub-datasets for each state with permitted adult-use cannabis, as well
as a sub-dataset that includes all licenses.
"""
_CITATION = """\
@inproceedings{cannlytics2022cannabis_licenses,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Licenses},
  booktitle = {Cannabis Data Science},
  month     = {October},
  year      = {2022},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Dataset fields.
FIELDS = datasets.Features({
    'id': datasets.Value(dtype='string'),
    'license_number': datasets.Value(dtype='string'),
    'license_status': datasets.Value(dtype='string'),
    'license_status_date': datasets.Value(dtype='string'),
    'license_term': datasets.Value(dtype='string'),
    'license_type': datasets.Value(dtype='string'),
    'license_designation': datasets.Value(dtype='string'),
    'issue_date': datasets.Value(dtype='string'),
    'expiration_date': datasets.Value(dtype='string'),
    'licensing_authority_id': datasets.Value(dtype='string'),
    'licensing_authority': datasets.Value(dtype='string'),
    'business_legal_name': datasets.Value(dtype='string'),
    'business_dba_name': datasets.Value(dtype='string'),
    'business_image_url': datasets.Value(dtype='string'),
    'business_owner_name': datasets.Value(dtype='string'),
    'business_structure': datasets.Value(dtype='string'),
    'business_website': datasets.Value(dtype='string'),
    'activity': datasets.Value(dtype='string'),
    'premise_street_address': datasets.Value(dtype='string'),
    'premise_city': datasets.Value(dtype='string'),
    'premise_state': datasets.Value(dtype='string'),
    'premise_county': datasets.Value(dtype='string'),
    'premise_zip_code': datasets.Value(dtype='string'),
    'business_email': datasets.Value(dtype='string'),
    'business_phone': datasets.Value(dtype='string'),
    'parcel_number': datasets.Value(dtype='string'),
    'premise_latitude': datasets.Value(dtype='float'),
    'premise_longitude': datasets.Value(dtype='float'),
    'data_refreshed_date': datasets.Value(dtype='string'),
})

# DEV: Read subsets from local source.
# with open('cannabis_licenses.json', 'r') as f:
#     SUBSETS = json.loads(f.read())

# PRODUCTION: Read subsets from the official source.
import urllib.request
with urllib.request.urlopen('https://huggingface.co/datasets/cannlytics/cannabis_licenses/raw/main/cannabis_licenses.json') as url:
    SUBSETS = json.load(url)


class CannabisLicensesConfig(datasets.BuilderConfig):
    """BuilderConfig for Cannabis Licenses."""

    def __init__(self, name, **kwargs):
        """BuilderConfig for Cannabis Licenses.
        Args:
            name (str): Configuration name that determines setup.
            **kwargs: Keyword arguments forwarded to super.
        """
        description = _DESCRIPTION
        description += f'This configuration is for the `{name}` subset.'
        super().__init__(name=name, description=description, **kwargs)


class CannabisLicenses(datasets.GeneratorBasedBuilder):
    """The Cannabis Licenses dataset."""

    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = CannabisLicensesConfig
    BUILDER_CONFIGS = [CannabisLicensesConfig(s) for s in SUBSETS.keys()]
    DEFAULT_CONFIG_NAME = 'ca'

    def _info(self):
        """Returns the dataset metadata."""
        return datasets.DatasetInfo(
            features=FIELDS,
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


# === Test ===
if __name__ == '__main__':

    from datasets import load_dataset

    # Define all of the dataset subsets.
    subsets = list(SUBSETS.keys())

    # Load each dataset subset.
    for subset in subsets:
        dataset = load_dataset(_SCRIPT, subset)
        data = dataset['data']
        assert len(data) > 0
        print('Read %i %s data points.' % (len(data), subset))
