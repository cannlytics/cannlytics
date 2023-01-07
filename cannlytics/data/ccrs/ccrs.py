"""
CCRS Module | Cannlytics
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/10/2022
Updated: 1/7/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import os
from typing import List, Optional
from zipfile import ZipFile

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
    convert_to_numeric,
    rmerge,
    sorted_nicely,
)


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


def unzip_datafiles(
        data_dir: str,
        verbose: Optional[bool] = True,
    ) -> None:
    """Unzip all CCRS datafiles in a given directory."""
    zip_files = [f for f in os.listdir(data_dir) if f.endswith('.zip')]
    for zip_file in zip_files:
        filename = os.path.join(data_dir, zip_file)
        zip_dest = filename.rstrip('.zip')
        if not os.path.exists(zip_dest):
            os.makedirs(zip_dest)
        zip_ref = ZipFile(filename)
        zip_ref.extractall(zip_dest)
        zip_ref.close()
        os.remove(filename)
        if verbose:
            print('Unzipped:', zip_file)


def merge_datasets(
        df: pd.DataFrame,
        datafiles: List[str],
        dataset: str,
        on: Optional[str] = 'id',
        target: Optional[str] = '',
        how: Optional[str] = 'left',
        sep: Optional[str] = '\t',
        validate: Optional[str] = 'm:1',
        drop: Optional[dict] = None,
        rename: Optional[dict] = None,
        on_bad_lines: Optional[str] = 'skip',
    ) -> pd.DataFrame:
    """Merge a supplemental CCRS dataset to an existing dataset.
    Note: `IsDeleted` and `UnitWeightGrams` are treated as strings.
    Lab results cannot be split between datafiles.
    """
    n = len(df)
    augmented = pd.DataFrame()
    fields = CCRS_DATASETS[dataset]['fields']
    parse_dates = CCRS_DATASETS[dataset]['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    # FIXME: These fields throw `ValueError` if not strings.
    if dtype.get('IsDeleted'):
        dtype['IsDeleted'] = 'string'
    if dtype.get('UnitWeightGrams'):
        dtype['UnitWeightGrams'] = 'string'
    if dtype.get('TestValue'):
        dtype['TestValue'] = 'string'
    for datafile in datafiles:
        supplement = pd.read_csv(
            datafile,
            sep=sep,
            encoding='utf-16',
            engine='python',
            parse_dates=parse_dates,
            dtype=dtype,
            usecols=usecols,
            on_bad_lines=on_bad_lines,
        )
        if rename is not None:
            supplement.rename(rename, axis=1, inplace=True)
        if drop is not None:
            supplement.drop(drop, axis=1, inplace=True)
        # FIXME: Handle lab results that may be split between datafiles.
        if dataset == 'lab_results':
            supplement = format_lab_results(df, supplement)
        match = rmerge(
            df,
            supplement,
            on=on,
            how=how,
            validate=validate,
        )
        matched = match.loc[~match[target].isna()]
        augmented = pd.concat([augmented, matched], ignore_index=True) 
        if len(augmented) == n:
            break
    return augmented


def format_test_value(tests, compound, value_key='TestValue'):
    """Format a lab result test value from a DataFrame of tests."""
    value = tests.loc[(tests.key == compound)]
    try:
        return convert_to_numeric(value.iloc[0][value_key])
    except:
        return None


def find_detections(
        tests,
        analysis,
        analysis_key='type',
        analyte_key='key',
        value_key='TestValue',
    ) -> List[str]:
    """Find compounds detected for a given analysis from given tests."""
    analysis_tests = tests.loc[tests[analysis_key] == analysis]
    if analysis_tests.empty:
        return []
    values = analysis_tests[value_key].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    analysis_tests = analysis_tests.assign(**{value_key: values})
    detected = analysis_tests.loc[analysis_tests[value_key] > 0]
    if detected.empty:
        return []
    return detected[analyte_key].to_list()


def format_lab_results(
        df: pd.DataFrame,
        results: pd.DataFrame,
        item_key: Optional[str] = 'InventoryId',
        analysis_name: Optional[str] = 'TestName',
        analysis_key: Optional[str] = 'TestValue',
    ) -> pd.DataFrame:
    """Format CCRS lab results to merge into another dataset."""

    # Curate lab results.
    analyte_data = results[analysis_name].map(CCRS_ANALYTES).values.tolist()
    results = results.join(pd.DataFrame(analyte_data))
    results['type'] = results['type'].map(CCRS_ANALYSES)

    # Find lab results for each item.
    formatted = []
    item_ids = list(df[item_key].unique())
    for item_id in item_ids:
        item_results = results.loc[results[item_key].astype(str) == item_id]
        if item_results.empty:
            continue

        # Map certain test values.
        values = item_results.iloc[0].to_dict()
        [values.pop(key) for key in [analysis_name, analysis_key]]
        entry = {
            **values,
            'analyses': list(item_results['type'].unique()),
            'delta_9_thc': format_test_value(item_results, 'delta_9_thc'),
            'thca': format_test_value(item_results, 'thca'),
            'total_thc': format_test_value(item_results, 'total_thc'),
            'cbd': format_test_value(item_results, 'cbd'),
            'cbda': format_test_value(item_results, 'cbda'),
            'total_cbd': format_test_value(item_results, 'total_cbd'),
            'moisture_content': format_test_value(item_results, 'moisture_content'),
            'water_activity': format_test_value(item_results, 'water_activity'),
        }

        # Determine `status`.
        statuses = list(item_results['LabTestStatus'].unique())
        if 'Fail' in statuses:
            entry['status'] = 'Fail'
        else:
            entry['status'] = 'Pass'

        # Determine detected contaminants.
        entry['pesticides'] = find_detections(item_results, 'pesticides')
        entry['residual_solvents'] = find_detections(item_results, 'residual_solvent')
        entry['heavy_metals'] = find_detections(item_results, 'heavy_metals')

        # Record the lab results for the item.
        formatted.append(entry)

    # Return the lab results.
    return pd.DataFrame(formatted)


def anonymize(
        df: pd.DataFrame,
        columns: Optional[List[str]] = ['CreatedBy', 'UpdatedBy'],
    ) -> pd.DataFrame:
    """Anonymize a CCRS dataset."""
    for column in columns:
        df.loc[:, column] = df[column].astype(str).apply(create_hash)
    return df


def save_dataset(
        data: pd.DataFrame,
        data_dir: str,
        name: str,
        ext: Optional[str] = 'xlsx',
        rows: Optional[float] = 1e6,
    ) -> None:
    """Save a curated dataset, determining the number of datafiles
    (1 million per file) and saving each shard of the dataset."""
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    file_count = round((len(data) + rows) / rows)
    for i in range(0, file_count):
        start = int(0 + rows * i)
        stop = int(rows + rows * i)
        shard = data.iloc[start: stop, :]
        outfile = os.path.join(data_dir, f'{name}_{i}.{ext}')
        shard.to_excel(outfile, index=False)
