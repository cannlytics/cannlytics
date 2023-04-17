"""
Washington Cannabis Data
Copyright (c) 2022-2023 Cannlytics
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/7/2023
Updated: 4/16/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Original author: Cannabis Data
Original license: MIT <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB PRR (latest)
    URL: <https://lcb.app.box.com/s/l9rtua9132sqs63qnbtbw13n40by0yml>

Command-line Usage:

    python tools/ccrs/curate_ccrs.py

"""
# Standard imports.
import json

# External imports.
import datasets
import pandas as pd


# Constants.
_SCRIPT = 'washington_cannabis_data.py'
_VERSION = '1.0.0'
_HOMEPAGE = 'https://huggingface.co/datasets/cannlytics/washington_cannabis_data'
_LICENSE = "https://opendatacommons.org/licenses/by/4-0/"
_DESCRIPTION = """\
Washington Cannabis Data is a dataset of curated Washington Sate
cannabis data. The dataset consists of sub-datasets for each main type
of cannabis data, segmented by time.
"""
_CITATION = """\
@inproceedings{cannlytics2023washington_cannabis_data,
  author    = {Skeate, Keegan and O'Sullivan-Sutherland, Candace},
  title     = {Washington Cannabis Data},
  booktitle = {Cannabis Data Science},
  month     = {April},
  year      = {2023},
  address   = {United States of America},
  publisher = {Cannlytics}
}
"""

# Fields for each dataset.
# TODO: Review and standardize.
areas_features = datasets.Features({
    'area_id': datasets.Value(dtype='string'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'is_quarantine': datasets.Value(dtype='bool'),
    'licensee_id': datasets.Value(dtype='string'),
    'name': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
contacts_features = datasets.Features({
    'contact_id': datasets.Value(dtype='string'),
    'licensee_id': datasets.Value(dtype='string'),
    'integrator_id': datasets.Value(dtype='string'),
    'first_name': datasets.Value(dtype='string'),
    'middle_initial': datasets.Value(dtype='string'),
    'last_name': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
    'is_admin': datasets.Value(dtype='bool'),
})
integrators_features = datasets.Features({
    'integrator_id': datasets.Value(dtype='string'),
    'name': datasets.Value(dtype='string'),
    'is_active': datasets.Value(dtype='bool'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
inventory_features = datasets.Features({
    'licensee_id': datasets.Value(dtype='string'),
    'inventory_id': datasets.Value(dtype='string'),
    'strain_id': datasets.Value(dtype='string'),
    'area_id': datasets.Value(dtype='string'),
    'product_id': datasets.Value(dtype='string'),
    'inventory_identifier': datasets.Value(dtype='string'),
    'initial_quantity': datasets.Value(dtype='float32'),
    'quantity_on_hand': datasets.Value(dtype='float32'),
    'total_cost': datasets.Value(dtype='float32'),
    'is_medical': datasets.Value(dtype='bool'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
inventory_adjustments_features = datasets.Features({
    'inventory_adjustment_id': datasets.Value(dtype='string'),
    'inventory_id': datasets.Value(dtype='string'),
    'inventory_adjustment_reason': datasets.Value(dtype='string'),
    'adjustment_detail': datasets.Value(dtype='string'),
    'quantity': datasets.Value(dtype='float32'),
    'adjustment_date': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
inventory_plant_transfers_features = datasets.Features({
    'inventory_plant_transfer_id': datasets.Value(dtype='string'),
    'inventory_transfer_id': datasets.Value(dtype='string'),
    'plant_transfer_id': datasets.Value(dtype='string'),
    'from_licensee_id': datasets.Value(dtype='string'),
    'to_licensee_id': datasets.Value(dtype='string'),
    'from_inventory_id': datasets.Value(dtype='string'),
    'to_inventory_id': datasets.Value(dtype='string'),
    'from_plant_id': datasets.Value(dtype='string'),
    'to_plant_id': datasets.Value(dtype='string'),
    'quantity': datasets.Value(dtype='float32'),
    'transfer_date': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
lab_results_features = datasets.Features({
    'lab_result_id': datasets.Value(dtype='string'),
    'lab_licensee_id': datasets.Value(dtype='string'),
    'licensee_id': datasets.Value(dtype='string'),
    'lab_test_status': datasets.Value(dtype='string'),
    'inventory_id': datasets.Value(dtype='string'),
    'test_name': datasets.Value(dtype='string'),
    'test_date': datasets.Value(dtype='string'),
    'test_value': datasets.Value(dtype='float32'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='string'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
licensees_features = datasets.Features({
    'licensee_id': datasets.Value(dtype='string'),
    'license_status': datasets.Value(dtype='string'),
    'ubi': datasets.Value(dtype='string'),
    'license_number': datasets.Value(dtype='string'),
    'name': datasets.Value(dtype='string'),
    'dba': datasets.Value(dtype='string'),
    'license_issue_date': datasets.Value(dtype='string'),
    'license_expiration_date': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'address1': datasets.Value(dtype='string'),
    'address2': datasets.Value(dtype='string'),
    'city': datasets.Value(dtype='string'),
    'state': datasets.Value(dtype='string'),
    'zip_code': datasets.Value(dtype='string'),
    'county': datasets.Value(dtype='string'),
    'email_address': datasets.Value(dtype='string'),
    'phone_number': datasets.Value(dtype='string'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
plants_features = datasets.Features({
    'plant_id': datasets.Value(dtype='string'),
    'licensee_id': datasets.Value(dtype='string'),
    'area_id': datasets.Value(dtype='string'),
    'strain_id': datasets.Value(dtype='string'),
    'plant_source': datasets.Value(dtype='string'),
    'plant_state': datasets.Value(dtype='string'),
    'growth_stage': datasets.Value(dtype='string'),
    'harvest_cycle': datasets.Value(dtype='string'),
    'mother_plant_id': datasets.Value(dtype='string'),
    'plant_identifier': datasets.Value(dtype='string'),
    'harvest_date': datasets.Value(dtype='string'),
    'is_mother_plant': datasets.Value(dtype='bool'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
plant_destructions_features = datasets.Features({
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'destruction_date': datasets.Value(dtype='string'),
    'destruction_method': datasets.Value(dtype='string'),
    'destruction_reason': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'plant_destruction_id': datasets.Value(dtype='string'),
    'plant_id': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
products_features = datasets.Features({
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'description': datasets.Value(dtype='string'),
    'external_identifier': datasets.Value(dtype='string'),
    'inventory_type': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'licensee_id': datasets.Value(dtype='string'),
    'name': datasets.Value(dtype='string'),
    'product_id': datasets.Value(dtype='string'),
    'unit_weight_grams': datasets.Value(dtype='float'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
sale_features = datasets.Features({
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'discount': datasets.Value(dtype='float'),
    'external_identifier': datasets.Value(dtype='string'),
    'inventory_id': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'licensee_id': datasets.Value(dtype='string'),
    'other_tax': datasets.Value(dtype='float'),
    'plant_id': datasets.Value(dtype='string'),
    'quantity': datasets.Value(dtype='float'),
    'sale_date': datasets.Value(dtype='string'),
    'sale_detail_id': datasets.Value(dtype='string'),
    'sale_header_id': datasets.Value(dtype='string'),
    'sale_type': datasets.Value(dtype='string'),
    'sales_tax': datasets.Value(dtype='float'),
    'sold_to_licensee_id': datasets.Value(dtype='string'),
    'unit_price': datasets.Value(dtype='float'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
strain_features = datasets.Features({
    'created_by': datasets.Value(dtype='string'),
    'created_date': datasets.Value(dtype='string'),
    'is_deleted': datasets.Value(dtype='bool'),
    'name': datasets.Value(dtype='string'),
    'strain_id': datasets.Value(dtype='string'),
    'strain_type': datasets.Value(dtype='string'),
    'updated_by': datasets.Value(dtype='string'),
    'updated_date': datasets.Value(dtype='string'),
})
transfer_features = datasets.Features({
    'arrival_date': datasets.Value(dtype='string'),
    'completed_time': datasets.Value(dtype='string'),
    'departure_date': datasets.Value(dtype='string'),
    'destination_license_address': datasets.Value(dtype='string'),
    'destination_license_email': datasets.Value(dtype='string'),
    'destination_license_name': datasets.Value(dtype='string'),
    'destination_license_number': datasets.Value(dtype='string'),
    'destination_license_phone': datasets.Value(dtype='string'),
    'draft': datasets.Value(dtype='int32'),
    'estimated_arrival_time': datasets.Value(dtype='string'),
    'estimated_departure_time': datasets.Value(dtype='string'),
    'items_shipped': datasets.Value(dtype='string'),
    'modified_time': datasets.Value(dtype='string'),
    'origin_license_address': datasets.Value(dtype='string'),
    'origin_license_email': datasets.Value(dtype='string'),
    'origin_license_number': datasets.Value(dtype='string'),
    'origin_license_phone': datasets.Value(dtype='string'),
    'origin_trade_name': datasets.Value(dtype='string'),
    'scheduled_transportation_date': datasets.Value(dtype='string'),
    'serial': datasets.Value(dtype='string'),
    'sid': datasets.Value(dtype='string'),
    'submitted_time': datasets.Value(dtype='string'),
    'transportation_type': datasets.Value(dtype='string'),
    'ubi_number': datasets.Value(dtype='string'),
    'uid': datasets.Value(dtype='string'),
    'username': datasets.Value(dtype='string'),
})

# DEV: Read subsets from local source.
with open('subsets.json', 'r') as f:
    SUBSETS = json.loads(f.read())

# PRODUCTION: Read subsets from the official source.
# import urllib.request
# with urllib.request.urlopen('https://huggingface.co/datasets/cannlytics/cannabis_licenses/raw/main/subsets.json') as url:
#     SUBSETS = json.load(url)


class WashingtonCannabisDataConfig(datasets.BuilderConfig):
    """BuilderConfig for Washington Cannabis Data."""

    def __init__(self, name, description, features, **kwargs):
        """BuilderConfig for Washington Cannabis Data.
        Args:
            name (str): Configuration name that determines setup.
            **kwargs: Keyword arguments forwarded to super.
        """
        self.features = features
        super().__init__(name=name, description=description, **kwargs)


class WashingtonCannabisData(datasets.GeneratorBasedBuilder):
    """The Washington Cannabis Data dataset."""

    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIG_CLASS = WashingtonCannabisDataConfig
    BUILDER_CONFIGS = [WashingtonCannabisDataConfig(s) for s in SUBSETS.keys()]
    DEFAULT_CONFIG_NAME = 'ca'

    def _info(self):
        """Returns the dataset metadata."""
        return datasets.DatasetInfo(
            features=self.config.features,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
            description=self.config.description,
            license=_LICENSE,
            version=_VERSION,
        )
    
    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        config_name = self.config.name
        data_url = SUBSETS[config_name]['data_url']
        urls = {config_name: data_url}
        downloaded_files = dl_manager.download_and_extract(urls)
        filepath = downloaded_files[config_name]
        params = {'filepath': filepath}
        return [datasets.SplitGenerator(name='data', gen_kwargs=params)]
    
    def _generate_examples(self, filepath):
        """Returns the examples in raw text form."""
        with open(filepath) as f:
            df = pd.read_csv(filepath)
            for index, row in df.iterrows():
                obs = row.to_dict()
                yield index, obs


# === Test ===
if __name__ == '__main__':

    from datasets import load_dataset

    # Download data.
    dataset = load_dataset('washington_cannabis_data.py', 'strains')
    data = dataset['data']
    assert len(data) > 0
    print('Downloaded %i observations.' % len(data))


# FIXME: Standardize collection.

# # Internal imports:
# from curate_ccrs_lab_results import curate_ccrs_lab_results
# from curate_ccrs_inventory import curate_ccrs_inventory
# from curate_ccrs_sales import curate_ccrs_sales
# from curate_ccrs_strains import curate_ccrs_strains


# # === Test ===
# if __name__ == '__main__':

#     # Specify the date of the public records request.
#     DATE = '3-6-23'

#     # TODO: Unzip the initial zipped folder.

#     # Specify where your data lives.
#     base = 'D:\\data\\washington\\'
#     DATA_DIR = f'{base}\\CCRS PRR ({DATE})\\CCRS PRR ({DATE})\\'
#     STATS_DIR = f'{base}\\ccrs-stats\\'
#     curate_ccrs_lab_results(DATA_DIR, STATS_DIR)
#     curate_ccrs_inventory(DATA_DIR, STATS_DIR)
#     curate_ccrs_sales(DATA_DIR, STATS_DIR)
#     curate_ccrs_strains(DATA_DIR, STATS_DIR)
