"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/20/2023
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


    #-------------------------------------------------------------------
    # [✓] License management.
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
    # [✓] Facilities and employees
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
    # [✓] Locations
    #-------------------------------------------------------------------

    # [✓] Test getting locations.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations', params=params)
    assert response.status_code == 200
    locations = response.json()['data']
    print('Found %i locations' % len(locations))

    # [✓] Get location types.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/types/locations', params=params)
    assert response.status_code == 200
    location_types = response.json()['data']
    print('Found %i location types' % len(location_types))

    # [✓] Test creating a location.
    data = {
        'name': 'CAN API Test Location',
        'location_type': location_types[0]['name']
    }
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Created location.')

    # [✓] Test update the name of the location.
    data = {
        'id': '61001',
        'name': 'CAN Test Location',
        'location_type_name': location_types[0]['name']
    }
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Updated location.')

    # [✓] Test getting a specific location.
    uid = '61001'
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    location = response.json()['data']
    print('Found location.')

    # [✓] Test deleting a location.
    uid = '61001'
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted location.')


    #-------------------------------------------------------------------
    # [✓] Strains
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
    params = {'license': facilities[0]['license']['number']}
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
    # TODO: [ ] Items
    #-------------------------------------------------------------------

    # [✓] Get item categories.
    response = session.get(f'{BASE}/metrc/types/categories', params=params)
    categories = response.json()['data']

    # [✓] Create an item.
    item_name = 'Moonshine Haze Eighth'
    data = {
        'item_category': categories[7]['name'],
        'name': item_name,
        'unit_of_measure': 'Ounces',
        'strain': strain_name,
    }
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=data, params=params)
    assert response.status_code == 200
    print('Created item.')

    # [ ] Create multiple items.


    # [ ] Query items.


    # [ ] Get an item.


    # [ ] Update an item.


    # [ ] Update items.


    # [ ] Delete an item.


    #-------------------------------------------------------------------
    # TODO: [ ] Batches
    #-------------------------------------------------------------------

    # [ ] Create a new plant batch.


    # [ ] Get a plant batch.


    # [ ] Create a package.


    # [ ] Update a batch.


    # [ ] Destroy a batch.


    # [ ] Get additives.


    # [ ] Manage waste.


    #-------------------------------------------------------------------
    # TODO: [ ] Plants
    #-------------------------------------------------------------------

    # [ ] Get a plant created in a plant batch.


    # [ ] Change the growth phase of a plant from `Vegetative` to `Flowering`.


    # [ ] Move a plant to a different room.


    # [ ] Destroy a plant.


    # [ ] Manicure a plant.


    # [ ] Harvest a plant.


    # [ ] Delete a harvest?


    #-------------------------------------------------------------------
    # TODO: [ ] Harvests
    #-------------------------------------------------------------------

    # [ ] Get a harvest.


    # [ ] Create a package.


    # [ ] Remove waste weight from a harvest.


    # [ ] Finish a harvest.


    # [ ] Unfinish the harvest.


    # [ ] Delete a harvest?


    #-------------------------------------------------------------------
    # TODO: [ ] Packages
    #-------------------------------------------------------------------

    # [ ] Get a package.


    # [ ] Create a package from another package.


    # [ ] Change the item of a package.


    # [ ] Adjust the weight of a package.


    # [ ] Finish a package.


    # [ ] Unfinish a package.


    # [ ] Delete a package?


    #-------------------------------------------------------------------
    # TODO: [ ] Transfers and transfer templates
    #-------------------------------------------------------------------

    # [ ] Get a licensed courier.


    # [ ] Create a testing package.


    # [ ] Get the tested package.


    # [ ] Set up an external transfer.


    # [ ] Get external transfers.


    # [ ] Update an external transfer.


    # [ ] Create a transfer template.


    # [ ] Get transfer templates.


    # [ ] Update a transfer template.


    # [ ] Delete a transfer template.


    #-------------------------------------------------------------------
    # TODO: [ ] Lab results
    #-------------------------------------------------------------------

    # [ ] Get test statuses.
    # [ ] Get test types.
    # [ ] Get units of measure.


    # [ ] Record a lab test result.


    # [ ] Create the lab result record.


    # [ ] Get a package's lab results.


    # [ ] Get lab results for multiple packages.



    #-------------------------------------------------------------------
    # TODO: [ ] Sales
    #-------------------------------------------------------------------

    # [ ] Get customer types.


    # [ ] Create a sales receipt for a package.


    # [ ] Get a sale.


    # [ ] Get sales.


    # [ ] Update a sales receipt.


    # [ ] Void a sales receipt.

