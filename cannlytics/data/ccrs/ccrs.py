"""
CCRS Module | Cannlytics
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/10/2022
Updated: 7/23/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import functools
from glob import glob
from pathlib import Path
import os
from typing import Callable, List, Optional, Union
from zipfile import ZipFile
import numpy as np

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data import create_hash
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils.utils import (
    camel_to_snake,
    rmerge,
    sorted_nicely,
)


# Cache the to_numeric function.
@functools.lru_cache
def to_numeric(val, errors: Optional[str] = 'coerce'):
    return pd.to_numeric(val, errors=errors)


def anonymize(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
    """Anonymize a CCRS dataset by creating a hash for fields that end
    in "_by" or "_By."""
    if columns is None:
        columns = df.filter(regex=r'.*_by$|.*_By$', axis=1).columns
    df.loc[:, columns] = df.loc[:, columns].astype(str).apply(create_hash)
    return df


# FIXME:
# def get_datafiles(
#         data_dir: str,
#         dataset: Optional[str] = '',
#         desc: Optional[bool] = True,
#         ext: Optional[str] = 'csv',
#     ) -> list:
#     """Get all CCRS datafiles of a given type in a directory."""
#     datafiles = sorted_nicely(glob(os.path.join(data_dir, dataset + f"*.{ext}")))
#     return datafiles[::-1] if desc else datafiles
def get_datafiles(
        data_dir: str,
        dataset: Optional[str] = '',
        desc: Optional[bool] = True,
    ) -> list:
    """Get all CCRS datafiles of a given type in a directory."""
    datafiles = sorted_nicely([
        os.path.join(data_dir, f, f, f + '.csv')
        for f in os.listdir(data_dir) if f.startswith(dataset)
    ])
    if desc:
        datafiles.reverse()
    return datafiles


def format_test_value(
        tests: pd.DataFrame,
        compound: str,
        value_key: str = 'TestValue',
    ) -> Union[float, None]:
    """Format a lab result test value from a DataFrame of tests."""
    compound_value = tests.loc[(tests.key == compound), value_key]
    if compound_value.empty:
        return None
    compound_value = to_numeric(compound_value.iloc[0], errors='coerce')
    if np.isnan(compound_value):
        return None
    return compound_value


# TODO: Determine fastest version of find_detections.
# def find_detections(
#         tests,
#         analysis,
#         analysis_key='analysis',
#         analyte_key='key',
#         value_key='value',
#     ) -> List[str]:
#     """Find compounds detected for a given analysis from given tests."""
#     tests = pd.DataFrame(tests)
#     analysis_tests = tests.loc[tests[analysis_key] == analysis]
#     if analysis_tests.empty:
#         return []
#     values = pd.to_numeric(analysis_tests[value_key], errors='coerce')
#     analysis_tests.loc[:, value_key] = values
#     detected = analysis_tests.loc[analysis_tests[value_key] > 0]
#     if detected.empty:
#         return []
#     return detected[analyte_key].to_list()


def find_detections(
        tests,
        analysis,
        analysis_key='analysis',
        analyte_key='key',
        value_key='value',
    ) -> List[str]:
    """Find compounds detected for a given analysis from given tests."""
    if isinstance(tests, list):
        return [test[analyte_key] for test in tests if test[analysis_key] == analysis and to_numeric(test[value_key], errors='coerce') > 0]
    tests = tests[tests[analysis_key] == analysis]
    tests[value_key] = to_numeric(tests[value_key], errors='coerce')
    return tests[tests[value_key] > 0][analyte_key].to_list()


# def format_lab_results(
#         df: pd.DataFrame,
#         results: pd.DataFrame,
#         item_key: Optional[str] = 'InventoryId',
#         analysis_name: Optional[str] = 'TestName',
#         analysis_key: Optional[str] = 'TestValue',
#     ) -> pd.DataFrame:
#     """Format CCRS lab results to merge into another dataset."""
#     analyte_data = results[analysis_name].map(CCRS_ANALYTES)
#     results = results.join(pd.DataFrame(analyte_data.values.tolist()))
#     results['type'] = results['type'].map(CCRS_ANALYSES)
#     item_ids = df[item_key].unique()
#     formatted = []
#     for item_id in item_ids:
#         item_results = results.loc[results[item_key] == item_id]
#         if item_results.empty:
#             continue
#         values = item_results.iloc[0].to_dict()
#         [values.pop(key, None) for key in [analysis_name, analysis_key]]
#         entry = {
#             **values,
#             'analyses': item_results['type'].unique().tolist(),
#             'delta_9_thc': format_test_value(item_results, 'delta_9_thc'),
#             'thca': format_test_value(item_results, 'thca'),
#             'total_thc': format_test_value(item_results, 'total_thc'),
#             'cbd': format_test_value(item_results, 'cbd'),
#             'cbda': format_test_value(item_results, 'cbda'),
#             'total_cbd': format_test_value(item_results, 'total_cbd'),
#             'moisture_content': format_test_value(item_results, 'moisture_content'),
#             'water_activity': format_test_value(item_results, 'water_activity'),
#             'status': 'Fail' if 'Fail' in item_results['LabTestStatus'].unique() else 'Pass',
#             'pesticides': find_detections(item_results, 'pesticides'),
#             'residual_solvents': find_detections(item_results, 'residual_solvent'),
#             'heavy_metals': find_detections(item_results, 'heavy_metals'),
#         }
#         formatted.append(entry)
#     return pd.DataFrame(formatted)


# TODO: Test if this function is faster.
def format_lab_results(df: pd.DataFrame, results: pd.DataFrame, item_key: Optional[str] = 'InventoryId',
                       analysis_name: Optional[str] = 'TestName', analysis_key: Optional[str] = 'TestValue') -> pd.DataFrame:
    """Format CCRS lab results to merge into another dataset."""
    # Curate lab results.
    analyte_data = results[analysis_name].map(CCRS_ANALYTES)
    results = pd.concat([results, pd.DataFrame(analyte_data)], axis=1)
    results['type'] = results['type'].map(CCRS_ANALYSES)

    # Find lab results for each item.
    item_results = results[results[item_key].astype(str).isin(df[item_key].unique())]
    if item_results.empty:
        return []

    # Map certain test values.
    entries = item_results.apply(lambda row: {
        **row.drop([analysis_name, analysis_key]),
        'analyses': list(item_results['type'].unique()),
        'delta_9_thc': format_test_value(item_results, 'delta_9_thc'),
        'thca': format_test_value(item_results, 'thca'),
        'total_thc': format_test_value(item_results, 'total_thc'),
        'cbd': format_test_value(item_results, 'cbd'),
        'cbda': format_test_value(item_results, 'cbda'),
        'total_cbd': format_test_value(item_results, 'total_cbd'),
        'moisture_content': format_test_value(item_results, 'moisture_content'),
        'water_activity': format_test_value(item_results, 'water_activity'),
        'status': 'Fail' if 'Fail' in item_results['LabTestStatus'].unique() else 'Pass',
        'pesticides': find_detections(item_results, 'pesticides'),
        'residual_solvents': find_detections(item_results, 'residual_solvent'),
        'heavy_metals': find_detections(item_results, 'heavy_metals')
    }, axis=1).tolist()

    # Return the lab results.
    return pd.DataFrame(entries)


def load_supplement_data(
        datafile: Path,
        dtype: dict,
        usecols: List[str],
        parse_dates: List[str],
        on_bad_lines: str,
        sep: str = '\t',
        encoding: str = 'utf-16',
        engine: str = 'python',
    ) -> pd.DataFrame:
    """Load supplement data from a specified data file."""
    return pd.read_csv(datafile,
                       sep=sep,
                       encoding=encoding,
                       engine=engine,
                       parse_dates=parse_dates,
                       dtype=dtype,
                       usecols=usecols,
                       on_bad_lines=on_bad_lines)


def preprocess_supplement(
        supplement: pd.DataFrame,
        on: str,
        rename: Optional[dict],
        drop: Optional[dict],
        dedupe: Optional[bool],
    ) -> pd.DataFrame:
    """Preprocess the supplement data."""
    if dedupe:
        supplement = supplement.drop_duplicates(subset=[on])
    if rename is not None:
        supplement = supplement.rename(rename, axis=1)
    if drop is not None:
        supplement = supplement.drop(drop, axis=1)
    return supplement


def merge_datasets(
        df: pd.DataFrame,
        datafiles: List[str],
        dataset: str,
        on: Optional[str] = 'id',
        target: Optional[str] = '',
        how: Optional[str] = 'left',
        sep: Optional[str] = '\t',
        validate: Optional[str] = 'm:1',
        dedupe: Optional[bool] = False,
        drop: Optional[dict] = None,
        rename: Optional[dict] = None,
        break_once_matched: Optional[bool] = True,
        on_bad_lines: Optional[str] = 'skip',
        string_columns: Optional[list] = [
            'IsDeleted', 'UnitWeightGrams',
            'TestValue', 'IsQuarantine'],
    ) -> pd.DataFrame:
    """
    Merge multiple datasets into a single DataFrame.

    Args:
        df: The initial DataFrame to merge onto.
        datafiles: A list of file paths containing the datasets to merge.
        dataset: The name of the dataset being merged.
        on: The column to merge on. Defaults to 'id'.
        target: The target column. Defaults to empty string.
        how: How to merge the dataframes. Defaults to 'left'.
        sep: The separator used in the data files. Defaults to '\t'.
        validate: Validate argument for pandas merge function. Defaults to 'm:1'.
        dedupe: Whether to drop duplicates. Defaults to False.
        drop: Columns to drop from the supplemental dataset. Defaults to None.
        rename: Columns to rename in the supplemental dataset. Defaults to None.
        break_once_matched: Whether to break after a match is found. Defaults to True.
        on_bad_lines: What to do when bad lines are encountered. Defaults to 'skip'.
        string_columns: Columns to force read as strings. Defaults to ['IsDeleted', 'UnitWeightGrams', 'TestValue', 'IsQuarantine'].

    Returns:
        A DataFrame that is the result of merging all datasets.
    """

    n = len(df)
    augmented = pd.DataFrame()
    fields = CCRS_DATASETS[dataset]['fields']
    parse_dates = CCRS_DATASETS[dataset]['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    for column in string_columns:
        if dtype.get(column):
            dtype[column] = 'string'
    for datafile in datafiles:
        datafile = Path(datafile)
        print(datafile) # TODO: replace with logging
        supplement = load_supplement_data(datafile, dtype, usecols, parse_dates, on_bad_lines, sep)
        supplement = preprocess_supplement(supplement, on, rename, drop, dedupe)
        if dataset == 'lab_results':
            supplement = format_lab_results(df, supplement)
        match = rmerge(df, supplement, on=on, how=how, validate=validate)
        matched = match.loc[~match[target].isna()]
        augmented = pd.concat([augmented, matched], ignore_index=True)
        if len(augmented) == n and break_once_matched:
            break
    return augmented


def save_dataset(
        data: pd.DataFrame,
        data_dir: str,
        name: str,
        ext: Optional[str] = 'xlsx',
        rows: Optional[int] = 1_000_000,
    ) -> None:
    """Save a curated dataset, determining the number of datafiles
    (1 million per file) and saving each shard of the dataset."""
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    num_files = -(-len(data) // rows) # equivalent to math.ceil(len(data) / rows)
    for i in range(num_files):
        data.iloc[i*rows : (i+1)*rows].to_excel(os.path.join(data_dir, f'{name}_{i}.{ext}'), index=False)


def standardize_dataset(
        df: pd.DataFrame,
        rename_function: Optional[Callable] = camel_to_snake,
    ) -> pd.DataFrame:
    """Standardize a given DataFrame."""
    df.rename(columns={col: rename_function(col) for col in df.columns}, inplace=True)
    return anonymize(df).sort_index(axis=1)


def unzip_datafiles(
        data_dir: str,
        verbose: Optional[bool] = True,
    ) -> None:
    """Unzip all CCRS datafiles in a given directory."""
    zip_files = [f for f in os.listdir(data_dir) if f.endswith('.zip')]
    for zip_file in zip_files:
        filename = os.path.join(data_dir, zip_file)
        zip_dest = filename.rstrip('.zip')
        os.makedirs(zip_dest, exist_ok=True)
        with ZipFile(filename) as zip_ref:
            zip_ref.extractall(zip_dest)
        os.remove(filename)
        if verbose:
            print('Unzipped:', zip_file)
