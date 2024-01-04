"""
Cannabis Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 9/30/2023
License: <https://huggingface.co/datasets/cannlytics/cannabis_licenses/blob/main/LICENSE>
"""
# External imports:
import datasets
import pandas as pd


# Constants.
_SCRIPT = 'cannabis_licenses.py'
_VERSION = '1.0.2'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_licenses'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Cannabis Licenses is a dataset of curated cannabis license data. The dataset consists of sub-datasets for each state with permitted adult-use cannabis, as well as a sub-dataset that includes all licenses.
"""
_CITATION = """\
@inproceedings{cannlytics2023cannabis_licenses,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Licenses},
  booktitle = {Cannabis Data Science},
  month     = {August},
  year      = {2023},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""


# Define subsets.
SUBSETS = [
    'all',
    'ak',
    'az',
    'ca',
    'co',
    'ct',
    'il',
    'ma',
    'md',
    'me',
    'mi',
    'mo',
    'mt',
    'nj',
    'nm',
    'ny',
    'nv',
    'or',
    'ri',
    'vt',
    'wa',
]


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
    'premise_latitude': datasets.Value(dtype='string'),
    'premise_longitude': datasets.Value(dtype='string'),
    'data_refreshed_date': datasets.Value(dtype='string'),
})


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
        super().__init__(
            data_dir='data',
            description=description,
            name=name,
            **kwargs,
        )


class CannabisLicenses(datasets.GeneratorBasedBuilder):
    """The Cannabis Licenses dataset."""

    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = CannabisLicensesConfig
    BUILDER_CONFIGS = [CannabisLicensesConfig(s) for s in SUBSETS]
    DEFAULT_CONFIG_NAME = 'all'

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
        subset = self.config.name
        data_url = f'data/{subset}/licenses-{subset}-latest.csv'
        urls = {subset: data_url}
        downloaded_files = dl_manager.download_and_extract(urls)
        params = {'filepath': downloaded_files[subset]}
        return [datasets.SplitGenerator(name='data', gen_kwargs=params)]
    
    def _generate_examples(self, filepath):
        """Returns the examples in raw text form."""
        # Read the data.
        df = pd.read_csv(filepath)

        # Add missing columns.
        for col in FIELDS.keys():
            if col not in df.columns:
                df[col] = ''

        # Keep only the feature columns.
        df = df[list(FIELDS.keys())]

        # Fill missing values.
        df.fillna('', inplace=True)

        # Return the data as a dictionary.
        for index, row in df.iterrows():
            obs = row.to_dict()
            yield index, obs


# === Test ===
# [✓] Tested: 2023-09-19 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    from datasets import load_dataset

    # Load each dataset subset.
    for subset in SUBSETS:
        dataset = load_dataset(_SCRIPT, subset)
        data = dataset['data']
        assert len(data) > 0
        print('Read %i %s data points.' % (len(data), subset))
