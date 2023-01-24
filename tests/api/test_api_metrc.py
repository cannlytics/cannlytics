"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/22/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import dotenv_values

# Define the endpoint.
ENDPOINT = 'metrc'

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
# BASE = 'https://console.cannlytics.com/api'

# Load your API key to pass in the authorization header as a bearer token.
config = dotenv_values('../../.env')
API_KEY = config['CANNLYTICS_API_KEY']


# === Tests ===
if __name__ == '__main__':

    # Authentication a session.
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {API_KEY}'})

    # Define test namespaces.
    today = '2023-01-24'
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

    # [✓] Adjust the weight of a package.
    data = {
        'label': packages[0]['label'],
        'quantity': -0.05,
        'unit_of_measure': 'Each',
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

    # TODO: Adjust the weight of a package to 0.

    # [ ] Finish a package.
    data = {
        'label': packages[0]['label'],
        'actual_date': today,
    }
    params = {
        'license': facilities[5]['license']['number'],
        'action': 'finish',
    }
    response = session.post(f'{BASE}/metrc/packages', json=data, params=params)
    assert response.status_code == 200
    print('Finished a package.')

    # [ ] Unfinish a package.
    data = {'label': packages[0]['label']}
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

    # [ ] Create a testing package.
    data = {
        'tag': 'YOUR_TEST_PACKAGE_TAG',
        'location': 'CAN API Test Flower Bed',
        'item': 'Moonshine Haze Shake',
        'quantity': 0.05,
        'unit_of_measure': 'Grams',
        'note': 'Quality assurance test sample.',
        'actual_date': '2023-01-21',
        'ingredients': [
            {
                'package': 'redacted',
                'quantity': 0.05,
                'unit_of_measure': 'Grams',
            }
        ]
    }

    # [ ] Get the tested package.


    # [ ] Set up an external transfer.
    transfer_data = {
        'shipper_license_number': 'cultivator.license_number',
        'shipper_name': 'cultivator.name',
        'shipper_main_phone_number': '18005555555',
        'shipper_address1': 'Mulberry Street',
        'shipper_address2': None,
        'shipper_address_city': 'Oklahoma City',
        'shipper_address_state': 'OK',
        'shipper_address_postal_code': '123',
        'transporter_facility_license_number': "lab.license['number']",
        'driver_occupational_license_number': "grower.license['number']",
        'driver_name': 'grower.full_name',
        'driver_license_number': 'xyz',
        'phone_number_for_questions': '18005555555',
        'vehicle_make': 'xyz',
        'vehicle_model': 'xyz',
        'vehicle_license_plate_number': 'xyz',
        'destinations': [
            {
                'recipient_license_number': 'lab.license_number',
                'transfer_type_name': 'Lab Sample Transfer',
                'planned_route': 'Hyper-tube.',
                'estimated_departure_date_time': 'get_timestamp()',
                'estimated_arrival_date_time': 'get_timestamp(future=60 * 24)',
                'gross_weight': 4,
                'gross_unit_of_weight_id': None,
                'transporters': [
                    {
                        'transporter_facility_license_number': 'lab.license_number',
                        'driver_occupational_license_number': "courier.license['number']",
                        'driver_name': 'courier.full_name',
                        'driver_license_number': 'xyz',
                        'phone_number_for_questions': '18005555555',
                        'vehicle_make': 'xyz',
                        'vehicle_model': 'xyz',
                        'vehicle_license_plate_number': 'xyz',
                        'is_layover': False,
                        'estimated_departure_date_time': 'get_timestamp()',
                        'estimated_arrival_date_time': 'get_timestamp(future=60 * 24)',
                        'transporter_details': None,
                    }
                ],
                'packages': [
                    {
                        'package_label': 'traced_package.label',
                        'harvest_name': '2nd New Old-Time Moonshine Harvest',
                        'item_name': 'New Old-Time Moonshine Teenth',
                        'quantity': 1,
                        'unit_of_measure_name': 'Each',
                        'packaged_date': 'get_timestamp()',
                        'gross_weight': 4.0,
                        'gross_unit_of_weight_name': 'Grams',
                        'wholesale_price': None,
                        'source': '2nd New Old-Time Moonshine Harvest'
                    },
                ]
            }
        ]
    }


    # [ ] Get external transfers.


    # [ ] Update an external transfer.


    # [ ] Create a transfer template.
    cultivator_license_number = facilities[5]['license']['number']
    template_data = {
        'name': 'HyperLoop Template',
        'transporter_facility_license_number': cultivator_license_number,
        'driver_occupational_license_number': courier['license']['number'],
        'driver_name': courier['full_name'],
        'driver_license_number': None,
        'phone_number_for_questions': None,
        'vehicle_make': None,
        'vehicle_model': None,
        'vehicle_license_plate_number': None,
        'destinations': [
            {
                'recipient_license_number': 'lab.license_number',
                'transfer_type_name': 'Affiliated Transfer',
                'planned_route': 'Take hyperlink A to hyperlink Z.',
                'estimated_departure_date_time': '2023-01-23T12:00',
                'estimated_arrival_date_time': '2023-01-23T13:00',
                'transporters': [
                    {
                        'transporter_facility_license_number': 'transporter.license_number',
                        'driver_occupational_license_number': "courier.license['number']",
                        'driver_name': 'courier.full_name',
                        'driver_license_number': 'dash',
                        'phone_number_for_questions': '18005555555',
                        'vehicle_make': 'X',
                        'vehicle_model': 'X',
                        'vehicle_license_plate_number': 'X',
                        'is_layover': False,
                        'estimated_departure_date_time': 'get_timestamp()',
                        'estimated_arrival_date_time': 'get_timestamp(future=360)',
                        'transporter_details': None,
                    }
                ],
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
    response = session.post(f'{BASE}/metrc/transfers/templates', params=params)
    assert response.status_code == 200
    print('Created transfer template.')

    # [✓] Get transfer templates.
    params = {
        'license': facilities[5]['license']['number'],
        'start': '2021-04-09',
        'end': '2021-04-10',
    }
    response = session.get(f'{BASE}/metrc/transfers/templates', params=params)
    assert response.status_code == 200
    templates = response.json()['data']
    print('Found %i transfer templates.' % len(templates))

    # [ ] Update a transfer template.
    data = {
        'transfer_template_id': templates[0]['id'],
        'name': 'Driverless Truck Template',
        'transporter_facility_license_number': None,
        'driver_occupational_license_number': None,
        'driver_name': None,
        'driver_license_number': None,
        'phone_number_for_questions': None,
        'vehicle_make': None,
        'vehicle_model': None,
        'vehicle_license_plate_number': None,
        'destinations': [
            {
                'transfer_destination_id': 0,
                'recipient_license_number': '123-XYZ',
                'transfer_type_name': 'Transfer',
                'planned_route': 'I will drive down the road to the place.',
                'estimated_departure_date_time': '2018-03-06T09:15:00.000',
                'estimated_arrival_date_time': '2018-03-06T12:24:00.000',
                'transporters': [
                    {
                        'transporter_facility_license_number': '123-ABC',
                        'driver_occupational_license_number': '50',
                        'driver_name': 'X',
                        'driver_license_number': '5',
                        'phone_number_for_questions': '18005555555',
                        'vehicle_make': 'X',
                        'vehicle_model': 'X',
                        'vehicle_license_plate_number': 'X',
                        'is_layover': False,
                        'estimated_departure_date_time': '2018-03-06T12:00:00.000',
                        'estimated_arrival_date_time': '2018-03-06T21:00:00.000',
                        'transporter_details': None
                    }
                ],
                # 'packages': [
                #     {
                #         'package_label': 'ABCDEF012345670000010026',
                #         'wholesale_price': None
                #     },
                # ],
            }
        ],
    }
    response = session.post(f'{BASE}/metrc/transfers/templates', json=data, params=params)
    assert response.status_code == 200
    print('Updated a transfer template.')

    # [ ] Delete a transfer template.


    #-------------------------------------------------------------------
    # Lab results
    #-------------------------------------------------------------------

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

    # [ ] Record a lab test result.


    # [ ] Create the lab result record.
    lab_result_data = {
        'Label': 'test_package_label',
        'ResultDate': 'get_timestamp()',
        'LabTestDocument': {
            'DocumentFileName': 'new-old-time-moonshine.pdf',
            'DocumentFileBase64': 'encoded_pdf',
        },
        'Results': [
            {
                'LabTestTypeName': 'THC',
                'Quantity': 0.07,
                'Passed': True,
                'Notes': ''
            },
            {
                'LabTestTypeName': 'CBD',
                'Quantity': 23.33,
                'Passed': True,
                'Notes': ''
            },
        ]
    }


    # [ ] Get a package's lab results.


    # [ ] Get lab results for multiple packages.


    # TODO: Fail a sample.


    #-------------------------------------------------------------------
    # Sales
    #-------------------------------------------------------------------

    # [✓] Get customer types.
    response = session.get(f'{BASE}/metrc/types/customers', params=params)
    assert response.status_code == 200
    customer_types = response.json()['data']
    print('Found %i customer types' % len(customer_types))

    # [ ] Create a sales receipt for a package.
    data = {
        'sales_date_time': 'get_timestamp()',
        'sales_customer_type': 'Patient',
        'patient_license_number': '1',
        'transactions': [
            {
                'package_label': 'retailer_package.label',
                'quantity': 1.75,
                'unit_of_measure': 'Grams',
                'total_amount': 25.0
            }
        ]
    }

    # [ ] Get sales by date.
    date_ranges = [
        ('2023-01-13', '2023-01-14'),
        ('2023-01-14', '2023-01-15'),
        ('2023-01-15', '2023-01-16'),
        ('2023-01-16', '2023-01-17'),
        ('2023-01-17', '2023-01-18'),
        ('2023-01-18', '2023-01-19'),
        ('2023-01-19', '2023-01-20'),
        ('2023-01-20', '2023-01-21'),
        ('2023-01-21', '2023-01-22'),
        ('2023-01-22', '2023-01-23'),
        ('2023-01-23', '2023-01-24')
    ]
    for date_range in date_ranges:
        start, end = date_range
        params = {
            'license': facilities[0]['license']['number'],
            'start': start,
            'end': end,
        }
        response = session.get(f'{BASE}/metrc/sales', params=params)
        assert response.status_code == 200
        sales = response.json()['data']
        print('Found %i sales on %s.' % (len(sales), start))
        if len(sales) > 0:
            break

    # [ ] Get a sale.
    for i in range(400, 420):
        uid = str(i)
        params = {'license': facilities[0]['license']['number']}
        response = session.get(f'{BASE}/metrc/sales/{uid}', params=params)
        assert response.status_code == 200
        print(response.json())
        if response.json()['data']:
            break


    # [ ] Update a sales receipt.


    # [ ] Void a sales receipt.


    #-------------------------------------------------------------------
    # Deliveries
    #-------------------------------------------------------------------

    # [ ] Get return reasons.
    # FIXME: This may only be valid in certain states.
    params = {'license': facilities[0]['license']['number'],}
    response = session.get(f'{BASE}/metrc/types/return-reasons', params=params)
    assert response.status_code == 200
    return_reasons = response.json()['data']
    print('Found %i return reasons.' % len(return_reasons))

    # [ ] Create a delivery.


    # [ ] Get deliveries.


    # [ ] Query deliveries.


    # [ ] Update a delivery.


    # [ ] Delete a delivery.


    # [ ] Complete a delivery.
