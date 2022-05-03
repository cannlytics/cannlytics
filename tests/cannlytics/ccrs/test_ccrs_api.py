"""
CCRS API Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/10/2022
Updated: 4/20/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: This script tests Washington State CCRS data management tools.

Data sources:

    - CCRS PRR All Data Up To 3-12-2022
    https://lcb.app.box.com/s/7pi3wqrmkuo3bh5186s5pqa6o5fv8gbs

Setup:

    1. pip install cannlytics

FIXME: Turn script into re-usable functions.

"""
# Standard imports.
import os

# External imports.
from dotenv import dotenv_values

# Internal imports.
from ccrs import CCRS

# Create a place for your data to live.
DATA_DIR = 'D://data/washington/CCRS PRR All Data Up To 3-12-2022'

# Initialize a CCRS client.
config = dotenv_values('../../.env')
os.environ['CANNLYTICS_API_KEY'] = config['CANNLYTICS_API_KEY']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE_APPLICATION_CREDENTIALS']
ccrs = CCRS(data_dir=DATA_DIR)


#------------------------------------------------------------------------------
# Upload CCRS data.
#------------------------------------------------------------------------------

# Upload licensee data.
licensees = ccrs.read_licensees()
# FIXME: Redact sensitive fields

# ccrs.upload(licensees, 'licensees', id_field='license_number')

# TODO: Upload summary statistics instead of raw data.

# # Read areas data.
# areas = ccrs.read_areas(limit=100)
# areas['area_id'] = areas.index
# ccrs.upload(areas, 'areas', id_field='area_id')

# # Read contacts data.
# contacts = ccrs.read_contacts()
# contacts['contact_id'] = contacts.index
# ccrs.upload(contacts, 'contacts', id_field='contact_id')

# # Read integrators data.
# integrators = ccrs.read_integrators()
# integrators['integrator_id'] = integrators.index
# ccrs.upload(integrators, 'integrators', id_field='integrator_id')

# # Read inventory data.
# inventory = ccrs.read_inventory(limit=100)
# inventory['inventory_id'] = inventory.index
# ccrs.upload(inventory, 'inventory', id_field='inventory_id')

# # Read inventory adjustment data.
# adjustments = ccrs.read_inventory_adjustments(limit=100)
# adjustments['inventory_adjustment_id'] = adjustments.index
# ccrs.upload(adjustments, 'inventory_adjustments', id_field='inventory_adjustment_id')

# # Read plant data.
# plants = ccrs.read_plants(limit=100)
# plants['plant_id'] = plants.index
# ccrs.upload(plants, 'plants', id_field='plant_id')

# # FIXME: Read strain data.
# strains = ccrs.read_strains(limit=100)
# strains['strain_id'] = strains.index
# ccrs.upload(strains, 'strains', id_field='strain_id')

# # Read plant destruction data.
# destructions = ccrs.read_plant_destructions(limit=100)
# destructions['plant_destruction_id'] = destructions.index
# ccrs.upload(destructions, 'plant_destructions', id_field='plant_destruction_id')

# # Read product data.
# products = ccrs.read_products(limit=100)
# products['product_id'] = products.index
# ccrs.upload(products, 'products', id_field='product_id')

# # Read sale header data.
# sale_headers = ccrs.read_sale_headers(limit=100)
# ccrs.upload(sale_headers, 'sale_headers', id_field='sale_header_id')

# # Read sale detail data.
# sale_details = ccrs.read_sale_details(limit=100)
# ccrs.upload(sale_details, 'sale_details', id_field='sale_detail_id')

# # FIXME: Read transfer data.
# # transfers = ccrs.read_transfers(limit=100)
# # transfers['transfer_id'] = transfers.index
# # ccrs.upload(transfers, 'transfers', id_field='transfer_id')

# # Read lab results.
# lab_results = ccrs.read_lab_results(limit=100)
# lab_results['lab_result_id'] = lab_results.index
# ccrs.upload(lab_results, 'lab_results', id_field='lab_result_id')


#------------------------------------------------------------------------------
# Test getting all data from the Cannlytics API!
#------------------------------------------------------------------------------

# # Define the base.
# base = 'http://127.0.0.1:8000/api'
# # base = 'https://cannlytics.com/api'

# # Get licensees.
# test_licensees = ccrs.get('licensees', limit=100, base=base)
# print(f'Accessed {len(test_licensees)} licensees.')

# # Get areas.
# test_areas = ccrs.get('areas', limit=100, base=base)
# print(f'Accessed {len(test_areas)} areas.')

# # Get contacts.
# test_contacts = ccrs.get('contacts', limit=100, base=base)
# print(f'Accessed {len(test_contacts)} contacts.')

# # Get integrators.
# test_integrators = ccrs.get('integrators', limit=100, base=base)
# print(f'Accessed {len(test_integrators)} integrators.')

# # Get inventory.
# test_inventory = ccrs.get('inventory', limit=100, base=base)
# print(f'Accessed {len(test_inventory)} inventory.')

# # Get inventory_adjustments.
# test_inventory_adjustments = ccrs.get('inventory_adjustments', limit=100, base=base)
# print(f'Accessed {len(test_inventory_adjustments)} inventory_adjustments.')

# # Get plants.
# test_plants = ccrs.get('plants', limit=100, base=base)
# print(f'Accessed {len(test_plants)} plants.')

# # Get plant_destructions.
# test_plant_destructions = ccrs.get('plant_destructions', limit=100, base=base)
# print(f'Accessed {len(test_plant_destructions)} plant_destructions.')

# # Get products.
# test_products = ccrs.get('products', limit=100, base=base)
# print(f'Accessed {len(test_products)} products.')

# # Get sale_headers.
# test_sale_headers = ccrs.get('sale_headers', limit=100, base=base)
# print(f'Accessed {len(test_sale_headers)} sale_headers.')

# # Get sale_details.
# test_sale_details = ccrs.get('sale_details', limit=100, base=base)
# print(f'Accessed {len(test_sale_details)} sale_details.')

# # Get strains.
# test_strains = ccrs.get('strains', limit=100, base=base)
# print(f'Accessed {len(test_strains)} strains.')

# # Get transfers.
# # test_transfers = ccrs.get('transfers', limit=100, base=base)
# # print(f'Accessed {len(test_transfers)} transfers.')

# # Get lab_results.
# test_lab_results = ccrs.get('lab_results', limit=100, base=base)
# print(f'Accessed {len(test_lab_results)} lab_results.')
