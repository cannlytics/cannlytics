"""
CCRS Client | Cannlytics
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/10/2022
Updated: 12/21/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import csv
import os
from typing import List, Optional
from zipfile import ZipFile

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils.utils import (
    convert_to_numeric,
    rmerge,
    snake_case,
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
        augmented = pd.concat([augmented, matched]) 
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
    df = tests.loc[tests[analysis_key] == analysis]
    if df.empty:
        return []
    df.loc[:, value_key] = df[value_key].apply(convert_to_numeric)
    detected = df.loc[df[value_key] > 0]
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


class CCRS(object):
    """An instance of this class handles CCRS data."""

    def __init__(self, data_dir='C:\\data', test=True):
        """Initialize a CCRS client."""
        self.data_dir = data_dir
        self.state = 'WA'
        self.test = test


    def read_areas(self, data_dir=None, limit=None):
        """Read areas into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Areas_0', 'areas', data_dir, limit)


    def read_contacts(self, data_dir=None, limit=None):
        """Read contacts into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Contacts_0', 'contacts', data_dir, limit)


    def read_integrators(self, data_dir=None, limit=None):
        """Read integrators into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Integrator_0', 'integrators', data_dir, limit)


    def read_inventory(self, data_dir=None, limit=None):
        """Read inventory into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Inventory_0', 'inventory', data_dir, limit)


    def read_inventory_adjustments(self, data_dir=None, limit=None):
        """Read inventory adjustments into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('InventoryAdjustment_0', 'inventory_adjustments', data_dir, limit)


    def read_lab_results(self, data_dir=None, limit=None):
        """Read lab results into a well-formatted DataFrame,
        mapping analyses from `test_name` into `key`, `type`, `units`.
        Future work: Allow users to specify which fields to read.
        """
        data = self.read_data('LabResult_0', 'lab_results', data_dir, limit)
        parsed_analyses = data['test_name'].map(CCRS_ANALYTES).values.tolist()
        data = data.join(pd.DataFrame(parsed_analyses))
        data['type'] = data['type'].map(CCRS_ANALYSES)
        # TODO: Exclude any test lab results.
        return data


    def read_licensees(self, data_dir=None):
        """Read licensee data into a well-formatted DataFrame.
            1. If a row has a value in cell 22, shift 2 to the left,
            condensing column 4 to 3 and column 6 to 5.
            2. If a row has a value in cell 21, shift 1 to the left,
            condensing column 4 to 3.

        Future work: Allow users to specify which fields to read.
        """
        dataset = 'Licensee_0'
        if data_dir is None:
            data_dir = self.data_dir
        datafile = f'{data_dir}/{dataset}/{dataset}.csv'
        csv_list = []
        with open(datafile, 'r', encoding='latin1') as f:
            for line in csv.reader(f):
                csv_list.append(line)
        headers = csv_list[:1][0]
        raw_data = pd.DataFrame(csv_list[1:])
        csv_list = []
        # FIXME: Some rows are even longer due to addresses.
        for _, values in raw_data.iterrows():
            if values[22]:
                values[5] = values[5] + values[6]
                values[3] = values[3] + values[4]
                values.pop(6)
                values.pop(4)
            elif values[21]:
                values[3] = values[3] + values[4]
                values.pop(4)
            csv_list.append(values)
        data = pd.DataFrame(csv_list)
        data.columns = headers + [''] * (len(data.columns) - len(headers))
        data.drop('', axis=1, inplace=True)
        for key in CCRS_DATASETS['licensees']['date_fields']:
            data[key] = pd.to_datetime(data[key], errors='coerce')
        data.columns = [snake_case(x) for x in data.columns]
        # TODO: Clean names more elegantly?
        data['name'] = data['name'].str.title()
        data['dba'] = data['dba'].str.title()
        data['city'] = data['city'].str.title()
        data['county'] = data['county'].str.title()
        data['license_number'] = data['license_number'].str.strip()
        return data


    def read_plants(self, data_dir=None, limit=None):
        """Read plants into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Plant_0', 'plants', data_dir, limit)


    def read_plant_destructions(self, data_dir=None, limit=None):
        """Read plant destructions into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('PlantDestructions_0', 'plant_destructions', data_dir, limit)


    def read_products(self, data_dir=None, limit=None):
        """Read products into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Product_0', 'products', data_dir, limit)


    def read_sale_headers(self, data_dir=None, limit=None):
        """Read sale headers into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('SaleHeader_0', 'sale_headers', data_dir, limit)


    def read_sale_details(self, data_dir=None, limit=None):
        """Read sale headers into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('SalesDetail_0', 'sale_details', data_dir, limit)


    def read_strains(self, data_dir=None, limit=None):
        """Read strains into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        return self.read_data('Strains_0', 'strains', data_dir, limit)


    def read_transfers(self, data_dir=None, limit=None):
        """Read transfers into a well-formatted DataFrame.
        Future work: Allow users to specify which fields to read.
        """
        dataset = 'Transfers_0'
        if data_dir is None:
            data_dir = self.data_dir
        datafile = f'{data_dir}/{dataset}/{dataset}.xlsx'
        data = pd.read_excel(
            datafile,
            usecols=CCRS_DATASETS['transfers']['fields'],
            parse_dates=CCRS_DATASETS['transfers']['date_fields'],
            nrows=limit,
            skiprows=2,
        )
        data.columns = [snake_case(x) for x in data.columns]
        return data


    def read_data(self, datafile, dataset, data_dir=None, limit=None):
        """Read a dataset from local storage."""
        if data_dir is None:
            data_dir = self.data_dir
        if not datafile.endswith('.csv'):
            datafile += '.csv'
        # datafile = f'{data_dir}/{dataset}/{dataset}.csv'
        filename = os.path.join(data_dir, datafile)
        data = pd.read_csv(
            filename,
            low_memory=False,
            nrows=limit,
            parse_dates=CCRS_DATASETS[dataset]['date_fields'],
            usecols=CCRS_DATASETS[dataset]['fields'],
        )
        data.columns = [snake_case(x) for x in data.columns]
        return data
