"""
Curate CCRS Lab Results
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/1/2023
Updated: 1/15/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/plb3dr2fvsuvgixb38g10tbwqos73biz>

"""
# Standard imports:
from datetime import datetime
import gc
import os
from typing import Optional

# External imports:
from cannlytics.data.ccrs import (
    CCRS,
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
    anonymize,
    get_datafiles,
    find_detections,
    format_test_value,
    save_dataset,
    unzip_datafiles,
)
from cannlytics.utils import convert_to_numeric, camel_to_snake
import pandas as pd


def read_lab_results(
        data_dir: str,
        value_key: Optional[str] = 'TestValue',
    ) -> pd.DataFrame:
    """Read CCRS lab results."""
    lab_results = pd.DataFrame()
    lab_result_files = get_datafiles(data_dir, 'LabResult_')
    fields = CCRS_DATASETS['lab_results']['fields']
    parse_dates = CCRS_DATASETS['lab_results']['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    dtype[value_key] = 'string' # Hot-fix for `ValueError`.
    for datafile in lab_result_files:
        data = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            engine='python',
            parse_dates=parse_dates,
            dtype=dtype,
            usecols=usecols,
            on_bad_lines='skip',
            # DEV: Uncomment to make development quicker.
            # nrows=1000,
        )
        lab_results = pd.concat([lab_results, data])
    if 'TestValue' in lab_results.columns:
        lab_results[value_key] = lab_results[value_key].apply(convert_to_numeric)
    # lab_results = lab_results.assign(TestValue=values)
    return lab_results


def format_result(
        item_results,
        manager: Optional[CCRS] = None,
        drop: Optional[list] = []
    ) -> dict:
    """Format results for a lab sample."""

    # Skip items with no lab results.
    if item_results.empty:
        return None

    # Record item metadata and important results.
    item = item_results.iloc[0].to_dict()
    [item.pop(key) for key in drop]
    entry = {
        **item,
        'delta_9_thc': format_test_value(item_results, 'delta_9_thc'),
        'thca': format_test_value(item_results, 'thca'),
        'total_thc': format_test_value(item_results, 'total_thc'),
        'cbd': format_test_value(item_results, 'cbd'),
        'cbda': format_test_value(item_results, 'cbda'),
        'total_cbd': format_test_value(item_results, 'total_cbd'),
        'moisture_content': format_test_value(item_results, 'moisture_content'),
        'water_activity': format_test_value(item_results, 'water_activity'),
    }

    # Determine "Pass" or "Fail" status.
    statuses = list(item_results['LabTestStatus'].unique())
    if 'Fail' in statuses:
        entry['status'] = 'Fail'
    else:
        entry['status'] = 'Pass'

    # Augment the complete `results`.
    entry_results = []
    for _, item_result in item_results.iterrows():
        test_name = item_result['TestName']
        analyte = CCRS_ANALYTES[test_name]
        try:
            analysis = CCRS_ANALYSES[analyte['type']]
        except KeyError:
            if manager is not None:
                manager.create_log('Unidentified analysis: ' + str(analyte['type']))
            else:
                print('Unidentified analysis:', analyte['type'])
            analysis = analyte['type']
        entry_results.append({
            'analysis': analysis,
            'key': analyte['key'],
            'name': item_result['TestName'],
            'units': analyte['units'],
            'value': item_result['TestValue'],
        })
    entry['results'] = entry_results

    # Determine detected contaminants.
    entry['pesticides'] = find_detections(entry_results, 'pesticides')
    entry['residual_solvents'] = find_detections(entry_results, 'residual_solvents')
    entry['heavy_metals'] = find_detections(entry_results, 'heavy_metals')

    # Return the entry.
    return entry


def augment_lab_results(
        manager: CCRS,
        results: pd.DataFrame,
        item_key: Optional[str] = 'InventoryId',
        analysis_name: Optional[str] = 'TestName',
        analysis_key: Optional[str] = 'TestValue',
        verbose: Optional[str] = True,
    ) -> pd.DataFrame:
    """Format CCRS lab results to merge into another dataset."""

    # Handle `TestName`'s that are not in known analytes.
    results[analysis_name] = results[analysis_name].apply(
        lambda x: x.replace('Pesticides - ', '').replace(' (ppm) (ppm)', '')
    )

    # Map `TestName` to `type` and `key`.
    # Future work: Handle unidentified analyses. Ask ChatGPT?
    test_names = list(results[analysis_name].unique())
    known_analytes = list(CCRS_ANALYTES.keys())
    missing = list(set(test_names) - set(known_analytes))
    try:
        assert len(missing) == 0
        del test_names, known_analytes, missing
        gc.collect()
    except:
        manager.create_log('Unidentified analytes: ' + ', '.join(missing))
        raise ValueError(f'Unidentified analytes. Add missing analytes to `CCRS_ANALYTES`: {", ".join(missing)}')

    # Augment lab results with standard analyses and analyte keys.
    analyte_data = results[analysis_name].map(CCRS_ANALYTES).values.tolist()
    results = results.join(pd.DataFrame(analyte_data))
    results['type'] = results['type'].map(CCRS_ANALYSES)
    results[item_key] = results[item_key].astype(str)

    # Setup for iteration.    
    item_ids = list(results[item_key].unique())
    drop = [analysis_name, analysis_key, 'LabTestStatus', 'key', 'type', 'units']
    N = len(item_ids)
    if verbose:
        manager.create_log(f'Curating {N} items...')
        manager.create_log('Estimated runtime: ' + str(round(N * 0.00011, 2)) + ' minutes')

    # Return the curated lab results.
    group = results.groupby(item_key).apply(format_result, drop=drop, manager=manager).dropna()
    return pd.DataFrame(group.tolist())


def curate_ccrs_lab_results(
        manager: CCRS,
        data_dir: str,
        stats_dir: str
    ) -> pd.DataFrame:
    """Curate CCRS lab results."""

    # Start curating lab results.
    manager.create_log('Curating lab results...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(data_dir)

    # Read all lab results.
    lab_results = read_lab_results(data_dir)

    # Curate all lab results.
    lab_results = augment_lab_results(manager, lab_results)

    # Standardize the lab results.
    # TODO: Add producer
    columns = {
        'ExternalIdentifier': 'lab_id',
        'inventory_type': 'product_type',
        'test_date': 'date_tested',
    }
    lab_results.rename(columns=columns, inplace=True)

    # Anonymize the data.
    lab_results = anonymize(lab_results)

    # Standardize the column names.
    lab_results.rename(columns=lambda x: camel_to_snake(x), inplace=True)

    # Save the curated lab results.
    # TODO: Save a copy as `wa-lab-results-latest.csv` in the `data` directory.
    timestamp = lab_results['created_date'].max().strftime('%Y-%m-%d')
    lab_results_dir = os.path.join(stats_dir, 'lab_results')
    outfile = save_dataset(lab_results, lab_results_dir, f'wa-lab-results-{timestamp}')
    manager.create_log('Saved lab results: ' + str(outfile))

    # Finish curating lab results.
    end = datetime.now()
    manager.create_log('✓ Finished curating lab results in ' + str(end - start))
    return lab_results


# === Test ===
# [✓] Tested: 2024-01-15 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Debug variables.
    item_key = 'InventoryId'
    analysis_name = 'TestName'
    analysis_key = 'TestValue'
    value_key = 'TestValue'
    verbose = True
    drop = []

    # Initialize.
    base = 'D://data/washington/'
    stats_dir = 'D://data/washington/stats'
    manager = CCRS()

    # Curate lab results for each release.
    releases = [
        'CCRS PRR (4-4-23)',
        'CCRS PRR (5-7-23)',
        'CCRS PRR (6-6-23)',
        'CCRS PRR (8-4-23)',
        'CCRS PRR (9-5-23)',
        'CCRS PRR (11-2-23)',
        'CCRS PRR (12-2-23)',
    ]
    for release in releases:
        data_dir = os.path.join(base, release, release)
        lab_results = curate_ccrs_lab_results(manager, data_dir, stats_dir)
        manager.create_log('Curated %i WA lab results.' % len(lab_results))

    # Aggregate lab results.
    all_results = []
    datafiles = os.listdir(os.path.join(stats_dir, 'lab_results'))
    datafiles = [os.path.join(stats_dir, 'lab_results', x) for x in datafiles if \
                  not x.startswith('~') and \
                  not 'aggregate' in x and \
                  not 'inventory' in x]
    for datafile in datafiles:
        data = pd.read_excel(datafile)
        all_results.append(data)
    results = pd.concat(all_results)
    results.drop_duplicates(subset=['lab_result_id', 'updated_date'], inplace=True)
    results.sort_values(by=['created_date'], inplace=True)
    print('Number of results:', len(results))
    outfile = os.path.join(stats_dir, 'lab_results', 'wa-lab-results-aggregate.xlsx')
    results.to_excel(outfile, index=False)
    manager.log('Saved aggregate lab results to: ' + outfile)
