"""
Data Tools | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2022
Updated: 9/8/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Internal imports.
from hashlib import sha256
import hmac
import json
import os
import re
from typing import Any, Optional

# External imports.
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd

# Internal imports.
from cannlytics.utils import rmerge
from cannlytics.utils.utils import snake_case

# Constants.
DATA_PROVIDER = 'cannlytics'
DATA_URL = 'https://cannlytics.com/api/data'
HASH_ERROR = """Unrecognized `public_key`. Expecting a str, list, dict,
int, bytes, or DataFrame."""

# Library of Cannlytics datasets.
CANNLYTICS_DATASETS = [
    'aggregated-cannabis-test-results',
]

# === Data collection tools. ===

def list_datasets() -> list:
    """Get the Cannlytics Hugging Face data catalogue.
    Returns:
        (list): A list of dataset names.
    """
    return CANNLYTICS_DATASETS


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

def find_first_value(
        string: str,
        breakpoints: Optional[list]=None,
    ) -> str:
    """Find the first value of a string, be it a digit, a 'ND', '<',
    or other specified breakpoints.
    Args:
        string (str): The string containing a value.
        breakpoints (list): A list of breakpoints (optional).
    Returns:
        (int): Returns the index of the first value.
    """
    if breakpoints is None:
        breakpoints = [' \d+', 'ND', '<']
    detects = []
    for breakpoint in breakpoints:
        try:
            detects.append(string.index(re.search(breakpoint, string).group()))
        except AttributeError:
            pass
    try:
        return min([x for x in detects if x])
    except ValueError:
        return None


def parse_data_block(div, tag='span') -> dict:
    """Parse an HTML data block into a dictionary.
    Args:
        div (bs4.element): An HTML element.
        tag (string): The type of tag that is repeated in the block.
    Returns:
        (dict): A dictionary of key and value pairs.
    """
    data = {}
    for el in div:
        try:
            label = el.find(tag).text
            value = el.text
            value = value.replace(label, '')
            value = value.replace('\n', '').strip()
            label = label.replace(':', '')
            data[snake_case(label)] = value
        except AttributeError:
            pass
    return data


# === Data augmentation tools. ===

def create_hash(
        public_key: Any,
        private_key: Optional[str] = 'cannlytics.eth',
    ) -> str:
    """Create a hash (HMAC-SHA256) that is unique to the provided data.
    Args:
        public_key (str): A string to be used as the public key.
        private_key (str): A string to be used as the private key,
            "cannlytics.eth" by default (optional).
    Returns:
        (str): A sample ID hash.
    References:
        - HMAC: Keyed-Hashing for Message Authentication
        URL: <https://www.ietf.org/rfc/rfc2104.txt>
        - What's the difference between HMAC-SHA256(key, data) and SHA256(key + data)
        URL: <https://security.stackexchange.com/questions/79577/whats-the-difference-between-hmac-sha256key-data-and-sha256key-data>
    """
    if isinstance(public_key, str) or isinstance(public_key, bytes):
        msg = public_key
    elif isinstance(public_key, list):
        msg = str(public_key)
    elif isinstance(public_key, dict):
        msg = json.dumps(public_key)
    elif isinstance(public_key, pd.DataFrame):
        msg = json.dumps(public_key.to_dict('records'))
    elif isinstance(public_key, pd.Series):
        msg = json.dumps(public_key.to_dict())
    elif isinstance(public_key, int) or isinstance(public_key, float):
        msg = str(public_key)
    else:
        raise ValueError(HASH_ERROR)
    try:
        msg = msg.encode()
    except AttributeError:
        pass
    return hmac.new(bytes(private_key, 'UTF-8'), msg, sha256).hexdigest()


def create_sample_id(private_key, public_key, salt='') -> str:
    """Create a hash to be used as a sample ID.
    The standard is to use:
        1. `private_key = results`
        2. `public_key = product_name`
        3. `salt = producer`
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

def random_sample(data, count=10_000):
    """Create a random sample of a given dataset."""
    # TODO: Implement !
    raise NotImplementedError


def shard_datasets(data, directory, count=10_000):
    """Shard a dataset for ease of use."""
    # TODO: Implement !
    raise NotImplementedError


# === Data saving tools. ===

def write_to_worksheet(ws, values):
    """Write data to an Excel Worksheet.
    Credit: Charlie Clark <https://stackoverflow.com/a/36664027>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    Args:
        ws (Worksheet) An openpyxl Worksheet.
        values (list): A list of values to print to the worksheet.
    """
    rows = dataframe_to_rows(pd.DataFrame(values), index=False)
    for r_idx, row in enumerate(rows, 1):
        for c_idx, value in enumerate(row, 1):
            try:
                ws.cell(row=r_idx, column=c_idx, value=value)
            except ValueError:
                ws.cell(row=r_idx, column=c_idx, value=str(value))


if __name__ == '__main__':

    # === Tests ===
    import cannlytics.data

    # [✓] TEST: List all of the available datasets.
    # dataset_names = list_datasets()
    # for name in dataset_names:
    #     assert name in CANNLYTICS_DATASETS

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
