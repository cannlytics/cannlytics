"""
Cannabis Analytes
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 10/10/2023
Updated: 10/10/2023
License: <https://huggingface.co/datasets/cannlytics/cannabis_analytes/blob/main/LICENSE>
"""
# External imports:
import datasets
import pandas as pd

# Constants.
_SCRIPT = 'cannabis_analytes.py'
_VERSION = '2023.10.10'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_analytes'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
This dataset consists of analyte data for various analytes that are regularly tested for in cannabis. The dataset consists of sub-datasets for each type of test, as well as a sub-dataset that includes all analytes.
"""
_CITATION = """\
@inproceedings{cannlytics2023cannabis_analytes,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Analytes},
  booktitle = {Cannabis Data Science},
  month     = {October},
  year      = {2023},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Define subsets.
SUBSETS = [
    # 'all',
    'cannabinoids',
    'terpenes',
]

# Dataset fields.
FIELDS = datasets.Features({
    'description': datasets.Value(dtype='string'),
    'key': datasets.Value(dtype='string'),
    'name': datasets.Value(dtype='string'),
    'scientific_name': datasets.Value(dtype='string'),
    'type': datasets.Value(dtype='string'),
    'wikipedia_url': datasets.Value(dtype='string'),
    'degrades_to': datasets.Sequence(datasets.Value(dtype='string')),
    'precursors': datasets.Sequence(datasets.Value(dtype='string')),
    'subtype': datasets.Value(dtype='string'),
    'cas_number': datasets.Value(dtype='string'),
    'chemical_formula': datasets.Value(dtype='string'),
    'molar_mass': datasets.Value(dtype='string'),
    'density': datasets.Value(dtype='string'),
    'boiling_point': datasets.Value(dtype='string'),
    'image_url': datasets.Value(dtype='string'),
    'chemical_formula_image_url': datasets.Value(dtype='string'),
})


class CannabisAnalytesConfig(datasets.BuilderConfig):
    """BuilderConfig for the Cannabis Analytes dataset."""

    def __init__(self, name, **kwargs):
        """BuilderConfig for the Cannabis Analytes dataset.
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
    BUILDER_CONFIG_CLASS = CannabisAnalytesConfig
    BUILDER_CONFIGS = [CannabisAnalytesConfig(s) for s in SUBSETS]
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
        data_url = f'data/{subset}.json'
        urls = {subset: data_url}
        downloaded_files = dl_manager.download_and_extract(urls)
        params = {'filepath': downloaded_files[subset]}
        return [datasets.SplitGenerator(name='data', gen_kwargs=params)]

    def _generate_examples(self, filepath):
        """Returns the examples in raw text form."""
        # Read the data.
        df = pd.read_json(filepath)

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
# [✓] Tested: 2023-10-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    from datasets import load_dataset

    # Load each dataset subset.
    for subset in SUBSETS:
        dataset = load_dataset(_SCRIPT, subset)
        data = dataset['data']
        assert len(data) > 0
        print('Read %i %s data points.' % (len(data), subset))
