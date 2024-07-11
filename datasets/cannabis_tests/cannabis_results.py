"""
Cannabis Tests
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/10/2022
Updated: 7/10/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# External imports:
import json
import datasets
import numpy as np
import pandas as pd

# Define constants.
_SCRIPT = 'cannabis_results.py'
_VERSION = '2024.07.10'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/cannabis_results'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Cannabis results is a dataset of curated cannabis lab test results. The dataset consists of sub-datasets for each state with any public cannabis lab tests, as well as a sub-dataset that includes all results.
"""
_CITATION = """\
@inproceedings{cannlytics2024cannabis_results,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Cannabis Results},
  month     = {July},
  year      = {2024},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Define subsets.
SUBSETS = [
    # 'all',
    # 'ak',
    # 'ca',
    # 'ct',
    # 'fl',
    'hi',
    # 'ma',
    # 'md',
    # 'mi',
    # 'nv',
    # 'ny',
    # 'or',
    # 'ri',
    'ut',
    # 'wa',
]

# Define fields that should be mapped to features.
FIELD_TO_FEATURE_MAP = {
    'business_dba_name': 'producer_dba_name',
    'business_image_url': 'producer_image_url',
    'business_legal_name': 'producer_legal_name',
    'business_owner_name': 'producer_owner_name',
    'business_phone': 'producer_phone',
    'business_structure': 'producer_structure',
    'business_website': 'producer_website',
    'producer_street_address': 'producer_street',
}

class CannabisTestsConfig(datasets.BuilderConfig):
    """BuilderConfig for Cannabis Tests."""

    def __init__(self, name, **kwargs):
        """BuilderConfig for Cannabis Tests."""
        description = _DESCRIPTION
        description += f'This configuration is for the `{name}` subset.'
        super().__init__(
            data_dir='./data',
            description=description,
            name=name,
            **kwargs,
        )

class CannabisTests(datasets.GeneratorBasedBuilder):
    """The Cannabis Tests dataset."""

    # Parameters.
    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = CannabisTestsConfig
    BUILDER_CONFIGS = [CannabisTestsConfig(s) for s in SUBSETS]
    DEFAULT_CONFIG_NAME = 'all'

    def get_features(self):
        """Load subset features from a JSON file."""
        subset = self.config.name
        with open('features.json', 'r') as f:
            feature_data = json.load(f)
        features = {k: datasets.Value(dtype=v) for k, v in feature_data[subset].items()}
        return datasets.Features(features)

    def _info(self):
        """Returns the dataset metadata."""
        features = self.get_features()
        return datasets.DatasetInfo(
            features=features,
            homepage=_HOMEPAGE,
            citation=_CITATION,
            description=_DESCRIPTION,
            license=_LICENSE,
            version=_VERSION,
            supervised_keys=None,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        subset = self.config.name
        try:
            data_url = f'./data/{subset}/{subset}-results-latest.csv'
            downloaded_files = dl_manager.download_and_extract({subset: data_url})
        except:
            data_url = f'./data/{subset}/{subset}-results-latest.xlsx'
            downloaded_files = dl_manager.download_and_extract({subset: data_url})
        params = {'filepath': downloaded_files[subset]}
        return [datasets.SplitGenerator(name='data', gen_kwargs=params)]

    def _generate_examples(self, filepath):
        """Returns the examples in raw text form."""
        print('Reading file:', filepath)
        try:
            df = pd.read_csv(filepath)
        except:
            df = pd.read_excel(filepath.replace('.csv', '.xlsx'))

        # Rename columns.
        df = df.rename(columns=FIELD_TO_FEATURE_MAP)

        # Add missing columns with appropriate defaults based on type.
        features = self.get_features()
        for col, feature in features.items():
            dtype = feature.dtype
            if col not in df.columns:
                if dtype == 'string':
                    df[col] = ''
                else:
                    df[col] = np.nan

        # Keep only the feature columns.
        df = df[list(features.keys())]

        # Optional: Fill missing values.
        # df.fillna(np.nan, inplace=True)

        # Get the features we want to keep.
        for index, row in df.iterrows():

            # Get observation features.
            keys = features.keys()
            obs = {}
            
            # Populate our structure with values from the row wherever available.
            for key in keys:
                # Convert the value to the appropriate type
                dtype = features[key].dtype
                value = row[key]
                
                # If the type is a string, ensure it's a string. For other types, use the corresponding conversion.
                if dtype == 'string':
                    obs[key] = str(value)
                elif dtype == 'float64':
                    try:
                        obs[key] = float(value)
                    except ValueError:
                        obs[key] = np.nan
                elif dtype == 'int64':
                    try:
                        obs[key] = int(value)
                    except ValueError:
                        obs[key] = np.nan
                else:
                    obs[key] = value

            # Yield the index and observation.
            yield index, obs


# === Tests ===
# [ ] Tested: 2024-07-09 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    from datasets import load_dataset

    # Load each dataset subset.
    for subset in SUBSETS:
        # try:
        dataset = load_dataset(_SCRIPT, subset)
        data = dataset['data']
        assert len(data) > 0
        print('Read %i %s data points.' % (len(data), subset))
        # except Exception as e:
        #     print(e)
        #     print('Failed to load subset:', subset)
