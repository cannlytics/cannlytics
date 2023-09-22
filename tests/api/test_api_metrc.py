"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/26/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports:
import os

# External imports:
from dotenv import dotenv_values
import requests

# Internal imports:
from cannlytics.utils import (
    get_date_range,
    encode_pdf,
    get_timestamp,
)

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
BASE = 'https://cannlytics.com/api'

# Load your API key to pass in the authorization header as a bearer token.
config = dotenv_values('../../.env')
API_KEY = config['CANNLYTICS_API_KEY']

# Define the URL endpoint.
ENDPOINT = 'metrc'


# === Tests ===
if __name__ == '__main__':

    # Authentication a session.
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {API_KEY}'})

    # Define test namespaces.
    today = '2023-01-26'
    strain_name = 'Moonshine Haze'
    batch_name = 'Moonshine Haze Clone Batch'
    test_location = 'CAN API Test Location'
    test_item = 'Moonshine Haze Eighth'

    #-------------------------------------------------------------------
    # License management.
    #-------------------------------------------------------------------

    # [✓] Test adding a Metrc user API key.
    print('Adding a license...')
    url = f'{BASE}/metrc/admin/create-license'
    data = {
      'metrc_user_api_key': os.getenv('METRC_TEST_USER_API_KEY'),
      'license_number': '',
      'license_type': 'Processor',
      'org_id': 'test-processor',
      'state': 'ok',
    }
    response = session.post(url, json=data)
    assert response.json()['success']
    print('Added Metrc user API key.')

    # [✓] Delete a license.
    print('Deleting a license...')
    url = f'{BASE}/metrc/admin/delete-license'
    data = {
      'license_number': '',
      'org_id': 'test-processor',
      'deletion_reason': 'Test deletion.',
    }
    response = session.post(url, json=data)
    assert response.json()['success']
    print('Deleted Metrc user API key.')


    #-------------------------------------------------------------------
    # Facilities and employees
    #-------------------------------------------------------------------

    # [✓] Test facilities.
    response = session.get(f'{BASE}/metrc/facilities')
    assert response.status_code == 200
    facilities = response.json()['data']
    print('Found %i facilities' % len(facilities))

    # [✓] Test getting employees.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/employees', params=params)
    assert response.status_code == 200
    employees = response.json()['data']
    print('Found %i employees' % len(employees))


    #-------------------------------------------------------------------
    # Locations
    #-------------------------------------------------------------------

    # [✓] Test getting locations.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations', params=params)
    assert response.status_code == 200
    locations = response.json()['data']
    print('Found %i locations' % len(locations))

    # [✓] Get location types.
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/types/locations', params=params)
    assert response.status_code == 200
    location_types = response.json()['data']
    print('Found %i location types' % len(location_types))

    # [✓] Test creating a location.
    data = {
        'name': 'CAN API Test Flower Bed',
        'location_type': location_types[0]['name']
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Created location.')

    # [✓] Test update the name of the location.
    uid = response.json()['data'][0]['uid']
    data = {
        'id': uid,
        'name': 'CAN Test Location',
        'location_type_name': location_types[0]['name']
    }
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Updated location.')

    # [✓] Test getting a specific location.
    uid = response.json()['data'][0]['uid']
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    location = response.json()['data']
    print('Found location.')

    # [✓] Test deleting a location.
    uid = response.json()['data'][0]['uid']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted location.')


    #-------------------------------------------------------------------
    # Strains
    #-------------------------------------------------------------------

    # [✓] Create a new strain.
    strain_name = 'Moonshine Haze'
    data = {
        'name': strain_name,
        'testing_status': 'None',
        'thc_level': 0.242,
        'cbd_level': 0.0333,
        'indica_percentage': 0.0,
        'sativa_percentage': 100.0
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/strains', json=data, params=params)
    assert response.status_code == 200
    print('Created strain.')

    # [✓] Get strains.
    response = session.get(f'{BASE}/metrc/strains', params=params)
    strains = response.json()['data']
    for strain in strains:
        if strain['name'] == strain_name:
            new_strain = strain
            break

    # [✓] Update a strain.
    data = {
        'id': new_strain['id'],
        'name': strain_name,
        'testing_status': 'None',
        'thc_level': 0.242,
        'cbd_level': 0.0333,
        'indica_percentage': 25.0,
        'sativa_percentage': 75.0
    }
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/strains', json=data, params=params)
    assert response.status_code == 200
    print('Updated strain.')

    # [✓] Get a strain.
    uid = new_strain['id']
    response = session.get(f'{BASE}/metrc/strains/{uid}', params=params)
    assert response.status_code == 200
    print('Retrieved strain.', response.json()['data'])

    # [✓] Delete a strain.
    uid = new_strain['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/strains/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted strain.')


    #-------------------------------------------------------------------
    # Items
    #-------------------------------------------------------------------

    # [✓] Get item categories.
    response = session.get(f'{BASE}/metrc/types/categories', params=params)
    assert response.status_code == 200
    categories = response.json()['data']
    print('Found %i categories.' % len(categories))

    # [✓] Create an item.
    item_name = 'Moonshine Haze Eighth'
    data = {
        'item_category': categories[7]['name'],
        'name': item_name,
        'unit_of_measure': 'Ounces',
        'strain': strain_name,
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=data, params=params)
    assert response.status_code == 200
    print('Created item.')

    # [✓] Create multiple items.
    data = [
        {
            'item_category': categories[7]['name'],
            'name': 'Moonshine Haze Shake',
            'unit_of_measure': 'Ounces',
            'strain': strain_name,
        },
        {
            'item_category': categories[7]['name'],
            'name': 'Moonshine Haze Gram Jar',
            'unit_of_measure': 'Grams',
            'strain': strain_name,
        },
        {
            'item_category': categories[7]['name'],
            'name': 'Moonshine Haze Sniffer Jar',
            'unit_of_measure': 'Grams',
            'strain': strain_name,
        },
        {
            'item_category': 'Immature Plants',
            'name': 'Moonshine Haze Clone',
            'unit_of_measure': 'Each',
            'strain': strain_name,
        }
    ]
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=data, params=params)
    assert response.status_code == 200
    print('Created items.')

    # [✓] Query items.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/items', params=params)
    assert response.status_code == 200
    items = response.json()['data']
    for item in items:
        if 'Moonshine' in item['name']:
            print(item['id'], item['name'])
            break

    # [✓] Get an item.
    uid = item['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/items/{uid}', params=params)
    assert response.status_code == 200

    # [✓] Update an item.
    update = item.copy()
    update['unit_of_measure'] = 'Grams'
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=update, params=params)
    assert response.status_code == 200
    print('Updated item.')

    # [✓] Delete an item.
    uid = item['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/items/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted item.')


    #-------------------------------------------------------------------
    # Batches
    #-------------------------------------------------------------------

    # [✓] Get batch types.
    response = session.get(f'{BASE}/metrc/types/batches', params=params)
    assert response.status_code == 200
    batch_types = response.json()['data']
    print('Found %i batch types' % len(batch_types))

    # [✓] Get waste methods.
    response = session.get(f'{BASE}/metrc/types/waste-methods', params=params)
    assert response.status_code == 200
    waste_methods = response.json()['data']
    print('Found %i waste methods' % len(waste_methods))

    # [✓] Get waste reasons.
    response = session.get(f'{BASE}/metrc/types/waste-reasons', params=params)
    assert response.status_code == 200
    waste_reasons = response.json()['data']
    print('Found %i waste reasons' % len(waste_reasons))

    # [✓] Get waste types.
    response = session.get(f'{BASE}/metrc/types/waste', params=params)
    assert response.status_code == 200
    waste_types = response.json()['data']
    print('Found %i waste types' % len(waste_types))

    # [✓] Create a new plant batch.
    batch_name = 'Moonshine Haze Clone Batch'
    data = {
        'name': batch_name,
        'type': 'Clone',
        'count': 77,
        'strain': strain_name,
        'location': test_location,
        'actual_date': today,
        'patient_license_number': '',
        'source_plant_batches': None,
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Created batch.')

    # [✓] Get plant batches by date.
    params = {
        'license': facilities[5]['license']['number'],
        'start': '2023-01-24',
        'end': '2023-01-25',
    }
    response = session.get(f'{BASE}/metrc/batches', params=params)
    assert response.status_code == 200
    batches = response.json()['data']
    print('Found %i batches.' % len(batches))

    # [✓] Get a plant batch.
    uid = response.json()['data'][0]['id']
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/batches/{uid}', params=params)
    assert response.status_code == 200

    # [✓] Create a package from a batch.
    uid = response.json()['data'][0]['id']
    data = {
        'id': uid,
        'plant_batch': None, # Specify `plant_batch` if `id` is None.
        'count': 3,
        'location': test_location,
        'item': 'Moonshine Haze Clone',
        'tag': 'redacted',
        'patient_license_number': None,
        'note': 'A package containing 3 plucky clones.',
        'is_trade_sample': False,
        'is_donation': False,
        'actual_date': '2023-01-24'
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'create-plant-package',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Created a package of clones from a plant batch.')

    # [✓] Flower 2 plants in a batch.
    data = {
        'name': batch_name,
        'count': 2,
        'starting_tag': '1A4FF0000000002000000123',
        'growth_phase': 'Flowering',
        'new_location': test_location,
        'growth_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'flower',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Flowered plant batch.')

    # [✓] Destroy plants in a batch.
    data = {
        'plant_batch': batch_name,
        'count': 1,
        'reason_note': 'Male plant!',
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'destroy-plants',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Destroyed a plant in a batch.')

    # [✓] Get units of measure.
    response = session.get(f'{BASE}/metrc/types/units', params=params)
    assert response.status_code == 200
    units = response.json()['data']
    print('Found %i units' % len(units))

    # [✓] Get types of additives.
    response = session.get(f'{BASE}/metrc/types/additives', params=params)
    assert response.status_code == 200
    additives = response.json()['data']
    print('Found %i additives' % len(additives))

    # [✓] Add additives.
    data = {
        'additive_type': additives[0],
        'product_trade_name': 'Great White Bat Guano',
        'epa_registration_number': None,
        'product_supplier': 'Ace',
        'application_device': 'Scoop',
        'total_amount_applied': 4.20,
        'total_amount_unit_of_measure': units[2]['name'],
        'plant_batch_name': batch_name,
        'actual_date': today,
        'active_ingredients': [
            {'Name': 'Phosphorous', 'Percentage': 7.0},
            {'Name': 'Nitrogen', 'Percentage': 7.0},
            {'Name': 'Potassium', 'Percentage': 7.0},
        ],
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'add-additives',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Added additives to a batch.')

    # [✓] Move batch.
    data = {
        'name': batch_name,
        'location': 'CAN API Test Flower Bed',
        'move_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'move',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Moved batch.')

    # [✓] Split batch.
    data = {
        'plant_batch': batch_name,
        'group_name': batch_name + ' #2',
        'count': 1,
        'location': 'CAN API Test Flower Bed',
        'strain': strain_name,
        'patient_license_number': None,
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'split',
    }
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Split batch.')


    #-------------------------------------------------------------------
    # Plants
    #-------------------------------------------------------------------

    # [✓] Create a plant.
    data = {
        'plant_label': '1A4FF0000000002000000150',
        'plant_batch_name': batch_name + ' #2',
        'plant_batch_type': 'Clone',
        'plant_count': 1,
        'location_name': test_location,
        'strain_name': strain_name,
        'patient_license_number': None,
        'actual_date': today,
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Created plant.')

    # [✓] Get plants created on a specific day.
    params = {
        'license': facilities[5]['license']['number'],
        'start': '2023-01-23',
        'end': '2023-01-24',
    }
    response = session.get(f'{BASE}/metrc/plants', params=params)
    assert response.status_code == 200
    plants = response.json()['data']
    print('Found %i plants.' % len(plants))

    # [✓] Get growth phases.
    response = session.get(f'{BASE}/metrc/types/growth-phases', params=params)
    assert response.status_code == 200
    growth_phases = response.json()['data']
    print('Found %i growth phases' % len(growth_phases))

    # [✓] Change the growth phase of a plant from `Vegetative` to `Flowering`.
    data = {
        'id': None,
        'label': plants[0]['label'],
        'new_tag': '1A4FF0000000002000000150',
        'growth_phase': 'Flowering',
        'new_location': test_location,
        'growth_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'flower',
    }
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Flowered plant.')

    # [✓] Get flowering plants.
    params = {
        'license': facilities[5]['license']['number'],
        'type': 'flowering',
        'start': '2023-01-24',
        'end': '2023-01-25',
    }
    response = session.get(f'{BASE}/metrc/plants', params=params)
    assert response.status_code == 200
    plants = response.json()['data']
    print('Found %i plants.' % len(plants))

    # [✓] Move a plant to a different room.
    data = {
        'id': None,
        'label': plants[-1]['label'],
        'location': 'CAN API Test Flower Bed',
        'actual_date': today
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'move',
    }
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Moved plant.')

    # [✓] Add additives to a plant.
    data = {
        'additive_type': additives[0],
        'product_trade_name': 'Great White Bat Guano',
        'epa_registration_number': None,
        'product_supplier': 'Ace',
        'application_device': 'Scoop',
        'total_amount_applied': 4.20,
        'total_amount_unit_of_measure': units[2]['name'],
        'plant_labels': [plants[-1]['label']],
        'actual_date': today,
        'active_ingredients': [
            {'Name': 'Phosphorous', 'Percentage': 7.0},
            {'Name': 'Nitrogen', 'Percentage': 7.0},
            {'Name': 'Potassium', 'Percentage': 7.0}
        ],
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'add-additives',
    }
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Added additives to a plant.')

    # [✓] Manicure a plant.
    data = {
        'plant': plants[-1]['label'],
        'weight': 1.23,
        'unit_of_weight': 'Grams',
        'drying_location': 'CAN API Test Flower Bed',
        'harvest_name': None,
        'patient_license_number': None,
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'manicure',
    }
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Manicured plant.')

    # [✓] Harvest from a plant.
    data = {
        'plant': plants[-1]['label'],
        'weight': 1.23,
        'unit_of_weight': 'Grams',
        'drying_location': test_location,
        'harvest_name': plants[-1]['strain_name'] + f' Harvest {today}',
        'patient_license_number': None,
        'actual_date': today
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'harvest',
    }
    response = session.post(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Harvested from a plant.')

    # [✓] Destroy a plant.
    uid = plants[-2]['id']
    response = session.delete(f'{BASE}/metrc/plants', json=data, params=params)
    assert response.status_code == 200
    print('Destroyed plant.')


    #-------------------------------------------------------------------
    # Harvests
    #-------------------------------------------------------------------

    # [✓] Get harvests created on a specific day.
    params = {
        'license': facilities[5]['license']['number'],
        'start': '2023-01-24',
        'end': '2023-01-25',
    }
    response = session.get(f'{BASE}/metrc/harvests', params=params)
    assert response.status_code == 200
    harvests = response.json()['data']
    print('Found %i harvests.' % len(harvests))

    # [✓] Create a package.
    harvest_id = harvests[0]['id']
    data = {
        'tag': '1A4FF0100000002000000088',
        'location': test_location,
        'item': 'Moonshine Haze Shake',
        'unit_of_weight': 'Grams',
        'patient_license_number': None,
        'note': 'Golden nug in this package.',
        'is_production_batch': False,
        'production_batch_number': None,
        'is_trade_sample': False,
        'is_donation': False,
        'product_requires_remediation': False,
        'remediate_product': False,
        'remediation_method_id': None,
        'remediation_date': None,
        'remediation_steps': None,
        'actual_date': today,
        'ingredients': [
            {
                'harvest_id': harvest_id,
                'harvest_name': None,
                'weight': 1.0,
                'unit_of_weight': 'Grams'
            }
        ]
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'create-packages',
    }
    response = session.post(f'{BASE}/metrc/harvests', json=data, params=params)
    assert response.status_code == 200
    print('Created package from harvest.')

    # [✓] Create a testing package.
    data = {
        'tag': '1A4FF0100000002000000090',
        'location': test_location,
        'item': 'Moonshine Haze Shake',
        'unit_of_weight': 'Grams',
        'patient_license_number': None,
        'note': 'Golden nug in this package.',
        'is_production_batch': False,
        'production_batch_number': None,
        'is_trade_sample': False,
        'is_donation': False,
        'product_requires_remediation': False,
        'remediate_product': False,
        'remediation_method_id': None,
        'remediation_date': None,
        'remediation_steps': None,
        'actual_date': today,
        'ingredients': [
            {
                'harvest_id': harvest_id,
                'harvest_name': None,
                'weight': 0.1,
                'unit_of_weight': 'Grams'
            }
        ]
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'create-testing-packages',
    }
    response = session.post(f'{BASE}/metrc/harvests', json=data, params=params)
    assert response.status_code == 200
    print('Created testing package from harvest.')

    # [✓] Remove waste weight from a harvest.
    data = {
        'id': harvest_id,
        'waste_type': waste_types[0]['name'],
        'unit_of_weight': 'Grams',
        'waste_weight': 0.05,
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'remove-waste',
    }
    response = session.post(f'{BASE}/metrc/harvests', json=data, params=params)
    assert response.status_code == 200
    print('Removed waste from a harvest.')

    # [✓] Finish a harvest.
    data = {
        'id': harvest_id,
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'finish',
    }
    response = session.post(f'{BASE}/metrc/harvests', json=data, params=params)
    assert response.status_code == 200
    print('Finished a harvest.')

    # [✓] Unfinish a harvest.
    data = {
        'id': harvest_id
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'unfinish',
    }
    response = session.post(f'{BASE}/metrc/harvests', json=data, params=params)
    assert response.status_code == 200
    print('Unfinished a harvest.')


    #-------------------------------------------------------------------
    # Packages
    #-------------------------------------------------------------------

    # [✓] Get package types.
    response = session.get(f'{BASE}/metrc/types/packages', params=params)
    assert response.status_code == 200
    package_types = response.json()['data']
    print('Found %i package types' % len(package_types))

    # [✓] Get package statuses.
    response = session.get(f'{BASE}/metrc/types/package-statuses', params=params)
    assert response.status_code == 200
    package_statuses = response.json()['data']
    print('Found %i package statuses' % len(package_statuses))

    # [✓] Get adjustment reasons.
    response = session.get(f'{BASE}/metrc/types/adjustments', params=params)
    assert response.status_code == 200
    adjustment_reasons = response.json()['data']
    print('Found %i adjustment reasons' % len(adjustment_reasons))

    # [✓] Get packages by date.
    params = {
        'license': facilities[5]['license']['number'],
        'start': '2023-01-24',
        'end': '2023-01-25',
    }
    response = session.get(f'{BASE}/metrc/packages', params=params)
    assert response.status_code == 200
    packages = response.json()['data']
    print('Found %i packages.' % len(packages))

    # [✓] Create a package from another package.
    data = {
        'tag': '1A4FF0100000002000000112',
        'location': test_location,
        'item': 'Moonshine Haze Shake',
        'quantity': 0.1,
        'unit_of_measure': 'Grams',
        'patient_license_number': None,
        'note': 'This is a tiny sample.',
        'is_production_batch': False,
        'production_batch_number': None,
        'is_donation': False,
        'product_requires_remediation': False,
        'use_same_item': True,
        'actual_date': today,
        'ingredients': [
            {
                'package': packages[0]['label'],
                'quantity': 0.1,
                'unit_of_measure': 'Grams'
            }
        ]
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Created a package from another package.')

    # [✓] Change the item of a package.
    data = {
        'label': packages[1]['label'],
        'item': 'Moonshine Haze Sniffer Jar'
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'change-package-items',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Changed an item in a package.')

    # [✓] Change the location of a package.
    data = {
        'label': packages[0]['label'],
        'location': 'CAN API Test Flower Bed',
        'move_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'move',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Changed the location of a package.')

    # [✓] Create a plant batch from a package.
    data = {
        'package_label': packages[-1]['label'],
        'package_adjustment_amount': 1.0,
        'package_adjustment_unit_of_measure_name': 'Ounces',
        'plant_batch_name': batch_name + ' #4',
        'plant_batch_type': 'Clone',
        'plant_count': 1,
        'location_name': test_location,
        'strain_name': strain_name,
        'patient_license_number': None,
        'planted_date': today,
        'unpackaged_date': today
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'create-plant-batches',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Created a plant batch from a package.')

    # [✓] Get a package using it's label.
    label = packages[0]['label']
    response = session.get(f'{BASE}/metrc/packages/{label}', params=params)
    assert response.status_code == 200
    package = response.json()['data']
    print('Found package:', package['label'])

    # [✓] Adjust the weight of a package.
    data = {
        'label': package['label'],
        'quantity': -0.9,
        'unit_of_measure': 'Grams',
        'adjustment_reason': adjustment_reasons[-1]['name'],
        'adjustment_date': today,
        'reason_note': 'The scales needed calibration.',
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'adjust',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Adjusted the weight of a package.')

    # [✓] Finish a package.
    data = {
        'label': package['label'],
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'finish',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Finished a package.')

    # [✓] Unfinish a package.
    data = {'label': package['label']}
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'unfinish',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Unfinished a package.')

    # [ ] Remediate a package.
    # TODO: This requires that the package has failed lab testing.
    data = {
        'package_label': packages[0]['label'],
        'remediation_method_name': 'Further Drying',
        'remediation_date': today,
        'remediation_steps': 'Used hair dryer'
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'remediate',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Remediated a package.')

    # [✓] Update the note for a package.
    data = {
        'package_label': packages[0]['label'],
        'note': 'Scale calibration is correct.'
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'update-package-notes',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Updated notes for a package.')


    #-------------------------------------------------------------------
    # Transfers and transfer templates
    #-------------------------------------------------------------------

    # [✓] Get transfer types.
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/types/transfers', params=params)
    assert response.status_code == 200
    transfer_types = response.json()['data']
    print('Found %i transfer types' % len(transfer_types))

    # [✓] Get a licensed courier.
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/employees', params=params)
    assert response.status_code == 200
    employees = response.json()['data']
    print('Found %i employees.' % len(employees))
    courier = employees[0]

    # [✓] Create a testing package.
    data = {
        'tag': '1A4FF0100000002000000113',
        'location': test_location,
        'item': 'Moonshine Haze Shake',
        'quantity': 0.025,
        'unit_of_measure': 'Grams',
        'note': 'Quality assurance test sample.',
        'actual_date': today,
        'ingredients': [
            {
                'package': packages[1]['label'],
                'quantity': 0.05,
                'unit_of_measure': 'Grams',
            }
        ]
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'create-testing-package',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Created a testing package.')

    # [✓] Get the tested package.
    label = '1A4FF0100000002000000113'
    response = session.get(f'{BASE}/metrc/packages/{label}', params=params)
    assert response.status_code == 200
    testing_package = response.json()['data']
    print('Found testing package:', testing_package['label'])

    # [✓] Set up an external transfer.
    lab = facilities[15]
    cultivator = facilities[5]
    courier = employees[0]
    retailer = facilities[0]
    transfer_data = {
        'shipper_license_number': cultivator['license']['number'],
        'shipper_name': cultivator['name'],
        'shipper_main_phone_number': '18005555555',
        'shipper_address1': 'Mulberry Street',
        'shipper_address2': None,
        'shipper_address_city': 'Oklahoma City',
        'shipper_address_state': 'OK',
        'shipper_address_postal_code': '123',
        'transporter_facility_license_number': retailer['license']['number'],
        'driver_occupational_license_number': courier['license']['number'],
        'driver_name': courier['full_name'],
        'driver_license_number': 'xyz',
        'phone_number_for_questions': '18005555555',
        'vehicle_make': 'xyz',
        'vehicle_model': 'xyz',
        'vehicle_license_plate_number': 'xyz',
        'destinations': [
            {
                'recipient_license_number': retailer['license']['number'],
                'transfer_type_name': 'Beginning Inventory Transfer',
                'planned_route': 'Hyper-tube.',
                'estimated_departure_date_time': get_timestamp(),
                'estimated_arrival_date_time': get_timestamp(future=60 * 24),
                'gross_weight': 0.025,
                'gross_unit_of_weight_id': None,
                'transporters': [
                    {
                        'transporter_facility_license_number': retailer['license']['number'],
                        'driver_occupational_license_number': courier['license']['number'],
                        'driver_name': courier['full_name'],
                        'driver_license_number': 'xyz',
                        'phone_number_for_questions': '18005555555',
                        'vehicle_make': 'xyz',
                        'vehicle_model': 'xyz',
                        'vehicle_license_plate_number': 'xyz',
                        'is_layover': False,
                        'estimated_departure_date_time': get_timestamp(),
                        'estimated_arrival_date_time': get_timestamp(future=60 * 24),
                        'transporter_details': None,
                    }
                ],
                'packages': [
                    {
                        'package_label': packages[1]['label'],
                        'harvest_name': packages[1]['source_harvest_names'],
                        'item_name': packages[1]['item']['name'],
                        'quantity': 0.025,
                        'unit_of_measure_name': 'Grams',
                        'packaged_date': get_timestamp(),
                        'gross_weight': 0.025,
                        'gross_unit_of_weight_name': 'Grams',
                        'wholesale_price': None,
                        'source': packages[1]['source_harvest_names']
                    },
                ]
            }
        ]
    }
    data = transfer_data
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/transfers', json=data, params=params)
    assert response.status_code == 200
    print('Created an external transfer.')

    # [✓] Get external transfers.
    params = {
        'license': facilities[0]['license']['number'],
        'start': get_timestamp(past=30),
        'type': 'rejected',
    }
    response = session.get(f'{BASE}/metrc/transfers', params=params)
    assert response.status_code == 200
    transfers = response.json()['data']
    print('Found %i external transfers.' % len(transfers))

    # [✓] Update an external transfer.
    data = transfer_data
    data['transfer_id'] = transfers[0]['id']
    data['shipper_address1'] = 'North Mulberry Street'
    response = session.post(f'{BASE}/metrc/transfers', json=data, params=params)
    assert response.status_code == 200
    transfers = response.json()['data']
    print('Updated external transfer.')

    # [✓] Create a transfer template.
    cultivator_license_number = facilities[5]['license']['number']
    data = {
        'name': 'HyperLoop Template',
        'transporter_facility_license_number': cultivator['license']['number'],
        'driver_occupational_license_number': courier['license']['number'],
        'driver_name': courier['full_name'],
        'driver_license_number': None,
        'phone_number_for_questions': None,
        'vehicle_make': None,
        'vehicle_model': None,
        'vehicle_license_plate_number': None,
        'destinations': [
            {
                'recipient_license_number': lab['license']['number'],
                'transfer_type_name': 'Affiliated Transfer',
                'planned_route': 'Take hyperlink A to hyperlink Z.',
                'estimated_departure_date_time': get_timestamp(),
                'estimated_arrival_date_time': get_timestamp(future=60),
                'transporters': [
                    {
                        'transporter_facility_license_number': cultivator['license']['number'],
                        'driver_occupational_license_number': courier['license']['number'],
                        'driver_name': courier['full_name'],
                        'driver_license_number': 'dash',
                        'phone_number_for_questions': '18005555555',
                        'vehicle_make': 'X',
                        'vehicle_model': 'X',
                        'vehicle_license_plate_number': 'X',
                        'is_layover': False,
                        'estimated_departure_date_time': get_timestamp(),
                        'estimated_arrival_date_time': get_timestamp(future=60),
                        'transporter_details': None,
                    }
                ],
                # Optional: Add packages to the transfer template.
                # 'packages': [
                #     {
                #         'package_label': 'YOUR_PACKAGE_TAG',
                #         'wholesale_price': 13.33,
                #     },
                # ]
            }
        ]
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/transfers/templates', json=data, params=params)
    assert response.status_code == 200
    print('Created transfer template.')

    # [✓] Get transfer templates.
    params = {
        'license': facilities[5]['license']['number'],
        'start': get_timestamp(past=30),
    }
    response = session.get(f'{BASE}/metrc/transfers/templates', params=params)
    assert response.status_code == 200
    templates = response.json()['data']
    print('Found %i transfer templates.' % len(templates))

    # [✓] Update a transfer template.
    params = {'license': facilities[5]['license']['number']}
    data['transfer_template_id'] = templates[0]['id']
    data['name'] = 'Premier Hyper Loop Template'
    response = session.post(f'{BASE}/metrc/transfers/templates', json=data, params=params)
    assert response.status_code == 200
    print('Updated a transfer template.')

    # [✓] Delete a transfer template.
    uid = templates[0]['id']
    params = {'license': facilities[5]['license']['number']}
    response = session.delete(f'{BASE}/metrc/transfers/templates/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted a transfer template.')


    #-------------------------------------------------------------------
    # Lab results
    #-------------------------------------------------------------------

    # Define the lab.
    lab = facilities[15]

    # [✓] Get test statuses.
    response = session.get(f'{BASE}/metrc/types/test-statuses', params=params)
    assert response.status_code == 200
    test_statuses = response.json()['data']
    print('Found %i test statuses' % len(test_statuses))
    
    # [✓] Get test types.
    response = session.get(f'{BASE}/metrc/types/tests', params=params)
    assert response.status_code == 200
    test_types = response.json()['data']
    print('Found %i test types' % len(test_types))

    # [✓] Get units of measure.
    response = session.get(f'{BASE}/metrc/types/units', params=params)
    assert response.status_code == 200
    units = response.json()['data']
    print('Found %i units of measure' % len(units))

    # [✓] Get testing package at the lab.
    params = {'license': lab['license']['number'],}
    response = session.get(f'{BASE}/metrc/packages', params=params)
    assert response.status_code == 200
    testing_packages = response.json()['data']
    print('Found %i testing packages.' % len(testing_packages))

    # [✓] Create a lab result record.
    encoded_coa = encode_pdf('../assets/pdfs/example_coa.pdf')
    data = {
        'label': testing_packages[0]['label'],
        'result_date': get_timestamp(zone='ok'),
        # Optional: Upload encoded COA PDF.
        'lab_test_document': {
            'document_file_name': 'coa.pdf',
            'document_file_base64': encoded_coa.decode('utf-8'),
        },
        'results': [
            {
                'lab_test_type_name': 'CBD',
                'quantity': 23.33,
                'passed': True,
                'notes': ''
            },
            {
                'lab_test_type_name': 'THC',
                'quantity': 0.07,
                'passed': True,
                'notes': ''
            },
        ]
    }
    params = {'license': lab['license']['number'],}
    response = session.post(f'{BASE}/metrc/tests', json=data, params=params)
    assert response.status_code == 200
    print('Created a lab result record.')

    # [✓] Fail a sample.
    analytes = []
    sample_type = 'Raw Plant Material'
    units = ['%', 'ppm', 'CFU/g', 'Aw']
    for unit in units:
        analytes += [x['name'] for x in test_types \
            if f'({unit}) {sample_type}' in x['name']]
    data = {
        'label': testing_packages[0]['label'],
        'result_date': get_timestamp(zone='ok'),
        'results': [
            {
                'lab_test_type_name': 'Spiromesifen (ppm) Raw Plant Material',
                'quantity': 0.2,
                'passed': False,
                'notes': 'This sample just passed the limit.'
            }
        ]
    }
    for analyte in analytes:
        if not 'Spiromesifen' in analyte:
            data['results'].append(
                {
                'lab_test_type_name': analyte,
                'quantity': 0,
                'passed': False,
                'notes': 'Nothing to note here.'
            }
            )
            
    params = {'license': lab['license']['number'],}
    response = session.post(f'{BASE}/metrc/tests', json=data, params=params)
    assert response.status_code == 200
    print('Posted a failing lab result record.')

    # [✓] Get test records for a package.
    uid = testing_packages[0]['id']
    params = {'license': lab['license']['number'],}
    response = session.get(f'{BASE}/metrc/tests/{uid}', params=params)
    assert response.status_code == 200
    tests = response.json()['data']
    print('Found package tests.')

    # [ ] Release lab results.
    data = {
        'package_label': testing_packages[0]['label'],
    }
    params = {
        'license': cultivator['license']['number'],
        'action': 'release',
    }
    response = session.post(f'{BASE}/metrc/tests', json=data, params=params)
    assert response.status_code == 200
    print('Released lab results.')


    # [ ] Upload a COA.
    encoded_coa = encode_pdf('../assets/pdfs/example_coa.pdf')
    data = {
        'lab_test_result_id': tests['lab_test_result_id'],
        'document_file_name': 'coa.pdf',
        'document_file_base64': encoded_coa.decode('utf-8'),
    }
    params = {
        'license': facilities[0]['license']['number'],
        'action': 'coas',
    }
    response = session.post(f'{BASE}/metrc/tests', json=data, params=params)
    assert response.status_code == 200
    print('Uploaded COA.')


    # [ ] Get a COA by appending `id` to the URL.
    test_id = tests['lab_test_result_id']
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/tests/coas/{test_id}', params=params)
    assert response.status_code == 200
    print('Retrieved COA.')


    # [ ] Get a COA by passing `id` as a parameter.
    test_id = tests['lab_test_result_id']
    params = {
        'license': facilities[0]['license']['number'],
        'id': tests['lab_test_result_id'],
    }
    response = session.get(f'{BASE}/metrc/tests/coas', params=params)
    assert response.status_code == 200
    print('Retrieved COA.')


    #-------------------------------------------------------------------
    # Sales
    #-------------------------------------------------------------------

    # Define the retailer.
    retailer = facilities[0]

    # [✓] Get customer types.
    response = session.get(f'{BASE}/metrc/types/customers', params=params)
    assert response.status_code == 200
    customer_types = response.json()['data']
    print('Found %i customer types' % len(customer_types))

    # [✓] Get a retail package.
    for dates in get_date_range('2021-01-01', '2021-04-20'):
        params = {
            'license': facilities[0]['license']['number'],
            'start': dates[0],
            'end': dates[1],
        }
        response = session.get(f'{BASE}/metrc/packages', params=params)
        assert response.status_code == 200
        retail_packages = response.json()['data']
        print(dates[0], 'Found %i retail packages' % len(retail_packages))
        if len(retail_packages) > 0:
            break

    # [✓] Create a sales receipt for a package.
    data = {
        'sales_date_time': get_timestamp(),
        'sales_customer_type': 'Patient',
        'patient_license_number': '1',
        'patient_license_number': None,
        'caregiver_license_number': None,
        'identification_method': None,
        'patient_registration_location_id': None,
        'transactions': [
            {
                'package_label': retail_packages[0]['label'],
                'quantity': 1.75,
                'unit_of_measure': 'Grams',
                'total_amount': 25.0,
                'unit_thc_percent': None,
                'unit_thc_content': None,
                'unit_thc_content_unit_of_measure': None,
                'unit_weight': None,
                'unit_weight_unit_of_measure': None,
                'invoice_number': None,
                'price': None,
                'excise_tax': None,
                'city_tax': None,
                'county_tax': None,
                'municipal_tax': None,
                'discount_amount': None,
                'sub_total': None,
                'sales_tax': None,
            }
        ]
    }
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/sales', json=data, params=params)
    assert response.status_code == 200
    print('Created a sales receipt.')

    # [✓] Get sales by date.
    for date_range in get_date_range('2023-01-22', '2023-01-25'):
        start, end = date_range
        params = {
            'license': facilities[0]['license']['number'],
            'start': start,
            'end': end,
        }
        response = session.get(f'{BASE}/metrc/sales', params=params)
        assert response.status_code == 200
        sales = response.json()['data']
        print(start, 'Found %i sales.' % len(sales))
        if len(sales) > 0:
            break

    # [✓] Get a sale given its Id.
    uid = sales[0]['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/sales/{uid}', params=params)
    assert response.status_code == 200
    sales = response.json()['data']
    print('Found sale', sales[0]['id'])

    # [✓] Update a sales receipt.
    data['id'] = sales[0]['id']
    data['transactions'][0]['total_amount'] = 4.20
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/sales', json=data, params=params)
    assert response.status_code == 200
    print('Updated a sales receipt.')

    # [✓] Void a sales receipt.
    uid = sales[0]['id']
    params = {'license': retailer['license']['number']}
    response = session.delete(f'{BASE}/metrc/sales/{uid}', params=params)
    assert response.status_code == 200
    print('Voided a sale.')


    #-------------------------------------------------------------------
    # Transactions
    #-------------------------------------------------------------------

    # [ ] Get transactions (daily statistics).
    for facility in facilities:
        try:
            params = {
                'license': facility['license']['number'],
                'start': '2021-01-01',
                'end': '2021-01-30',
            }
            response = session.get(f'{BASE}/metrc/transactions', params=params)
            assert response.status_code == 200
            transactions = response.json()['data']
            print('Found %i transactions.' % len(transactions))
            break
        except:
            print('Failed to find transactions for', facility['license']['number'])

    # [✓] Get patient registration locations.
    response = session.get(f'{BASE}/metrc/patients/locations')
    assert response.status_code == 200
    registration_locations = response.json()['data']
    print('Found %i patient registration locations.' % len(registration_locations))

    # [ ] Add transactions on a particular day.
    data = {
        'package_label': retail_packages[0]['label'],
        'quantity': 1.0,
        'unit_of_measure': 'Ounces',
        'total_amount': 299.99,
        'unit_thc_percent': None,
        'unit_thc_content': None,
        'unit_thc_content_unit_of_measure': None,
        'unit_weight': None,
        'unit_weight_unit_of_measure': None,
        'invoice_number': None,
        'price': None,
        'excise_tax': None,
        'city_tax': None,
        'county_tax': None,
        'municipal_tax': None,
        'discount_amount': None,
        'sub_total': None,
        'sales_tax': None,
    }
    params = {
        'license': facilities[0]['license']['number'],
        'date': '2023-01-26'
    }
    response = session.post(f'{BASE}/metrc/transactions', json=data, params=params)
    assert response.status_code == 200
    print('Created a transaction.')

    # [ ] Update transactions on a particular day.
    data = {
        'package_label': retail_packages[0]['label'],
        'quantity': 1.0,
        'unit_of_measure': 'Ounces',
        'total_amount': 249.99,
        'unit_thc_percent': None,
        'unit_thc_content': None,
        'unit_thc_content_unit_of_measure': None,
        'unit_weight': None,
        'unit_weight_unit_of_measure': None,
        'invoice_number': None,
        'price': None,
        'excise_tax': None,
        'city_tax': None,
        'county_tax': None,
        'municipal_tax': None,
        'discount_amount': None,
        'sub_total': None,
        'sales_tax': None,
    }
    params = {
        'license': facilities[0]['license']['number'],
        'date': '2023-01-26',
        'action': 'update',
    }
    response = session.post(f'{BASE}/metrc/transactions', json=data, params=params)
    assert response.status_code == 200
    print('Updated a transaction.')


    #-------------------------------------------------------------------
    # Patients
    #-------------------------------------------------------------------

    # [ ] Get active patients.
    for facility in facilities:
        try:
            params = {
                'license': facility['license']['number']
            }
            response = session.get(f'{BASE}/metrc/patients', params=params)
            assert response.status_code == 200
            patients = response.json()['data']
            print('Found %i patients.' % patients)
        except:
            print('Failed to find patients:', facility['license']['number'])

    # [ ] Get a patient using the patient's ID.
    uid = '000001'
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/patients/{uid}', params=params)
    assert response.status_code == 200
    print('Found patient.')

    # [ ] Add a patient.
    data = {
        'license_number': '000001',
        'license_effective_start_date': '2023-01-26',
        'license_effective_end_date': '2024-01-27',
        'recommended_plants': 6,
        'recommended_smokable_quantity': 1.0,
        'flower_ounces_allowed': None,
        'thc_ounces_allowed': None,
        'concentrate_ounces_allowed': None,
        'infused_ounces_allowed': None,
        'max_flower_thc_percent_allowed': None,
        'max_concentrate_thc_percent_allowed': None,
        'has_sales_limit_exemption': False,
        'actual_date': '2023-01-26'
    }
    params = {'license': facility['license']['number']}
    response = session.post(f'{BASE}/metrc/patients', json=data, params=params)
    assert response.status_code == 200
    print('Added a patient.')

    # [ ] Update a patient.
    data = {
        'license_number': '000001',
        'new_license_number': None,
        'license_effective_start_date': '2015-06-21',
        'license_effective_end_date': '2016-06-15',
        'recommended_plants': 7,
        'recommended_smokable_quantity': 2.0,
        'flower_ounces_allowed': None,
        'thc_ounces_allowed': None,
        'concentrate_ounces_allowed': None,
        'infused_ounces_allowed': None,
        'max_flower_thc_percent_allowed': None,
        'max_concentrate_thc_percent_allowed': None,
        'has_sales_limit_exemption': False,
        'actual_date': '2015-12-15'
    }
    params = {'license': facility['license']['number']}
    response = session.post(f'{BASE}/metrc/patients', json=data, params=params)
    assert response.status_code == 200
    print('Updated a patient.')

    # [ ] Delete a patient.
    uid = response.json()['data'][0]['uid']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/patients/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted a patient.')


    #-------------------------------------------------------------------
    # Deliveries
    #-------------------------------------------------------------------

    # [ ] Get return reasons.
    params = {'license': facilities[0]['license']['number'],}
    response = session.get(f'{BASE}/metrc/types/return-reasons', params=params)
    assert response.status_code == 200
    return_reasons = response.json()['data']
    print('Found %i return reasons.' % len(return_reasons))

    # [ ] Create a delivery.
    data = {
        'sales_date_time': '2017-04-04T10:10:19.000',
        'sales_customer_type': 'Consumer',
        'patient_license_number': None,
        'consumer_id': None,
        'driver_employee_id': '1',
        'driver_name': 'John Doe',
        'drivers_license_number': '1',
        'phone_number_for_questions': '+1-123-456-7890',
        'vehicle_make': 'Car',
        'vehicle_model': 'Small',
        'vehicle_license_plate_number': '000000',
        'recipient_name': None,
        'recipient_address_street1': '1 Someplace Road',
        'recipient_address_street2': 'Ste 9',
        'recipient_address_city': 'Denver',
        'recipient_address_county': None,
        'recipient_address_state': 'CO',
        'recipient_address_postal_code': '11111',
        'planned_route': 'Drive to destination.',
        'estimated_departure_date_time': '2017-04-04T11:00:00.000',
        'estimated_arrival_date_time': '2017-04-04T13:00:00.000',
        'transactions': [
            {
                'package_label': 'ABCDEF012345670000000001',
                'quantity': 1.0,
                'unit_of_measure': 'Ounces',
                'total_amount': 9.99,
                'unit_thc_percent': None,
                'unit_thc_content': None,
                'unit_thc_content_unit_of_measure': None,
                'unit_weight': None,
                'unit_weight_unit_of_measure': None,
                'invoice_number': None,
                'price': None,
                'excise_tax': None,
                'city_tax': None,
                'county_tax': None,
                'municipal_tax': None,
                'discount_amount': None,
                'sub_total': None,
                'sales_tax': None
            }
        ]
    }
    params = {'license': facility['license']['number']}
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Created a delivery.')

    # [ ] Get deliveries.
    params = {
        'license': facilities[0]['license']['number'],
        'start': '2023-01-26',
        'end': '2023-01-27',
        'salesStart': '2023-01-26',
        'salesEnd': '2023-01-27',
        'type': 'active',
    }
    response = session.get(f'{BASE}/metrc/deliveries', params=params)
    assert response.status_code == 200
    print('Found deliveries.')

    # [ ] Get a delivery using its ID.
    uid = '1'
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/deliveries/{uid}', params=params)
    assert response.status_code == 200
    print('Found delivery.')

    # [ ] Update a delivery.
    data['id'] = '1'
    params = {'license': facility['license']['number']}
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Updated a delivery.')

    # [ ] Delete a delivery.
    uid = '1'
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/deliveries/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted a delivery.')

    # [ ] Complete a delivery.
    data = {
        'id': 6,
        'actual_arrival_date_time': '2017-04-04T13:00:00.000',
        'accepted_packages': ['ABCDEF012345670000000001'],
        'returned_packages': [
            {
                'label': 'ABCDEF012345670000000002',
                'return_quantity_verified': 1.0,
                'return_unit_of_measure': 'Ounces',
                'return_reason': 'Spoilage',
                'return_reason_note': ''
            }
        ]
    }
    params = {
        'license': facility['license']['number'],
        'action': 'complete',
    }
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Completed a delivery.')

    # [ ] Depart a delivery.
    data = {
        'retailer_delivery_id': 6
    }
    params = {
        'license': facility['license']['number'],
        'action': 'depart',
    }
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Departed a delivery.')

    # [ ] Restock a delivery.
    data = {
        'retailer_delivery_id': 6,
        'date_time': '2017-04-04T10:10:19.000',
        'estimated_departure_date_time': '2017-04-04T11:00:00.000',
        'destinations': None,
        'packages': [
            {
                'package_label': 'ABCDEF012345670000000001',
                'quantity': 1.0,
                'unit_of_measure': 'Ounces',
                'total_price': 9.99,
                'remove_current_package': False
            }
        ]
    }
    params = {
        'license': facility['license']['number'],
        'action': 'restock',
    }
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Restocked a delivery.')

    # [ ] Deliver a delivery.
    data = {
        'retailer_delivery_id': 1,
        'sales_date_time': '2017-04-04T10:10:19.000',
        'sales_customer_type': 'Consumer',
        'patient_license_number': None,
        'consumer_id': None,
        'driver_employee_id': '1',
        'driver_name': 'John Doe',
        'drivers_license_number': '1',
        'phone_number_for_questions': '+1-123-456-7890',
        'vehicle_make': 'Car',
        'vehicle_model': 'Small',
        'vehicle_license_plate_number': '000000',
        'recipient_name': None,
        'recipient_address_street1': '1 Someplace Road',
        'recipient_address_street2': 'Ste 9',
        'recipient_address_city': 'Denver',
        'recipient_address_county': None,
        'recipient_address_state': 'CO',
        'recipient_address_postal_code': '11111',
        'planned_route': 'Drive to destination.',
        'estimated_departure_date_time': '2017-04-04T11:00:00.000',
        'estimated_arrival_date_time': '2017-04-04T13:00:00.000',
        'transactions': [
            {
                'package_label': 'ABCDEF012345670000000001',
                'quantity': 1.0,
                'unit_of_measure': 'Ounces',
                'total_amount': 9.99,
                'unit_thc_percent': None,
                'unit_thc_content': None,
                'unit_thc_content_unit_of_measure': None,
                'unit_weight': None,
                'unit_weight_unit_of_measure': None,
                'invoice_number': None,
                'price': None,
                'excise_tax': None,
                'city_tax': None,
                'county_tax': None,
                'municipal_tax': None,
                'discount_amount': None,
                'sub_total': None,
                'sales_tax': None
            }
        ]
    }
    params = {
        'license': facility['license']['number'],
        'action': 'deliver',
    }
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Delivered a delivery.')

    # [ ] End a delivery.
    data = {
        'retailer_delivery_id': 6,
        'actual_arrival_date_time': '2017-04-04T13:00:00.000',
        'packages': [
            {
                'label': 'ABCDEF012345670000000002',
                'end_quantity': 1.0,
                'end_unit_of_measure': 'Ounces'
            }
        ]
    }
    params = {
        'license': facility['license']['number'],
        'action': 'end',
    }
    response = session.post(f'{BASE}/metrc/deliveries', json=data, params=params)
    assert response.status_code == 200
    print('Ended a delivery.')
