"""
CCRS Module | Cannlytics
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/10/2022
Updated: 7/30/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import functools
from glob import glob
import logging
from pathlib import Path
import os
import tempfile
from typing import Callable, List, Optional, Union
from zipfile import ZipFile
import numpy as np

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data import create_hash
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYSES,
    CCRS_ANALYTES,
    CCRS_DATASETS,
    CCRS_PLANT_GROWTH_STAGES,
    CCRS_PLANT_HARVEST_CYCLES,
    CCRS_PLANTS_SOURCES,
    CCRS_PLANT_STATES,
    CURATED_CCRS_DATASETS,
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
    df.loc[:, columns] = df.loc[:, columns].astype(str).applymap(create_hash)
    return df


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
    # FIXME: There may be values that begin with an "=".
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


class CCRS(object):
    """An instance of this class manages CCRS data curation."""

    def __init__(self, data_dir='./', stats_dir='./', logs=True):
        """Initialize a CCRS API client.
        Args:
            logs (bool): Whether or not to log CCRS API requests, True by default.

        Example:

        ```py
        track = CCRS(logs=True)
        ```
        """
        self.data_dir = data_dir
        self.stats_dir = stats_dir
        self.inventory_dir = os.path.join(stats_dir, 'inventory')
        self.licensees = None
        self.fields = None
        self.date_fields = None
        self.item_cols = None
        self.item_types = None
        self.inventory_files = None
        self.product_files = None
        self.strain_files = None
        self.area_files = None
        self.logs = logs
        self.analyses = CCRS_ANALYSES
        self.analytes = CCRS_ANALYTES
        self.datasets = CCRS_DATASETS
        self.plant_growth_stages = CCRS_PLANT_GROWTH_STAGES
        self.plant_harvest_cycles = CCRS_PLANT_HARVEST_CYCLES
        self.plants_sources = CCRS_PLANTS_SOURCES
        self.plant_states = CCRS_PLANT_STATES
        self.curated_datasets = CURATED_CCRS_DATASETS
        self.anonymize = anonymize
        self.find_detections = find_detections
        self.format_lab_results = format_lab_results
        self.format_test_value = format_test_value
        self.get_datafiles = get_datafiles
        self.merge_datasets = merge_datasets
        self.save_dataset = save_dataset
        self.standardize_dataset = standardize_dataset
        self.unzip_datafiles = unzip_datafiles
        if logs:
            self.initialize_logs()


    def create_log(self, action):
        """Create a log given an HTTP response.
        Args:
            response (HTTPResponse): An HTTP request response.
        """
        try:
            self.logger.debug(str(action))
        except KeyError:
            raise ValueError({'message': '`logs=True` but no logger initialized. Use `client.initialize_logs()`.'})


    def initialize_logs(self):
        """Initialize CCRS logs."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'ccrs-{timestamp}.log')
        logging.getLogger('ccrs').handlers.clear()
        logging.basicConfig(
            filename=temp_file,
            filemode='w+',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger('ccrs')
        self.logger.addHandler(handler)
        self.logger.debug('CCRS data manager initialized.')


    # def format_test_value(self, tests, compound, value_key='TestValue'):
    #     """Format a lab result test value from a DataFrame of tests."""
    #     compound_value = self.extract_compound_value(tests, compound, value_key)
    #     return self.check_and_convert(compound_value)


    # def extract_compound_value(self, tests, compound, value_key):
    #     """Extract compound value from a set of tests."""
    #     compound_value = tests.loc[(tests.key == compound), value_key]
    #     return compound_value if not compound_value.empty else None


    # def check_and_convert(self, compound_value):
    #     """Check compound value and convert to numeric if not None."""
    #     if compound_value is not None:
    #         compound_value = to_numeric(compound_value.iloc[0], errors='coerce')
    #         if np.isnan(compound_value):
    #             return None
    #     return compound_value


    # def find_detections(self, tests, analysis, analysis_key='analysis', analyte_key='key', value_key='value'):
    #     """Find compounds detected for a given analysis from given tests."""
    #     if isinstance(tests, list):
    #         return [test[analyte_key] for test in tests if test[analysis_key] == analysis and to_numeric(test[value_key], errors='coerce') > 0]
    #     else:
    #         return self.find_detections_in_df(tests, analysis, analysis_key, analyte_key, value_key)


    # def find_detections_in_df(self, tests, analysis, analysis_key, analyte_key, value_key):
    #     """Find detections in a DataFrame."""
    #     tests = tests[tests[analysis_key] == analysis]
    #     tests[value_key] = to_numeric(tests[value_key], errors='coerce')
    #     return tests[tests[value_key] > 0][analyte_key].to_list()
