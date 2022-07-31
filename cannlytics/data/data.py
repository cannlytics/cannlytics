"""
Data Tools | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2022
Updated: 7/31/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Internal imports.
from hashlib import sha256
import hmac
import os
from typing import Optional

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.utils import rmerge
from cannlytics.utils.utils import snake_case

# === Constants ===
DATA_PROVIDER = 'cannlytics'
DATA_URL = 'https://cannlytics.com/api/data'

# Library of Cannlytics datasets.
CANNLYTICS_DATASETS = [
    'aggregated-cannabis-test-results'
]


# === Data collection tools. ===

# FIXME: Simply use Hugging Face's `datasets` package?
# from datasets import load_dataset
# dataset = load_dataset("cannlytics/aggregated-cannabis-test-results")

def download_dataset():
    """Download a specific dataset."""
    # TODO: Implement !
    raise NotImplementedError


def load_dataset():
    """Load a specific dataset."""
    # TODO: Implement !
    raise NotImplementedError


def list_datasets():
    """Get the Cannlytics data catalogue."""
    # TODO: Implement !
    raise NotImplementedError


# === Data aggregation tools. ===

def aggregate_datasets(
        directory: str,
        on: Optional[str] = 'sample_id',
        how: Optional[str] = 'left',
        replace: Optional[str] = 'right',
        reverse: Optional[bool] = True,
        concat=False
    ) -> pd.DataFrame:
    """Aggregate datasets. Leverages `rmerge` to combine
    each dataset in the given directory.
    Args:
        directory (string): Required dataset directory.
        on (string): The key to merge datasets, `sample_id` by default (optional).
        how (string): How to merge, `left` by default (optional).
        replace (string): How to replace, `right` by default (optional).
        reverse (bool): Whether to combine in reverse order, `True` by default (optional).
    Returns:
        (DataFrame): The aggregated data.
    """
    all_data = None
    files = os.listdir(directory)
    if reverse:
        files.reverse()
    for filename in files:
        datafile = os.path.join(directory, filename)
        try:
            data = pd.read_excel(datafile)
        except:
            continue
        if all_data is None:
            all_data = data
        else:
            if concat:
                all_data = pd.concat([all_data, data])
            else:
                all_data = rmerge(
                    all_data,
                    data,
                    on=on,
                    how=how,
                    replace=replace,
                )
    return all_data


# === Data cleaning tools. ===


# === Data augmentation tools. ===

def create_sample_id(private_key, public_key, salt='') -> str:
    """Create a hash to be used as a sample ID.
    The standard is to use:
        1. `private_key = producer`
        2. `public_key = product_name`
        3. `salt = date_tested`
    Args:
        private_key (str): A string to be used as the private key.
        public_key (str): A string to be used as the public key.
        salt (str): A string to be used as the salt, '' by default (optional).
    Returns:
        (str): A sample ID hash.
    """
    secret = bytes(private_key, 'UTF-8')
    message = snake_case(public_key) + snake_case(salt)
    sample_id = hmac.new(secret, message.encode(), sha256).hexdigest()
    return sample_id


# === Data analysis tools. ===

def shard_datasets(data, directory, count=10_000):
    """Shard a dataset for ease of use."""
    # TODO: Implement !
    raise NotImplementedError


if __name__ == '__main__':

    # === Tests ===

    # [ ] TEST: List all of the available datasets.
    print(list_datasets())

    # [ ] TEST: Load a dataset and print the first observation.
    dataset = load_dataset('aggregated-cannabis-test-results')
    print(dataset.iloc[0].to_dict())

    # [✓] TEST: `aggregate_datasets` with MCR Labs data.
    # data_dir = '../../../.datasets/lab_results/raw_data/mcr_labs'
    # data = aggregate_datasets(data_dir, concat=True)
    # subset = data.loc[~data['results'].isnull()]
    # subset.drop_duplicates(
    #     subset=['sample_id', 'total_cannabinoids'],
    #     keep='last',
    #     inplace=True
    # )
    # timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    # datafile = f'../../../.datasets/lab_results/mcr_labs_test_results-{timestamp}.xlsx'
    # subset.to_excel(datafile, sheet_name='mcr_labs_raw_data')
    # print('Aggregated %i samples.' % len(subset))

    # [✓] TEST: `aggregate_datasets` with PSI Labs data.
    # data_dir = '../../.datasets/lab_results/raw_data/psi_labs'
    # data = aggregate_datasets(data_dir)
    # subset = data.loc[~data['results'].isnull()]
    # subset.drop_duplicates(subset='sample_id', keep='first', inplace=True)
    # subset.to_excel('../../.datasets/lab_results/psi_labs_test_results.xlsx')

    # [✓] TEST: `aggregate_datasets` with SC Labs data.
    # data_dir = '../../.datasets/lab_results/raw_data/sc_labs'
    # data = aggregate_datasets(data_dir, concat=True)
    # subset = data.loc[~data['results'].isnull()]
    # subset.drop_duplicates(subset='sample_id', keep='first', inplace=True)
    # timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    # datafile = f'../../.datasets/lab_results/sc_labs_test_results-{timestamp}.xlsx'
    # subset.to_excel(datafile)
    # print(len(subset))
