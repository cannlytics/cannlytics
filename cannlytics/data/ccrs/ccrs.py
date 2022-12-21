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

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils.utils import snake_case


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
